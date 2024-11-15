from django.core.management.base import BaseCommand
from programs.models import ProgramRole


class Command(BaseCommand):
    help = 'Загружаем список ролей'

    def handle(self, *args, **options):
        ProgramRole.objects.bulk_create([
            ProgramRole(name='Методист'),
            ProgramRole(name='Эксперт'),
            ProgramRole(name='Супервайзер'),
            ProgramRole(name='Наблюдаель'),
        ])
        self.stdout.write(self.style.SUCCESS('Successfully loaded roles'))
