import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from programs.models import EducationLevel, Direction, Program, ProgramRole, \
    ProgramUser, MultiplicityType, Competence, Discipline
from programs.models import NsiType, Ministry, Nsi, Product, Step, LifeStage, Process
from users.serializers import UserShortSerializer

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
        fields = ['user', 'role', 'program_id']


class ProgramSerializer(serializers.ModelSerializer):
    direction = EducationDirectionSerializer(source='direction_id', read_only=True)
    level = EducationLevelSerializer(source='level_id', read_only=True)
    participants = ProgramUserSerializer(many=True, read_only=True)
    authorId = serializers.IntegerField(source='author_id', read_only=True)
    my_role = serializers.SerializerMethodField()
    form = serializers.CharField(required=True)

    name = serializers.SerializerMethodField()

    fgos_file = serializers.DictField(write_only=True, required=False)
    fgos_url = serializers.FileField(source='fgos_file', read_only=True)

    class Meta:
        model = Program
        fields = (
            'id', 'profile', 'annotation', 'level', 'direction', 'form', 'participants', 'my_role', 'authorId',
            'fgos_file', 'fgos_url', 'name'
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
        allowed_extensions = ['txt', 'pdf', 'jpg', 'png', 'docx']  # Допустимые форматы
        if ext.lower() not in allowed_extensions:
            raise serializers.ValidationError(
                f"Недопустимое расширение файла: {ext}. Допустимые форматы: {', '.join(allowed_extensions)}"
            )

        # Создаем объект файла
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

    def get_name(self, obj):
        return f"{obj.direction_id.code} {obj.direction_id.name} {obj.profile} ({obj.level_id.name})"

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
            'id', 'profile', 'form', 'annotation', 'participants', 'direction', 'level', 'name', 'authorId', 'my_role',
            'fgos_url')

    def get_name(self, obj):
        return f"{obj.direction_id.code} {obj.direction_id.name} {obj.profile} ({obj.level_id.name})"

    def get_my_role(self, obj):
        user_id = self.context['request'].user.id
        roles = ProgramUser.objects.filter(user_id=user_id)
        name = roles.first().role_id.name if roles.exists() else ''
        return name


class StepSerializer(serializers.ModelSerializer):
    step_type_name = serializers.CharField(source='step_type.name', read_only=True)
    step_type_code = serializers.CharField(source='step_type.code', read_only=True)
    step_type_position = serializers.IntegerField(source='step_type.position', read_only=True)

    class Meta:
        model = Step
        fields = ['id', 'step_type_name', 'step_type_code', 'step_type_position', 'created_at', 'chunks', 'result',
                  'result_json']


class ProductSerializer(serializers.ModelSerializer):
    position = serializers.IntegerField(read_only=True)
    program = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Program.objects.all())
    nsis = serializers.PrimaryKeyRelatedField(many=True, queryset=Nsi.objects.all(), required=False)

    class Meta:
        model = Product
        fields = ('id', 'name', 'position', 'description', 'program', 'nsis')



class ProcessRDSerializer(serializers.ModelSerializer):
    position = serializers.IntegerField(read_only=True)
    product = serializers.IntegerField(read_only=True, source='stage.product.id')
    nsis = serializers.PrimaryKeyRelatedField(many=True, queryset=Nsi.objects.all(), required=False)

    class Meta:
        model = Process
        fields = ('id', 'name', 'stage', 'position', 'product', 'description', 'result','nsis')


class LifeStageRDSerializer(serializers.ModelSerializer):
    position = serializers.IntegerField(read_only=True)
    processes = ProcessRDSerializer(many=True, read_only=True)
    nsis = serializers.PrimaryKeyRelatedField(many=True, queryset=Nsi.objects.all(), required=False)

    class Meta:
        model = LifeStage
        fields = ('id', 'name', 'product', 'position', 'description', 'processes','nsis')


class ProductRDSerializer(serializers.ModelSerializer):
    position = serializers.IntegerField(read_only=True)
    program = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Program.objects.all())
    stages = LifeStageRDSerializer(many=True, read_only=True)
    nsis = serializers.PrimaryKeyRelatedField(many=True, queryset=Nsi.objects.all(), required=False)

    class Meta:
        model = Product
        fields = ('id', 'name', 'position', 'description', 'program', 'stages', 'nsis')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['stages'] = sorted(data['stages'], key=lambda x: x.get('position', 0))
        return data

class SyncNsiWithProductSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    nsis = serializers.PrimaryKeyRelatedField(queryset=Nsi.objects.all(), many=True)


class SyncNsiWithLifeStageSerializer(serializers.Serializer):
    stage_id = serializers.PrimaryKeyRelatedField(queryset=LifeStage.objects.all())
    nsis = serializers.PrimaryKeyRelatedField(queryset=Nsi.objects.all(), many=True)


class SyncNsiWithProcessSerializer(serializers.Serializer):
    process_id = serializers.PrimaryKeyRelatedField(queryset=Process.objects.all())
    nsis = serializers.PrimaryKeyRelatedField(queryset=Nsi.objects.all(), many=True)


class MultiplicityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiplicityType
        fields = ['id', 'name', 'code', 'position']


class DisciplineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Discipline
        fields = '__all__'

class CompetenceSerializer(serializers.ModelSerializer):
    disciplines = DisciplineSerializer(many=True, read_only=True)
    class Meta:
        model = Competence
        fields = '__all__'



