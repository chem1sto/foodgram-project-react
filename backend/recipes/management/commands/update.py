import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from recipes.models import (
    Ingredient,
    Tag
)


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


action = {
    'ingredients.csv': ingredient_create,
    'tags.csv': tag_create,
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
                for row in reader:
                    action[filename](row)
