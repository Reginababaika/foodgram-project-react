import csv
from django.core.management.base import BaseCommand
from foodgram.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('data/ingredients.csv', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            ingredients = [
             Ingredient(
             name=row[0],
             measurement_unit=row[1],
             )
             for row in reader
            ]
            Ingredient.objects.bulk_create(ingredients)
