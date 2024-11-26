from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Direction(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=500)
    level = models.CharField(max_length=500)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'education_directions'  # This is optional if you want to specify the exact table name
        ordering = ['created_at']
        verbose_name = "Направление обучения"
        verbose_name_plural = "Направления обучения"
    def __str__(self):
        return self.name


class EducationLevel(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'education_levels'  # This is optional if you want to specify the table name
        ordering = ['created_at']
        verbose_name = "Уровень образования"
        verbose_name_plural = "Уровни образования"
    def __str__(self):
        return self.name


class ProgramRole(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'program_roles'
        ordering = ['created_at']
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

class Program(models.Model):
    FORMS = [
        ('Очная', 'Очная'),
        ('Очно-заочная', 'Очно-заочная'),
        ('Заочная', 'Заочная'),
    ]

    profile = models.CharField(max_length=255)
    annotation = models.TextField(null=True, blank=True)
    author = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='programs')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    level_id = models.ForeignKey('EducationLevel', on_delete=models.RESTRICT, default=1)
    direction_id = models.ForeignKey('Direction', on_delete=models.CASCADE, default=1)
    # type = models.IntegerField(default=1)
    form = models.CharField(
        max_length=20,
        choices=FORMS,
        default='Очная'
    )
    max_semesters = models.PositiveIntegerField(null=True)
    fgos_file = models.FileField(upload_to='fgos_files/', null=True, blank=True)
    class Meta:
        db_table = 'programs'
        verbose_name = "Программа"
        verbose_name_plural = "Программы"

    def __str__(self):
        return self.profile


class ProgramUser(models.Model):
    user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='work_programs', null=True,
        blank=True
    )
    program_id = models.ForeignKey(
        'Program', on_delete=models.CASCADE, related_name='participants',
        null=True, blank=True
    )
    role_id = models.ForeignKey(
        'ProgramRole', on_delete=models.CASCADE,
        null=True, blank=True
    )

    class Meta:
        db_table = 'program_users'
        verbose_name = "Роль пользователя"
        verbose_name_plural = "Роли пользователя"

class NsiType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    position = models.IntegerField()
    part = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=255)

    class Meta:
        ordering = ['position']
        verbose_name = 'Тип НСИ'
        verbose_name_plural = 'Типы НСИ'

    def __str__(self):
        return self.name


class Ministry(models.Model):
    fullname = models.TextField()
    short_nominative = models.CharField(max_length=191)
    short_genitive = models.CharField(max_length=191)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fullname

    class Meta:
        ordering = ['created_at']
        verbose_name = "Министерство"
        verbose_name_plural = "Министерства"

class Nsi(models.Model):
    type = models.ForeignKey(NsiType, on_delete=models.SET_NULL, null=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    old_name = models.CharField(max_length=2000, null=True, blank=True)
    start_date = models.CharField(max_length=100, null=True, blank=True)
    accept_date = models.CharField(max_length=100, null=True, blank=True)
    accept_number = models.CharField(max_length=100, null=True, blank=True)

    nsiDate = models.DateField(null=True, blank=True)
    nsiNumber = models.CharField(max_length=191, null=True, blank=True)
    nsiEdit = models.CharField(max_length=191, null=True, blank=True)
    nsiName = models.TextField(null=True, blank=True)
    nsiApproveName = models.CharField(max_length=191, null=True, blank=True)
    nsiProtocolDate = models.DateField(null=True, blank=True)
    nsiCode = models.CharField(max_length=191, null=True, blank=True)
    nsiPeriod = models.CharField(max_length=191, null=True, blank=True)
    nsiBasis = models.TextField(null=True, blank=True)
    nsiAuthors = models.TextField(null=True, blank=True)
    nsiEditor = models.CharField(max_length=191, null=True, blank=True)
    nsiCity = models.CharField(max_length=191, null=True, blank=True)
    nsiYear = models.IntegerField(null=True, blank=True)
    nsiPages = models.CharField(max_length=200, null=True, blank=True)
    nsiProtocolNumber = models.CharField(max_length=191, null=True, blank=True)
    nsiLink = models.TextField(null=True, blank=True)
    nsiFullName = models.TextField(null=True, blank=True)
    nsiMinistry = models.ForeignKey(Ministry, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(null=True, auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(null=True, auto_now_add=True, blank=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "НСИ"
        verbose_name_plural = "НСИ"

class StageType(models.Model):
    name = models.CharField(max_length=255)
    stage_number = models.PositiveIntegerField()
    code = models.CharField(max_length=255, null=True, blank=True)
    class Meta:
        ordering = ['stage_number']  # Сортировка по номеру этапа
        verbose_name = "Тип этап разработки"
        verbose_name_plural = "Типы этапов разработки"

    def __str__(self):
        return self.name

class Stage(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='stages')
    stage_type = models.ForeignKey(StageType, null=True, on_delete=models.CASCADE, related_name='stages')
    result = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['program']
        verbose_name = "Этап разработки программы"
        verbose_name_plural = "Этапы разработки программ"

class WizardType(models.Model):
    name = models.CharField(max_length=300)
    code = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип мастера"
        verbose_name_plural = "Типы мастеров"

class StepType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=255, null=True)
    wizard_type = models.ForeignKey(WizardType, on_delete=models.CASCADE, related_name='step_types')
    position = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['position']
        verbose_name = "Тип шага"
        verbose_name_plural = "Типы шагов"

class Wizard(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='wizards')
    wizard_type = models.ForeignKey(WizardType, on_delete=models.CASCADE)
    created_at = models.DateTimeField(null=True, auto_now_add=True, blank=True)
    def __str__(self):
        return f"{self.program} - {self.wizard_type}"

    class Meta:
        ordering = ['created_at']
        verbose_name = "Мастер ИИ"
        verbose_name_plural = "Мастера ИИ"
class Step(models.Model):
    wizard = models.ForeignKey(Wizard, on_delete=models.CASCADE, related_name='steps')
    step_type = models.ForeignKey(StepType, on_delete=models.CASCADE)
    created_at = models.DateTimeField(null=True, auto_now_add=True, blank=True)
    chunks = models.JSONField(null=True, blank=True)
    result = models.TextField(null=True, blank=True)
    result_json = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Шаг ИИ"
        verbose_name_plural = "Шаги ИИ"


class Product (models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    position = models.IntegerField(null=True, blank=True)
    nsis = models.ManyToManyField('Nsi', related_name='products', blank=True)

    class Meta:
        ordering = ['program','position']
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
