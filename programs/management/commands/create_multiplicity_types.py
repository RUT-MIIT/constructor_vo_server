from django.core.management.base import BaseCommand
from programs.models import MultiplicityType


class Command(BaseCommand):
    help = 'Загружаем список типов кратностей'

    def handle(self, *args, **options):
        MultiplicityType.objects.bulk_create([
            MultiplicityType(name='Один продукт', code='one-product', position=1),
            MultiplicityType(name='Один этап ЖЦ', code='one-lifestage', position=2),
            MultiplicityType(name='Несколько этапов ЖЦ', code='multi-lifestage', position=3),
            MultiplicityType(name='Один процесс', code='one-process', position=4),
            MultiplicityType(name='Несколько процессоа', code='multi-process', position=5),

        ])
        self.stdout.write(self.style.SUCCESS('Successfully loaded MultiplicityTypes'))
