import base64
import csv
import os

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from recipes.models import (
    Ingredient,
    IngredientToRecipe,
    Recipe,
    Tag,
    TagToRecipe
)
from users.models import CustomUser


def ingredient_create(row):
    Ingredient.objects.get_or_create(
        name=row[0],
        measurement_unit=row[1],
    )


def tag_create(row):
    Tag.objects.get_or_create(
        name=row[0],
        color=row[1],
        slug=row[2],
    )


def recipe_create(row, author):
    ingredients = Ingredient.objects.all()
    tags = Tag.objects.all()
    format, row[27] = row[27].split(';base64,')
    ext = format.split('/')[-1]
    recipe = Recipe.objects.get_or_create(
        author=author[0],
        image=ContentFile(base64.b64decode(row[27]), name='temp.' + ext),
        name= row[28],
        text=row[29],
        cooking_time=row[30]
    )
    for i in range(0,22,2):
        if row[i] != 'нет':
            IngredientToRecipe.objects.get_or_create(
                ingredient=ingredients[int(row[i])-1],
                amount=row[i+1],
                recipe=recipe[0]
            )
    for j in range(24,27):
        if row[j] != 'нет':
            TagToRecipe.objects.get_or_create(
                tag=tags[int(row[j])],
                recipe=recipe[0]
            )


action = {
    'ingredients.csv': ingredient_create,
    'tags.csv': tag_create,
    'recipes.csv': recipe_create
}


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            nargs='+',
            type=str
        )

    def handle(self, *args, **options):
        for filename in options['filename']:
            path = os.path.join(settings.BASE_DIR, 'data/') + filename
            with open(path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                if filename == 'recipes.csv':
                    author = CustomUser.objects.get_or_create(
                        username='vasya.pupkin',
                        email='vasya@yandex.ru',
                        first_name='Вася',
                        last_name='Пупкин',
                        password = make_password('password'),
                        role='admin',
                    )
                    for row in reader:
                        action[filename](row, author)
                else:
                    for row in reader:
                        action[filename](row)
