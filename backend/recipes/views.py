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
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import (IngredientSerializer, RecipeCreateSerializer,
                             RecipeReadSerializer, RecipeShortReadSerializer,
                             TagSerializer)
from api.permissions import IsAdminPermission, IsStaffOrAuthorOrReadOnlyPermission
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            Shopping_cart, Tag)


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
        Выбор уровня доступа для пользователя в зависимости от полученного запроса.
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
        '''Выбор сериализатора в зависимости от полученного запроса.'''
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def get_permissions(self):
        """
        Выбор уровня доступа для пользователя в зависимости от полученного запроса.
        """
        if self.action in ('list', 'retrieve'):
            self.permission_classes = (AllowAny,)
        if self.action in ('create', 'update', 'destroy'):
            self.permission_classes = (IsStaffOrAuthorOrReadOnlyPermission,)
        return [permission() for permission in self.permission_classes]

    @action(
        methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=(IsAuthenticated,),
        detail=True
    )
    def favorite_recipe(self, request, pk):
        """Добавление рецепта в список "Избранное" по его id."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = RecipeShortReadSerializer(
                instance=recipe,
                context={'request': request}
            )
            if not FavoriteRecipe.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                FavoriteRecipe.objects.create(
                    user=request.user,
                    recipe=recipe,
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                {'errors': _('рецепт уже добавлен в список "Избранное"')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            get_object_or_404(
                FavoriteRecipe,
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        detail=True
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = RecipeShortReadSerializer(
                instance=recipe,
                context={'request': request}
            )
            if not Shopping_cart.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                Shopping_cart.objects.create(
                    user=request.user,
                    recipe=recipe,
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                {'errors': _('рецепт уже добавлен в список покупок')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            get_object_or_404(
                Shopping_cart,
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


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
        Выбор уровня доступа для пользователя в зависимости от полученного запроса.
        """
        if self.action in ('create', 'update', 'destroy'):
            self.permission_classes = (IsAdminPermission,)
        return [permission() for permission in self.permission_classes]


@action(detail=False, permission_classes=(IsAuthenticated,))
class ShoppingCardView(APIView):
    def get(self, request):
        recipes_in_shopping_list = Recipe.objects.filter(
            recipe_on_shopping_cart__user=request.user
        ).annotate(sum_ingredients=Sum('recipe_to_ingredient__amount')
            ).values_list(
            'ingredients__name',
            'ingredients__measurement_unit',
            'sum_ingredients'
        )
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4, bottomup=0)
        font = 'Tantular'
        pdfmetrics.registerFont(TTFont('Tantular', 'backend/static/fonts/Tantular.ttf', 'UTF-8'))
        textobj = pdf.beginText()
        textobj.setTextOrigin(inch, inch)
        textobj.setFont(font, 12)
        lines = []
        lines.append('Список покупок:')
        lines.append('-'*settings.DIVIDING_LINE_LENGTH)
        for i, recipe in enumerate(recipes_in_shopping_list, start=1):
            lines.append(f'{i}. {recipe[0]} ({recipe[1]}) - {recipe[2]}')
            lines.append(' ')
        for line in lines:
            textobj.textLine(line)
        pdf.drawText(textobj)
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='shopping_list.pdf')