from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework.routers import DefaultRouter

from api.views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                       ShoppingCardView, TagViewSet)


router_api = DefaultRouter()
router_api.register(r'users', CustomUserViewSet)
router_api.register(r'ingredients', IngredientViewSet)
router_api.register(r'recipes', RecipeViewSet)
router_api.register(r'tags', TagViewSet)

auth_token_urls = [
    path('login/', TokenCreateView.as_view()),
    path('logout/', TokenDestroyView.as_view()),
]

urlpatterns = [
    path(
        'api/recipes/download_shopping_cart/',
        ShoppingCardView.as_view(),
        name='download_shopping_cart'
    ),
    path('api/', include(router_api.urls)),
    path('api/auth/token/', include(auth_token_urls)),
]
