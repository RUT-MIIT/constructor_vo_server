from django.core.management.base import BaseCommand
from programs.models import EducationLevel


class Command(BaseCommand):
    help = 'Загружаем список уровней образования'

    def handle(self, *args, **options):
        EducationLevel.objects.bulk_create([
            EducationLevel(name='Бакалавриат'),
            EducationLevel(name='Специалитет'),
            EducationLevel(name='Магистратура'),
        ])
        self.stdout.write(self.style.SUCCESS('Successfully loaded levels'))
