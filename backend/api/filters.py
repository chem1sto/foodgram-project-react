from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag
from users.models import CustomUser


class IngredientFilter(FilterSet):
    """Фильтр для поиска ингредиентов по названию."""
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class RecipeFilter(FilterSet):
    """
    Фильтр для поиска рецептов по тегам
    и полям is_favorited и is_in_shopping_cart.
    """
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = filters.ModelChoiceFilter(
        queryset=CustomUser.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def get_is_favorited(self, queryset, name, value):
        """Фильтрация очереди рецептов по полю is_favorited."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(
                favorite_recipe__user=self.request.user
            )
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация очереди рецептов по полю is_in_shopping_cart."""
        if self.request.user.is_authenticated and value:
            return queryset.filter(
                recipe_on_shopping_cart__user=self.request.user
            )
        return queryset.all()
