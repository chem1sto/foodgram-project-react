from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.fields import Base64ImageField
from recipes.models import (FavoriteRecipe, Ingredient, IngredientToRecipe,
                            Recipe, ShoppingCart, Tag, TagToRecipe)
from users.models import CustomUser, Subscription


class SignUpUserSerializer(UserCreateSerializer):
    """Сериализатор для получения данных о новом пользователе."""
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода детализации о пользовате по его id."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        read_only_fields = fields

    def get_is_subscribed(self, subscribing):
        '''Получение значения для поля пользователя is_subscribed.'''
        if self.context.get('request') and not (
            self.context.get('request').user.is_anonymous
        ):
            return Subscription.objects.filter(
                subscriber=self.context.get('request').user.id,
                subscribing=subscribing
            ).exists()
        return False


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор для для изменения пароля пользователя."""
    new_password = serializers.CharField(
        write_only=True,
        max_length=settings.PASSWORD_LENGTH,
        required=True
    )
    current_password = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = ('new_password', 'current_password')

    def validate_current_password(self, value):
        '''Валидация значения current_password.'''
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError(_('Указан неправильный пароль.'))
        return value

    def validate_new_password(self, value):
        '''Валидация значения new_password.'''
        validate_password(value)
        return value

    def save(self):
        '''Переопределение метода save сериализатора.'''
        password = self.validated_data['new_password']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class RecipeShortReadSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода сокращённой информации о рецепте."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода информации о подписке пользователя."""
    is_subscribed = serializers.SerializerMethodField(default=False)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, subscribing):
        '''Получение значения для поля подписки пользователя is_subscribed.'''
        if self.context.get('request'):
            return Subscription.objects.filter(
                subscriber=self.context.get('request').user.id,
                subscribing=subscribing
            ).exists()
        return False

    def get_recipes(self, subscriber):
        '''Получение рецептов автора с выводом нужного количества рецептов.'''
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        author_recipes = Recipe.objects.filter(author=subscriber)
        if limit:
            author_recipes = author_recipes[:int(limit)]
        return RecipeShortReadSerializer(author_recipes, many=True).data

    def get_recipes_count(self, subscribing):
        '''Получение количества рецептов автора.'''
        return Recipe.objects.filter(author=subscribing).count()

    def validate(self, data):
        '''Валидация данных о подписке в зависимости от метода запроса.'''
        request = self.context.get('request')
        if request.method == 'DELETE':
            return data
        if self.context.get('subscriber') == self.context.get('subscribing'):
            raise serializers.ValidationError(_('Подписка на себя невозможна'))
        if Subscription.objects.filter(
            subscriber=self.context.get('subscriber'),
            subscribing=self.context.get('subscribing')
        ).exists():
            raise serializers.ValidationError(
                _('Вы уже подписаны на данного пользователя.')
            )
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода данных об ингредиенте."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientToRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода данных об ингредиенте в рецепте."""
    id = serializers.IntegerField(
        source='ingredient_id',
        required=True,
    )
    amount = serializers.IntegerField(
        required=True
    )

    class Meta:
        model = IngredientToRecipe
        fields = ('id', 'amount')


class IngredientToRecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с промежуточной моделью IngredientToRecipe.
    Вывод списка ингредиентов с указанием их количества для текущего рецепта.
    """
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id',
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientToRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientToRecipe.objects.all(),
                fields=['ingredient', 'recipe']
            )
        ]


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для получения данных о теге."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода информации о рецепте."""
    ingredients = IngredientToRecipeReadSerializer(
        source='recipe_to_ingredient',
        many=True
    )
    author = UserProfileSerializer(
        read_only=True
    )
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    image = Base64ImageField(
        required=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, recipe):
        '''Получение значения для поля рецепта is_subscribed.'''
        if not self.context.get('request').user.is_anonymous:
            return FavoriteRecipe.objects.filter(
                user=self.context.get('request').user,
                recipe=recipe
            ).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        '''Получение значения для поля рецепта is_in_shopping_cart.'''
        if not self.context.get('request').user.is_anonymous:
            return ShoppingCart.objects.filter(
                user=self.context.get('request').user,
                recipe=recipe
            ).exists()
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания нового рецепта."""
    ingredients = IngredientToRecipeSerializer(
        source='ingredient_to_recipe',
        many=True,
    )
    author = UserProfileSerializer(
        read_only=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(
        required=True
    )
    name = serializers.CharField(
        required=True
    )
    text = serializers.CharField(
        max_length=settings.RECIPE_TEXT_NAME_LENGTH,
        required=True
    )
    cooking_time = serializers.IntegerField(
        min_value=1,
        default=1
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, recipe):
        '''Валидация данных рецепта.'''
        ingred_to_recipe = recipe.get('ingredient_to_recipe')
        ingred_list = [ingred['ingredient_id'] for ingred in ingred_to_recipe]
        if len(ingred_list) != len(set(ingred_list)):
            raise serializers.ValidationError(
                _('В рецепте указаны дублирующиеся ингредиенты.')
            )
        return super().validate(recipe)

    def create(self, validated_data):
        '''Переопределение метода create для создания нового рецепта.'''
        request = self.context['request']
        if request.user.own_recipe.filter(
            name=validated_data.get('name')
        ).exists():
            raise serializers.ValidationError(
                _('Рецепт с таким именем уже существует.')
            )
        ingredients = validated_data.pop('ingredient_to_recipe')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=request.user,
            **validated_data
        )
        self.add_entries_to_related_models(recipe, ingredients, tags)
        return recipe

    def update(self, recipe, validated_data):
        '''Переопределение метода update для обновления данных о рецепте.'''
        ingredients = validated_data.pop('ingredient_to_recipe')
        tags = validated_data.pop('tags')
        IngredientToRecipe.objects.filter(
            recipe=recipe,
        ).delete()
        TagToRecipe.objects.filter(
            recipe=recipe,
        ).delete()
        self.add_entries_to_related_models(
            recipe=recipe,
            ingredients=ingredients,
            tags=tags
        )
        return super().update(recipe, validated_data)

    @staticmethod
    def add_entries_to_related_models(recipe, ingredients, tags):
        '''
        Статический метод для создания/обновления рецепта в связанных таблицах.
        '''
        TagToRecipe.objects.bulk_create(
            TagToRecipe(
                recipe=recipe,
                tag=tag,
            )
            for tag in tags
        )
        IngredientToRecipe.objects.bulk_create(
            IngredientToRecipe(
                recipe=recipe,
                ingredient=Ingredient.objects.get(
                    id=ingredient.get('ingredient_id')
                ),
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients
        )

    def to_representation(self, instance):
        '''
        Переопределение метода сериализатора to_representation
        для вывода данных о новом/обновленном рецепте.
        '''
        serializer = RecipeReadSerializer(
            instance=instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data
