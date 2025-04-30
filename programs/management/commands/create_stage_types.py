from django.core.management.base import BaseCommand
from programs.models import StageType


class Command(BaseCommand):
    help = 'Загружаем список этапов'

    def handle(self, *args, **options):
        StageType.objects.bulk_create([
            StageType(name='Иcходные данные', stage_number=1),
            StageType(name='Реконструкция деятельности', stage_number=2),
            StageType(name='Профессиональные дисциплины', stage_number=3),
            StageType(name='Общепрофессиональные дисциплины', stage_number=4),
            StageType(name='Учебный план', stage_number=5),
            StageType(name='Дизайн-концепт', stage_number=6),
        ])
        self.stdout.write(self.style.SUCCESS('Successfully loaded stage_types'))
