from django.conf import settings
from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _

from recipes.validators import tag_regex_validator, tag_color_validator
from users.models import CustomUser


Enum = (
    (0, False),
    (1, True),
)

class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        verbose_name=_('название'),
        max_length=settings.INGREDIENT_NAME_LENGTH,
    )
    measurement_unit = models.CharField(
        verbose_name=_('единица измерения'),
        max_length=settings.MEASUREMENT_UNIT_LENGTH,
    )

    class Meta:
        verbose_name = _('ингредиент')
        verbose_name_plural = _('ингредиенты')

    def __str__(self):
        """Строковое представление объекта модели Ingredient."""
        return self.name


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        verbose_name=_('Название'),
        max_length=settings.TAG_NAME_LENGTH,
        unique=True
    )
    color = models.CharField(
        verbose_name=_('Цвет в HEX-формате'),
        max_length=settings.TAG_COLOR_LENGTH,
        validators=(tag_color_validator,)
    )
    slug = models.CharField(
        verbose_name=_('Обозначение'),
        max_length=settings.TAG_SLUG_LENGTH,
        validators=(tag_regex_validator,),
        unique=True
    )

    class Meta:
        verbose_name = _('тег')
        verbose_name_plural = _('теги')

    def __str__(self):
        """Строковое представление объекта модели Tag."""
        return f'{self.name}'


class Recipe(models.Model):
    """Модель рецептов."""
    author = models.ForeignKey(
        verbose_name=_('автор рецепта'),
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='own_recipe'
    )
    created = models.DateTimeField(
        verbose_name=_('дата создания'),
        auto_now_add=True,
        db_index=True
    )
    ingredients = models.ManyToManyField(
        to=Ingredient,
        through='IngredientToRecipe',
        related_name='in_recipe'
    )
    tags = models.ManyToManyField(
        verbose_name=_('теги'),
        to=Tag,
        through='TagToRecipe',
        related_name='tags_for_recipe'
    )
    image = models.ImageField(
        verbose_name=_('изображение'),
        upload_to='recipes/images/',
    )
    name = models.CharField(
        verbose_name=_('название рецепта'),
        max_length=settings.RECIPE_NAME_LENGTH,
        unique=True
    )
    text = models.CharField(
        verbose_name=_('описание'),
        max_length=settings.RECIPE_TEXT_NAME_LENGTH,
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name=_('время приготовления (в минутах)'),
        default=1
    )

    class Meta:
        verbose_name = _('рецепт')
        verbose_name_plural = _('рецепты')
        ordering = ('created',)
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'name'),
                name='unique_author_name'
            )
        ]

    def __str__(self):
        """Строковое представление объекта модели Recipe."""
        return self.name


class FavoriteRecipe(models.Model):
    """Модель списка "Избранное" для рецептов."""
    user = models.ForeignKey(
        verbose_name=_('пользователь'),
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='user'
    )
    recipe = models.ForeignKey(
        verbose_name=_('рецепт в списке "Избранное"'),
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe'
    )

    class Meta:
        verbose_name = _('список "Избранное"')
        verbose_name_plural = _('списки "Избранное"')
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe'
            )
        ]

    def __str__(self):
        """Строковое представление объекта модели FavoriteRecipe."""
        return f'{self.recipe} в списке "Избранное" {self.user}'


class ShoppingCart(models.Model):
    """Модель списка покупок."""
    recipe = models.ForeignKey(
        verbose_name=_('рецепт в списке покупок'),
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_on_shopping_cart'
    )
    user = models.ForeignKey(
        verbose_name=_('пользователь'),
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='shopper'
    )
    add_date = models.DateTimeField(
        verbose_name=_('дата добавления'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('рецепт в списке покупок')
        verbose_name_plural = _('рецепты в списках покупок')
        ordering = ('-add_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_recipe_in_cart'
            ),
        )

    def __str__(self):
        """Строковое представление объекта модели RecipeToShopping."""
        return f'{self.recipe} в списке покупок {self.user}'


class IngredientToRecipe(models.Model):
    """Модель для связи ингредиентов и рецептов."""
    ingredient = models.ForeignKey(
        verbose_name=_('ингредиент'),
        to=Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_to_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name=_('количество'),
        validators=(validators.MinValueValidator(
            1, message='Минимальное количество ингредиентов 1'),
        )
    )
    recipe = models.ForeignKey(
        verbose_name=_('рецепт'),
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_to_ingredient'
    )

    class Meta:
        verbose_name = _('ингредиент в рецепте')
        verbose_name_plural = _('ингердиенты в рецептах')
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_ingredient_in_recipe'
            ),
        )

    def __str__(self):
        """Строковое представление объекта модели IngredientToRecipe."""
        return f'{self.ingredient} - {self.recipe}'


class TagToRecipe(models.Model):
    """Модель для связи тегов и рецептов."""
    tag = models.ForeignKey(
        verbose_name=_('тег'),
        to=Tag,
        on_delete=models.CASCADE,
        related_name='tag_for_recipe'
    )
    recipe = models.ForeignKey(
        verbose_name=_('рецепт с тегом'),
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_to_tag'
    )

    class Meta:
        verbose_name = _('тег для рецепта')
        verbose_name_plural = _('теги для рецептов')
        constraints = (
            models.UniqueConstraint(
                fields=('tag', 'recipe'),
                name='unique_tag_for_recipe'
            ),
        )

    def __str__(self):
        """Строковое представление объекта модели TagToRecipe."""
        return f'{self.tag} - {self.recipe}'
