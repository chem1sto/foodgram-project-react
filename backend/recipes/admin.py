from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from recipes.models import (FavoriteRecipe, Ingredient, IngredientToRecipe,
                            Recipe, Shopping_cart, Tag, TagToRecipe)
from users.models import CustomUser, Subscription


admin.site.unregister(Group)


class CustomUserAdmin(UserAdmin):
    pass


admin.site.register(CustomUser, CustomUserAdmin)


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'date_joined',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'role'
    )
    search_fields = ('username', 'email', 'role', 'date_joined')
    list_filter = ('username', 'email')
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'subscribing')
    search_fields = ('subscriber',)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'created',
        'image',
        'cooking_time',
        'count_favorites'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('author', 'name', 'tags')
    ordering = ('name',)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY

    def count_favorites(self, recipe):
        return recipe.favorite_recipe.count()
    count_favorites.short_description = _('Добавлено в "Избранное"')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')
    ordering = ('name',)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    ordering = ('id',)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(TagToRecipe)
class TagToRecipeAdmin(admin.ModelAdmin):
    list_display = ('tag', 'recipe')
    list_filter = ('tag',)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(IngredientToRecipe)
class IngredientToRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'amount', 'recipe')
    list_filter = ('ingredient',)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe',)
    search_fields = ('user',)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(Shopping_cart)
class Shopping_cartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user', 'add_date')
    search_fields = ('user',)
    list_filter = ('add_date',)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
