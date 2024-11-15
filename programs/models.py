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

    def __str__(self):
        return self.name


class EducationLevel(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'education_levels'  # This is optional if you want to specify the table name

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
