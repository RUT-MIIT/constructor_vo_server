import csv
import os
from django.core.management.base import BaseCommand
from programs.models import Direction



class Command(BaseCommand):
    help = 'Загружаем список направлений образования'

    def handle(self, *args, **options):
        file_name = "directions.csv"
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 file_name)

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            directions = []

            for row in reader:
                direction = Direction(
                    code=row['code'],
                    name=row['name'],
                    level=row['level'],
                )
                directions.append(direction)

            Direction.objects.bulk_create(directions)

        self.stdout.write(self.style.SUCCESS('Successfully loaded directions'))
