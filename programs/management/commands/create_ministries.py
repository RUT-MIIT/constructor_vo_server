# create_ministries.py
import datetime
from django.core.management.base import BaseCommand
from programs.models import Ministry


class Command(BaseCommand):
    help = 'Load ministries data into the database'

    def handle(self, *args, **kwargs):
        # Данные для загрузки
        data = [
            {'fullname': 'Министерство внутренних дел Российской Федерации', 'short_nominative': 'МВД России',
             'short_genitive': 'МВД России'},
            {
                'fullname': 'Министерство Российской Федерации по делам гражданской обороны, чрезвычайным ситуациям и ликвидации последствий стихийных бедствий',
                'short_nominative': 'МЧС России', 'short_genitive': 'МЧС России'},
            {'fullname': 'Министерство иностранных дел Российской Федерации', 'short_nominative': 'МИД России',
             'short_genitive': 'МИД России'},
            {'fullname': 'Министерство обороны Российской Федерации', 'short_nominative': 'Минобороны России',
             'short_genitive': 'Минобороны России'},
            {'fullname': 'Министерство юстиции Российской Федерации', 'short_nominative': 'Минюст России',
             'short_genitive': 'Минюста России'},
            {'fullname': 'Министерство здравоохранения Российской Федерации', 'short_nominative': 'Минздрав России',
             'short_genitive': 'Минздрава России'},
            {'fullname': 'Министерство культуры Российской Федерации', 'short_nominative': 'Минкультуры России',
             'short_genitive': 'Минкультуры России'},
            {'fullname': 'Министерство науки и высшего образования Российской Федерации',
             'short_nominative': 'Минобрнауки России', 'short_genitive': 'Минобрнауки России'},
            {'fullname': 'Министерство природных ресурсов и экологии Российской Федерации',
             'short_nominative': 'Минприроды России', 'short_genitive': 'Минприроды России'},
            {'fullname': 'Министерство промышленности и торговли Российской Федерации',
             'short_nominative': 'Минпромторг России', 'short_genitive': 'Минпромторга России'},
            {'fullname': 'Министерство просвещения Российской Федерации', 'short_nominative': 'Минпросвещения России',
             'short_genitive': 'Минпросвещения России'},
            {'fullname': 'Министерство Российской Федерации по развитию Дальнего Востока и Арктики',
             'short_nominative': 'Минвостокразвития России', 'short_genitive': 'Минвостокразвития России'},
            {'fullname': 'Министерство сельского хозяйства Российской Федерации',
             'short_nominative': 'Минсельхоз России', 'short_genitive': 'Минсельхоза России'},
            {'fullname': 'Министерство спорта Российской Федерации', 'short_nominative': 'Минспорт России',
             'short_genitive': 'Минспорта России'},
            {'fullname': 'Министерство строительства и жилищно-коммунального хозяйства Российской Федерации',
             'short_nominative': 'Минстрой России', 'short_genitive': 'Минстроя России'},
            {'fullname': 'Министерство транспорта Российской Федерации', 'short_nominative': 'Минтранс России',
             'short_genitive': 'Минтранса России'},
            {'fullname': 'Министерство труда и социальной защиты Российской Федерации',
             'short_nominative': 'Минтруд России', 'short_genitive': 'Минтруда России'},
            {'fullname': 'Министерство финансов Российской Федерации', 'short_nominative': 'Минфин России',
             'short_genitive': 'Минфина России'},
            {'fullname': 'Министерство цифрового развития, связи и массовых коммуникаций Российской Федерации',
             'short_nominative': 'Минцифры России', 'short_genitive': 'Минцифры России'},
            {'fullname': 'Министерство экономического развития Российской Федерации',
             'short_nominative': 'Минэкономразвития России', 'short_genitive': 'Минэкономразвития России'},
            {'fullname': 'Министерство энергетики Российской Федерации', 'short_nominative': 'Минэнерго России',
             'short_genitive': 'Минэнерго России'},
        ]

        # Создание и сохранение объектов моделей
        for ministry_data in data:
            ministry = Ministry(**ministry_data)
            ministry.save()

        self.stdout.write(self.style.SUCCESS('Successfully loaded ministries'))
