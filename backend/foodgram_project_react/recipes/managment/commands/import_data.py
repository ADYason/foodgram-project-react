from _parsers import ingredients_parser
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        path = '../../data/'
        ingredients_parser(f'{path}/ingredients.csv')
