from dj_rest_auth.serializers import TokenSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework.authtoken.models import Token
from dj_rest_auth.serializers import UserDetailsSerializer

from dj_rest_auth.serializers import PasswordResetSerializer as _PasswordResetSerializer
from allauth.account.adapter import get_adapter
from allauth.account.forms import ResetPasswordForm
from allauth.account.utils import user_pk_to_url_str
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()

class CustomTokenSerializer(TokenSerializer):
    token_type = serializers.CharField(source="get_token_type")

    def get_token_type(self, obj):
        return "Bearer"

    class Meta:
        model = Token
        fields = ('key', 'token_type')

class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    middle_name = serializers.CharField()
    email = serializers.EmailField(required=True)


    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def save(self, request):
        user = super().save(request)
        user.first_name = self.data.get('first_name')
        user.last_name = self.data.get('last_name')
        user.middle_name = self.data.get('middle_name')
        user.save()
        return user


class CustomUserDetailsSerializer(UserDetailsSerializer):
    id = serializers.IntegerField(source='pk')

    class Meta(UserDetailsSerializer.Meta):
        fields = ('id', 'email', 'first_name', 'last_name','middle_name', 'role')


class UserShortSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name')

    def get_name(self, obj):
        # Возвращает соединенные имя и фамилию
        return f"{obj.first_name} {obj.last_name}"


class PasswordResetSerializer(_PasswordResetSerializer):

    @property
    def password_reset_form_class(self):
        return CustomResetPasswordForm

    def get_email_options(self):

        return {
            'email_template_name': 'password/password_reset'
        }


class CustomResetPasswordForm(ResetPasswordForm):
    def save(self, request, **kwargs):
        email = self.cleaned_data['email']
        token_generator = kwargs.get('token_generator')
        template = kwargs.get("email_template_name")
        extra = kwargs.get("extra_email_context", {})
        # client_app = extra["client_app"]
        for user in self.users:
            uid = user_pk_to_url_str(user)
            token = token_generator.make_token(user)
            reset_url = f"{settings.FRONT_END}/reset_password/{uid}/{token}"
            context = {"user": user, "request": request, "email": email, "reset_url": reset_url}
            context.update(extra)
            get_adapter(request).send_mail(template, email, context)
        return email