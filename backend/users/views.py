from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.serializers import (SetPasswordSerializer, SignUpUserSerializer,
                             SubscriptionSerializer, UserProfileSerializer)
from api.permissions import IsAdminPermission, IsStaffOrAuthorOrReadOnlyPermission
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
        '''Выбо сериализатора в зависимости от полученного запроса.'''
        if self.action in ('list', 'retrieve'):
            return UserProfileSerializer
        return SignUpUserSerializer

    def get_permissions(self):
        """
        Выбор уровня доступа для пользователя в зависимости от полученного запроса.
        """
        if self.action == 'retrieve':
            self.permission_classes = (IsStaffOrAuthorOrReadOnlyPermission,)
        elif self.action == 'destroy':
            self.permission_classes = (IsAdminPermission,)
        return [permission() for permission in self.permission_classes]


    @action(url_path='me', detail=False, permission_classes=(AllowAny,))
    def me(self, request):
        """Получение детализации текущего пользователя."""
        return Response(
            UserProfileSerializer(request.user).data, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='set_password', permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        """Изменение пароля текущего пользователя."""
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe', permission_classes=(IsAuthenticated,))
    def create_or_delete_subscribing(self, request, pk):
        """Создание или удаление подписки на пользователя по его id."""
        subscriber = CustomUser.objects.get(pk=request.user.id)
        subscribing = get_object_or_404(CustomUser, pk=pk)
        if request.method == 'POST':
            if subscriber == subscribing:
                raise ValidationError({'errors': _('Вы уже подписаны на данного пользователя.')})
            if Subscription.objects.filter(
                subscriber=subscriber,
                subscribing=subscribing
                ).exists():
                    raise ValidationError({'errors': _('Вы уже подписаны на данного пользователя.')})
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
