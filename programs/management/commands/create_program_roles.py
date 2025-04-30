from django.core.management.base import BaseCommand
from programs.models import ProgramRole


class Command(BaseCommand):
    help = 'Загружаем список ролей'

    def handle(self, *args, **options):
        ProgramRole.objects.bulk_create([
            ProgramRole(name='Методист'),
            ProgramRole(name='Руководитель проекта'),
            ProgramRole(name='Внутренний эксперт'),
            ProgramRole(name='Внешний эксперт'),
            ProgramRole(name='Эксперт по учебной работе'),
            ProgramRole(name='Наблюдатель'),
        ])
        self.stdout.write(self.style.SUCCESS('Successfully loaded roles'))
