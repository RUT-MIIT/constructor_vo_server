# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import NsiType, Ministry, Nsi, Program, EducationLevel, Direction, ProgramRole, ProgramUser
from .serializers import NsiTypeSerializer, MinistrySerializer, NsiSerializer, EducationLevelSerializer, \
    EducationDirectionSerializer, ProgramRoleSerializer, ProgramInformationSerializer, ProgramSerializer, \
    ProgramUserSerializer
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.decorators import action


User = get_user_model()


class NsiTypeViewSet(viewsets.ModelViewSet):
    queryset = NsiType.objects.filter(active=True).order_by('name')
    serializer_class = NsiTypeSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        # data.insert(0, data.pop())
        return Response(data)


class MinistryViewSet(viewsets.ModelViewSet):
    queryset = Ministry.objects.all()
    serializer_class = MinistrySerializer


class NsiViewSet(viewsets.ModelViewSet):
    queryset = Nsi.objects.all()
    serializer_class = NsiSerializer

    def get_queryset(self):
        program_id = self.kwargs['program_id']
        return Nsi.objects.filter(program_id=program_id)

    def create(self, request, *args, **kwargs):
        nsi_data = request.data['nsi']
        program_id = kwargs.get('program_id')
        author = self.request.user
        try:
            program = Program.objects.get(pk=program_id)
        except Program.DoesNotExist:
            raise ValidationError(f'Program with id {program_id} does not exist')

        nsi_data['program'] = program_id

        serializer = self.get_serializer(data=nsi_data)
        serializer.is_valid(raise_exception=True)
        serializer.save(program=program, author=author)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        program_id = self.kwargs['program_id']
        nsi_data = request.data.get('nsi', {})

        try:
            program = Program.objects.get(pk=program_id)
        except Program.DoesNotExist:
            raise ValidationError(f'Program with id {program_id} does not exist')

        serializer = self.get_serializer(instance, data=nsi_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(program=program)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EducationLevelListView(generics.ListAPIView):
    queryset = EducationLevel.objects.all()
    serializer_class = EducationLevelSerializer


class EducationDirectionListView(generics.ListAPIView):
    queryset = Direction.objects.all()
    serializer_class = EducationDirectionSerializer


class ProgramRoleListView(generics.ListAPIView):
    queryset = ProgramRole.objects.all()
    serializer_class = ProgramRoleSerializer


class ProgramInformationView(generics.RetrieveAPIView):
    queryset = Program.objects.prefetch_related('participants')
    serializer_class = ProgramInformationSerializer



class MyProgramsListView(generics.ListAPIView):
    serializer_class = ProgramInformationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        return Program.objects.filter(
            participants__user_id=user_id).prefetch_related('participants').select_related('direction_id').select_related('level_id')

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
        }


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Получить список программ.
        """
        queryset = self.get_queryset().prefetch_related('participants')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        program = self.get_object()
        serializer = self.get_serializer(program)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data['program'])
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        user_id = get_object_or_404(User, id=request.user.id)
        role_id = get_object_or_404(ProgramRole, id=1)
        program_id = serializer.instance
        ProgramUser.objects.create(program_id=program_id, user_id=user_id,
                                   role_id=role_id)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def partial_update(self, request, pk=None):
        program = self.get_object()
        data = request.data.get('program')
        serializer = self.get_serializer(program, data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        program = self.get_object()
        object_id = program.id
        program.delete()
        return Response({'message': 'Успешно удалено', 'id':object_id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], name='Add Participant')
    def add_participant(self, request, pk=None):
        program = self.get_object()
        data = request.data.get('participant', {})

        user_id = get_object_or_404(User, id=data.get('user_id'))
        role_id = get_object_or_404(ProgramRole, id=data.get('role_id'))

        # Проверяем, существует ли уже участник с такой ролью в программе
        if ProgramUser.objects.filter(program_id=program,
                                      user_id=user_id).exists():
            return Response(
                {'error': 'Пользователь уже имеет роль в этой программе.'},
                status=status.HTTP_400_BAD_REQUEST)

        ProgramUser.objects.create(program_id=program, user_id=user_id,
                                   role_id=role_id)

        program_users = ProgramUser.objects.filter(program_id=program)
        serializer = ProgramUserSerializer(program_users, many=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'],
            url_path='remove_participant/(?P<participant_id>[^/.]+)',
            name='Remove Participant')
    def remove_participant(self, request, pk=None, participant_id=None):
        program = self.get_object()
        # Здесь должна быть логика проверки, что пользователь может удалять участников

        ProgramUser.objects.filter(program_id=program,
                                   user_id=participant_id).delete()
        program_users = ProgramUser.objects.filter(program_id=program)
        serializer = ProgramUserSerializer(program_users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], name='Update Participant')
    def update_participant(self, request, pk=None):
        program = self.get_object()
        data = request.data.get('participant', {})

        user_id = get_object_or_404(User, id=data.get('user_id'))
        role_id = get_object_or_404(ProgramRole, id=data.get('role_id'))

        ProgramUser.objects.update_or_create(
            program_id=program, user_id=user_id,
            defaults={'role_id': role_id}
        )

        program_users = ProgramUser.objects.filter(program_id=program)
        serializer = ProgramUserSerializer(program_users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # @action(detail=True, methods=['get'], url_path='products_data')
    # def products_data (self, request, pk=None):
    #     program = self.get_object()
    #     products = Product.objects.filter(program_id=program).prefetch_related('stages__processes__results')
    #     context = {'stages': True, 'processes': True}
    #     serializer = ProductSerializer(products, many=True, context=context)
    #
    #     return Response(serializer.data)