from csv import reader
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Наполнение базы данных"""

    def handle(self, *args, **kwargs):
        path = 'recipes/data/ingredients.csv'
        with open(path, 'r', encoding='utf-8') as f:
            for row in reader(f):
                if len(row) == 2:
                    Ingredient.objects.get_or_create(
                        name=row[0], measurement_unit=row[1],
                    )
