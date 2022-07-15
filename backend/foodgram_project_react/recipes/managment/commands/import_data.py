from django.core.management.base import BaseCommand
from _parsers import ingredients_parser

class Command(BaseCommand):
    def handle(self, *args, **options):
        path = '../../data/'
        ingredients_parser(f'{path}/ingredients.csv')
