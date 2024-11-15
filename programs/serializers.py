import base64

from rest_framework import serializers
from programs.models import NsiType, Ministry, Nsi
from programs.models import EducationLevel, Direction, Program, ProgramRole, \
    ProgramUser
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from users.serializers import UserShortSerializer
from django.core.files.base import ContentFile
from drf_extra_fields.fields import Base64FileField
User = get_user_model()


class NsiTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NsiType
        fields = '__all__'


class MinistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Ministry
        fields = ['id', 'fullname', 'short_nominative', 'short_genitive']


class NsiSerializer(serializers.ModelSerializer):
    nsiDate = serializers.DateField(allow_null=True, required=False)
    nsiProtocolDate = serializers.DateField(allow_null=True, required=False)
    nsiYear = serializers.DateField(allow_null=True, required=False)

    class Meta:
        model = Nsi
        fields = '__all__'

    def to_internal_value(self, data):
        for field in ['nsiDate', 'nsiProtocolDate', 'nsiYear']:
            if data.get(field) == '':
                data[field] = None
        return super().to_internal_value(data)


class EducationLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationLevel
        fields = ['id', 'name']


class EducationDirectionSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Direction
        fields = ['id', 'code', 'name', 'level']

    def get_name(self, obj):
        # Объединяем значения полей code и name
        return f"{obj.code} {obj.name}"


class ProgramRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramRole
        fields = ['id', 'name']


class ProgramUserSerializer(serializers.ModelSerializer):
    role = ProgramRoleSerializer(source='role_id')
    user = UserShortSerializer(source='user_id')

    class Meta:
        model = ProgramUser
        fields = ['id', 'user', 'role', 'program_id']


class ProgramSerializer(serializers.ModelSerializer):
    direction = EducationDirectionSerializer(source='direction_id',read_only=True)
    level = EducationLevelSerializer(source='level_id', read_only=True)
    participants = ProgramUserSerializer(many=True, read_only=True)
    authorId = serializers.IntegerField(source='author_id', read_only=True)
    my_role = serializers.SerializerMethodField()
    form = serializers.CharField(required=True)

    fgos_file = serializers.DictField(write_only=True, required=False)
    fgos_url = serializers.FileField(source='fgos_file', read_only=True)


    class Meta:
        model = Program
        fields = (
            'id', 'profile', 'annotation', 'level', 'direction', 'form', 'participants', 'my_role', 'authorId',
            'fgos_file', 'fgos_url'
        )

    def convert_fgos_file(self, fgos_data):
        """
        Метод для валидации и преобразования Base64 в файл.
        """
        file_data = fgos_data.get('base64')
        filename = fgos_data.get('filename')

        if not file_data or not filename:
            raise serializers.ValidationError("Поле 'fgos_file' должно содержать 'base64' и 'filename'.")

        try:
            # Разделяем строку Base64
            format, file_str = file_data.split(';base64,')
        except ValueError:
            raise serializers.ValidationError("Неправильный формат строки Base64.")
        # Проверяем и получаем расширение файла
        ext = filename.split('.')[-1]
        allowed_extensions = ['txt', 'pdf', 'jpg', 'png','docx']  # Допустимые форматы
        if ext.lower() not in allowed_extensions:
            raise serializers.ValidationError(
                f"Недопустимое расширение файла: {ext}. Допустимые форматы: {', '.join(allowed_extensions)}"
            )

        # Создаем объект файла
        print("KEK")
        return ContentFile(base64.b64decode(file_str), name=filename)

    def validate(self, attrs):
        direction_data = self.initial_data.get('direction')
        direction = get_object_or_404(Direction, id=direction_data.get('id'))

        if '.03.' in direction.code:
            level_id = 1
        elif '.04.' in direction.code:
            level_id = 3
        else:
            level_id = 2

        level = get_object_or_404(EducationLevel, id=level_id)

        attrs['direction_id'] = direction
        attrs['level_id'] = level

        # Обрабатываем fgos_file, если оно есть
        fgos_file_data = attrs.get('fgos_file')
        if fgos_file_data:
            attrs['fgos_file'] = self.convert_fgos_file(fgos_file_data)
        return attrs

    def get_my_role(self, obj):
        user_id = self.context['request'].user.id
        roles = ProgramUser.objects.filter(user_id=user_id)
        name = roles.first().role_id.name if roles.exists() else ''
        return name

class ProgramInformationSerializer(serializers.ModelSerializer):
    participants = ProgramUserSerializer(many=True, read_only=True)
    level = EducationLevelSerializer(source='level_id')
    name = serializers.SerializerMethodField()
    my_role = serializers.SerializerMethodField()
    direction = EducationDirectionSerializer(source='direction_id')
    authorId = serializers.IntegerField(source='author_id', read_only=True)
    fgos_url = serializers.FileField(source='fgos_file', read_only=True)

    class Meta:
        model = Program
        fields = (
        'id', 'profile', 'form', 'annotation', 'participants', 'direction', 'level', 'name', 'authorId', 'my_role','fgos_url')

    def get_name(self, obj):
        return f"{obj.direction_id.code} {obj.direction_id.name} {obj.profile} ({obj.level_id.name})"

    def get_my_role(self, obj):
        user_id = self.context['request'].user.id
        roles = ProgramUser.objects.filter(user_id=user_id)
        name = roles.first().role_id.name if roles.exists() else ''
        return name

# class ProgramProductSerializer(serializers.ModelSerializer):
#     products = ProductSerializer(read_only=True,many=True)
#     name = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Program
#         fields = ('id', 'products', 'name')
#     def get_name(self, obj):
#         return f"{obj.direction_id.code} {obj.direction_id.name} {obj.profile} ({obj.level_id.name})"
