import csv

from ...models import Ingredients


def ingredients_parser(file):
    with open(file) as f:
        reader = csv.reader(f,)
        for row in reader:
            _, created = Ingredients.objects.get_or_create(
                name=row[0],
                measurment_unint=row[1],
                )
