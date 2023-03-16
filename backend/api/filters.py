import django_filters

from recipes.models import Recipe, Tag
from users.models import CustomUser


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = django_filters.ModelChoiceFilter(
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')
