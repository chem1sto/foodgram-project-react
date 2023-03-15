import io

from django.conf import settings
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from api.permissions import (IsAdminPermission,
                             IsAdminOrAuthorOrReadOnlyPermission)
from api.serializers import (IngredientSerializer, RecipeCreateSerializer,
                             RecipeReadSerializer, RecipeShortReadSerializer,
                             SetPasswordSerializer, SignUpUserSerializer,
                             SubscriptionSerializer, TagSerializer,
                             UserProfileSerializer)
from api.utils import post, delete
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from users.models import CustomUser, Subscription


class CustomUserViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin
):
    """
    Вьюсет для реализации операций с моделью CustomUser:
    - получения списка всех пользователей;
    - создание нового пользователя;
    - получение детализации пользователя по его id.
    """
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        '''Выбо сериализатора в зависимости от запроса.'''
        if self.action in ('list', 'retrieve'):
            return UserProfileSerializer
        return SignUpUserSerializer

    def get_permissions(self):
        """
        Выбор уровня доступа для пользователя в зависимости от запроса.
        """
        if self.action == 'retrieve':
            self.permission_classes = (IsAdminOrAuthorOrReadOnlyPermission,)
        elif self.action == 'destroy':
            self.permission_classes = (IsAdminPermission,)
        return [permission() for permission in self.permission_classes]

    @action(
        url_path='me',
        detail=False,
        permission_classes=(AllowAny,)
    )
    def me(self, request):
        """Получение детализации текущего пользователя."""
        return Response(
            UserProfileSerializer(request.user).data, status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['post'],
        url_path='set_password',
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        """Изменение пароля текущего пользователя."""
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,)
    )
    def get_subscriptions(self, request):
        """Получение списка всех подписок пользователя"""
        subscriptions = CustomUser.objects.filter(
            subscribing__subscriber=request.user
        )
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionSerializer(
            instance=page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def create_or_delete_subscribing(self, request, pk):
        """Создание или удаление подписки на пользователя по его id."""
        subscriber = CustomUser.objects.get(pk=request.user.id)
        subscribing = get_object_or_404(CustomUser, pk=pk)
        if request.method == 'POST':
            if subscriber == subscribing:
                raise ValidationError(
                    {'errors': _('Вы уже подписаны на данного пользователя.')}
                )
            if Subscription.objects.filter(
                subscriber=subscriber,
                subscribing=subscribing
            ).exists():
                raise ValidationError(
                    {'errors': _('Вы уже подписаны на данного пользователя.')}
                )
            Subscription.objects.create(
                subscriber=subscriber,
                subscribing=subscribing,
            )
            serializer = SubscriptionSerializer(
                instance=subscribing,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(
            Subscription,
            subscriber=subscriber,
            subscribing=subscribing
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для реализации операций с моделью Ingredient:
    - получения списка всех ингредиентов;
    - получение детализации ингредиента по его id.
    — добавление нового ингредиента (для администратора);
    — обновление ингредиента (для администратора);
    — удаление ингредиента (для администратора).
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_permissions(self):
        """
        Выбор уровня доступа для пользователя в зависимости от запроса.
        """
        if self.action in ('create', 'update', 'destroy'):
            self.permission_classes = (IsAdminPermission,)
        return [permission() for permission in self.permission_classes]


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для реализации CRUD операций с моделью Recipe:
    - получения списка всех рецептов;
    - получение детализации о рецепте по его id;
    - создание нового рецепта;
    - обновление существующего рецепта;
    - удаление рецепта по его id.
    """
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        '''Выбор сериализатора в зависимости от запроса.'''
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def get_permissions(self):
        """
        Выбор уровня доступа для пользователя в зависимости от запроса.
        """
        if self.action in ('list', 'retrieve'):
            self.permission_classes = (AllowAny,)
        if self.action in ('create', 'update', 'destroy'):
            self.permission_classes = (IsAdminOrAuthorOrReadOnlyPermission,)
        return [permission() for permission in self.permission_classes]

    @action(
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        detail=True
    )
    def favorite(self, request, pk):
        """Добавление рецепта в список "Избранное" по его id."""
        if request.method == 'POST':
            return post(request, pk, FavoriteRecipe, RecipeShortReadSerializer)
        return delete(request, pk, FavoriteRecipe)

    @action(
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        detail=True
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return post(request, pk, ShoppingCart, RecipeShortReadSerializer)
        return delete(request, pk, ShoppingCart)


class TagViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для реализации операций с моделью Tag:
    - получения списка всех тегов;
    - получение детализации о теге по его id;
    — добавление нового тега (для администратора);
    — обновление тега (для администратора);
    — удаление тега (для администратора).
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)

    def get_permissions(self):
        """
        Выбор уровня доступа для пользователя в зависимости от запроса.
        """
        if self.action in ('create', 'update', 'destroy'):
            self.permission_classes = (IsAdminPermission,)
        return [permission() for permission in self.permission_classes]


@action(detail=False, permission_classes=(IsAuthenticated,))
class ShoppingCardView(APIView):
    def get(self, request):
        recipes_in_shopping_list = Recipe.objects.filter(
            recipe_on_shopping_cart__user=request.user
        ).annotate(
            sum_ingredients=Sum('recipe_to_ingredient__amount')
        ).values_list(
            'ingredients__name',
            'ingredients__measurement_unit',
            'sum_ingredients'
        )
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4, bottomup=0)
        font = 'Tantular'
        pdfmetrics.registerFont(
            TTFont('Tantular', 'backend/static/fonts/Tantular.ttf', 'UTF-8')
        )
        textobj = pdf.beginText()
        textobj.setTextOrigin(inch, inch)
        textobj.setFont(font, 12)
        lines = []
        lines.append('Список покупок:')
        lines.append('-' * settings.DIVIDING_LINE_LENGTH)
        for i, recipe in enumerate(recipes_in_shopping_list, start=1):
            lines.append(f'{i}. {recipe[0]} ({recipe[1]}) - {recipe[2]}')
            lines.append(' ')
        for line in lines:
            textobj.textLine(line)
        pdf.drawText(textobj)
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename='shopping_list.pdf'
        )
