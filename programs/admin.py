from django.contrib import admin
from .models import Direction, EducationLevel, ProgramRole, Program, ProgramUser, NsiType, Ministry, Nsi

@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'level', 'created_at', 'updated_at')
    search_fields = ('code', 'name')
    list_filter = ('level',)

@admin.register(EducationLevel)
class EducationLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(ProgramRole)
class ProgramRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('profile', 'author', 'level_id', 'direction_id', 'form', 'max_semesters', 'created_at', 'updated_at')
    search_fields = ('profile', 'author__email')
    list_filter = ('form', 'level_id', 'direction_id')
    raw_id_fields = ('author',)

@admin.register(ProgramUser)
class ProgramUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'program_id', 'role_id')
    search_fields = ('user_id__email', 'program_id__profile')
    list_filter = ('role_id',)

@admin.register(NsiType)
class NsiTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'part', 'active', 'created_at', 'updated_at')
    search_fields = ('name', 'code')
    list_filter = ('active',)

@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'short_nominative', 'short_genitive', 'created_at', 'updated_at')
    search_fields = ('fullname', 'short_nominative', 'short_genitive')

@admin.register(Nsi)
class NsiAdmin(admin.ModelAdmin):
    list_display = ('type', 'program', 'author', 'nsiName', 'nsiCode', 'nsiYear', 'nsiCity', 'created_at', 'updated_at')
    search_fields = ('nsiName', 'nsiCode', 'nsiFullName')
    list_filter = ('type', 'nsiYear')
    raw_id_fields = ('author', 'program', 'nsiMinistry')
