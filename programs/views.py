# views.py
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import NsiType, Ministry, Nsi, Program, EducationLevel, Direction, ProgramRole, ProgramUser, Product, \
    LifeStage, Process, MultiplicityType, Competence, Discipline
from .serializers import NsiTypeSerializer, MinistrySerializer, NsiSerializer, EducationLevelSerializer, \
    EducationDirectionSerializer, ProgramRoleSerializer, ProgramInformationSerializer, ProgramSerializer, \
    ProgramUserSerializer, ProductSerializer, SyncNsiWithProductSerializer, ProductRDSerializer, LifeStageRDSerializer, \
    ProcessRDSerializer, SyncNsiWithLifeStageSerializer, SyncNsiWithProcessSerializer, MultiplicityTypeSerializer, \
    CompetenceSerializer, DisciplineSerializer

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
            participants__user_id=user_id).prefetch_related('participants').select_related(
            'direction_id').select_related('level_id')

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
        return Response({'message': 'Успешно удалено', 'id': object_id}, status=status.HTTP_200_OK)

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


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Переопределение метода для фильтрации продуктов по program_id.
        """
        program_id = self.kwargs.get('program_id')
        if program_id is not None:
            return Product.objects.filter(program_id=program_id).order_by('position').prefetch_related('nsis')
        return Product.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'kwargs': self.kwargs
        })
        return context

    def create(self, request, *args, **kwargs):
        product_data = request.data['product']
        program_id = kwargs.get('program_id')
        product_data['program'] = program_id
        queryset = self.get_queryset()
        position = queryset.count() + 1

        serializer = self.get_serializer(data=product_data)
        serializer.is_valid(raise_exception=True)
        serializer.save(position=position)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def partial_update(self, request, pk=None, *args, **kwargs):
        product = self.get_object()
        product_data = request.data['product']
        program_id = kwargs.get('program_id')
        product_data['program'] = program_id
        # program_id = kwargs.get('program_id')
        # product_data['program'] = program_id
        serializer = self.get_serializer(product, data=product_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        object_id = product.id
        position_to_update = product.position
        program = product.program
        self.perform_destroy(product)

        Product.objects.filter(
            position__gt=position_to_update,
            program=program
        ).update(position=F('position') - 1)

        return Response({'message': 'Успешно удалено', 'id': object_id}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='reorder')
    def reorder(self, request, program_id=None):
        products_order = request.data.get('products')
        with transaction.atomic():  # Используем атомарные транзакции для обеспечения консистентности
            for position, product_id in enumerate(products_order, start=1):
                Product.objects.filter(id=product_id).update(position=position)

        products = Product.objects.filter(id__in=products_order).order_by('position')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IshDataView(APIView):
    def get(self, request, program_id):
        # Получаем объект Program или возвращаем 404
        program = get_object_or_404(Program, id=program_id)

        # Получаем связанные продукты
        products = ProductSerializer(program.products.all(), many=True)
        # Формируем JSON-ответ
        return JsonResponse({
            "message": f"Products for program {program.profile}.",
            "products": products.data,
        }, status=200)


class RecDtView(APIView):
    def get(self, request, program_id):
        # Получаем объект Program или возвращаем 404
        program = get_object_or_404(Program, id=program_id)

        # Получаем связанные продукты
        products = ProductRDSerializer(
            program.products.all().prefetch_related(
                'nsis',  # Prefetch nsis for products
                'stages__nsis',  # Prefetch nsis for stages
                'stages__processes__nsis'  # Prefetch nsis for processes (если nsis связано с процессами)
            ),
            many=True
        )
        # Формируем JSON-ответ
        return JsonResponse({
            "message": f"Информация по этапу «Реконструкция деятельности» программы {program.id} - {program.profile}.",
            "products": products.data,
        }, json_dumps_params={'ensure_ascii': False}, status=status.HTTP_200_OK)


class PrOpdView(APIView):
    def get(self, request, program_id):
        # Получаем объект Program или возвращаем 404
        program = get_object_or_404(Program, id=program_id)

        # Получаем связанные продукты
        competences = CompetenceSerializer(
            program.competences.filter(type='Общепрофессиональные').prefetch_related(
                'disciplines',
            ),
            many=True
        )

        # Формируем JSON-ответ
        return JsonResponse({
            "message": f"Информация по этапу «Проектирование ОПД {program.id} - {program.profile}.",
            "competences": competences.data,
        }, json_dumps_params={'ensure_ascii': False}, status=status.HTTP_200_OK)


class SyncNsiWithProductView(APIView):
    def post(self, request, product_id):
        request.data["product_id"] = product_id
        serializer = SyncNsiWithProductSerializer(data=request.data)
        if serializer.is_valid():
            # Получаем данные из сериализатора
            product = serializer.validated_data['product_id']
            nsis = serializer.validated_data['nsis']
            # Синхронизируем Nsi: заменяем все текущие связи на новые
            product.nsis.set(nsis)

            updated_product = Product.objects.prefetch_related('nsis').get(id=product.id)
            serializer = ProductSerializer(updated_product)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SyncNsiWithLifeStageView(APIView):
    def post(self, request, stage_id):
        request.data["stage_id"] = stage_id
        serializer = SyncNsiWithLifeStageSerializer(data=request.data)
        if serializer.is_valid():
            # Получаем данные из сериализатора
            stage = serializer.validated_data['stage_id']
            nsis = serializer.validated_data['nsis']
            # Синхронизируем Nsi: заменяем все текущие связи на новые
            stage.nsis.set(nsis)

            updated_stage = LifeStage.objects.prefetch_related('nsis').get(id=stage.id)
            serializer = LifeStageRDSerializer(updated_stage)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LifeStageViewSet(viewsets.ModelViewSet):
    queryset = LifeStage.objects.all()
    serializer_class = LifeStageRDSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        queryset = LifeStage.objects.all()

        if product_id is not None:
            queryset = queryset.filter(product_id=product_id)

        return queryset.order_by('position')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'kwargs': self.kwargs
        })
        return context

    def create(self, request, *args, **kwargs):
        stage_data = request.data['stage']
        product_id = kwargs.get('product_id')
        stage_data['product'] = product_id
        queryset = self.get_queryset()
        position = queryset.count() + 1

        serializer = self.get_serializer(data=stage_data)
        serializer.is_valid(raise_exception=True)
        serializer.save(position=position)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def partial_update(self, request, pk=None, *args, **kwargs):
        stage = self.get_object()
        stage_data = request.data['stage']
        product_id = kwargs.get('product_id')
        stage_data['product'] = product_id

        serializer = self.get_serializer(stage, data=stage_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        stage = self.get_object()
        position_to_update = stage.position
        object_id = stage.id
        product = stage.product
        self.perform_destroy(stage)

        LifeStage.objects.filter(
            position__gt=position_to_update,
            product=product
        ).update(position=F('position') - 1)

        return Response({'message': 'Успешно удалено', 'id': object_id}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='reorder')
    def reorder(self, request, product_id=None):
        stages_order = request.data.get('stages')
        for stage_id in stages_order:
            get_object_or_404(LifeStage, id=stage_id)
        with transaction.atomic():
            for position, stage_id in enumerate(stages_order, start=1):
                LifeStage.objects.filter(id=stage_id).update(position=position)

        stages = LifeStage.objects.filter(id__in=stages_order).order_by('position')
        serializer = LifeStageRDSerializer(stages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProcessViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessRDSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        stage_id = self.kwargs.get('stage_id')
        if stage_id is not None:
            return Process.objects.filter(stage_id=stage_id).order_by('position')
        return Process.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'kwargs': self.kwargs})
        return context

    def create(self, request, *args, **kwargs):
        process_data = request.data['process']
        stage_id = kwargs.get('stage_id')
        process_data['stage'] = stage_id
        queryset = self.get_queryset()
        position = queryset.count() + 1

        serializer = self.get_serializer(data=process_data)
        serializer.is_valid(raise_exception=True)
        serializer.save(position=position)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def partial_update(self, request, pk=None, *args, **kwargs):
        process = self.get_object()
        process_data = request.data['process']
        stage_id = kwargs.get('stage_id')
        process_data['stage'] = stage_id

        serializer = self.get_serializer(process, data=process_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        process = self.get_object()
        object_id = process.id
        position_to_update = process.position
        stage = process.stage
        self.perform_destroy(process)

        Process.objects.filter(
            position__gt=position_to_update,
            stage=stage
        ).update(position=F('position') - 1)

        return Response({'message': 'Успешно удалено', 'id': object_id}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='reorder')
    def reorder(self, request, stage_id=None):
        processes_order = request.data.get('processes')
        for process_id in processes_order:
            get_object_or_404(Process, id=process_id)
        with transaction.atomic():
            for position, process_id in enumerate(processes_order, start=1):
                Process.objects.filter(id=process_id).update(position=position)

        processes = Process.objects.filter(id__in=processes_order).order_by('position')
        serializer = ProcessRDSerializer(processes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SyncNsiWithProcessView(APIView):
    def post(self, request, process_id):
        request.data["process_id"] = process_id
        serializer = SyncNsiWithProcessSerializer(data=request.data)
        if serializer.is_valid():
            # Получаем данные из сериализатора
            process = serializer.validated_data['process_id']
            nsis = serializer.validated_data['nsis']
            # Синхронизируем Nsi: заменяем все текущие связи на новые
            process.nsis.set(nsis)

            updated_process = Process.objects.prefetch_related('nsis').get(id=process.id)
            serializer = ProcessRDSerializer(updated_process)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MultiplicityTypesSerializer:
    pass


class MultiplicityTypesListView(ListAPIView):
    queryset = MultiplicityType.objects.all().order_by('position')
    serializer_class = MultiplicityTypeSerializer


class CompetenceViewSet(viewsets.ModelViewSet):
    serializer_class = CompetenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        program_id = self.kwargs.get('program_id')
        queryset = Competence.objects.filter(program_id=program_id).order_by(
            'position') if program_id else Competence.objects.all()
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['kwargs'] = self.kwargs
        return context

    def create(self, request, *args, **kwargs):
        program_id = kwargs.get('program_id')
        competence_data = request.data.get('competence', {})
        competence_data['program'] = program_id

        # Automatically set the next position
        competence_data['position'] = self.get_queryset().count() + 1

        serializer = self.get_serializer(data=competence_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def partial_update(self, request, *args, **kwargs):
        competence = self.get_object()
        serializer = self.get_serializer(competence, data=request.data.get('competence', {}), partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        competence = self.get_object()
        competence_id = competence.id
        program = competence.program
        position_to_update = competence.position

        self.perform_destroy(competence)

        # Reorder positions after deletion
        Competence.objects.filter(program=program, position__gt=position_to_update).update(position=F('position') - 1)

        return Response({'message': 'Успешно удалено', 'id': competence_id}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='reorder')
    def reorder(self, request, *args, **kwargs):
        competence_order = request.data.get('competences', [])
        if not competence_order:
            return Response({'error': 'Не указан порядок компетенций'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            for position, competence_id in enumerate(competence_order, start=1):
                Competence.objects.filter(id=competence_id).update(position=position)

        competences = Competence.objects.filter(id__in=competence_order).order_by('position')
        serializer = self.get_serializer(competences, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DisciplineViewSet(viewsets.ModelViewSet):
    serializer_class = DisciplineSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        program_id = self.kwargs.get('program_id')
        queryset = Discipline.objects.filter(program_id=program_id).order_by('type',
                                                                             'position') if program_id else Discipline.objects.all()
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['kwargs'] = self.kwargs
        return context

    def create(self, request, *args, **kwargs):
        program_id = kwargs.get('program_id')
        discipline_data = request.data.get('discipline', {})
        discipline_data['program'] = program_id

        # Automatically set the next position
        discipline_data['position'] = self.get_queryset().count() + 1

        serializer = self.get_serializer(data=discipline_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def partial_update(self, request, *args, **kwargs):
        discipline = self.get_object()
        serializer = self.get_serializer(discipline, data=request.data.get('discipline', {}), partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        discipline = self.get_object()
        discipline_id = discipline.id
        program = discipline.program
        position_to_update = discipline.position
        self.perform_destroy(discipline)

        # Reorder positions after deletion
        Discipline.objects.filter(program=program, position__gt=position_to_update).update(position=F('position') - 1)

        return Response({'message': 'Успешно удалено', 'id': discipline_id}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='reorder')
    def reorder(self, request, *args, **kwargs):
        disciplines_order = request.data.get('disciplines', [])
        if not disciplines_order:
            return Response({'error': 'Не указан порядок дисциплин'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            for position, discipline_id in enumerate(disciplines_order, start=1):
                Discipline.objects.filter(id=discipline_id).update(position=position)

        disciplines = Discipline.objects.filter(id__in=disciplines_order).order_by('position')
        serializer = self.get_serializer(disciplines, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
