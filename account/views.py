from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.conf import settings

from rest_framework import viewsets, generics, status, response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from .models import User
from .serializers import User_Serializer, Email_Serializer
from . import serializers

class User_register(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class =  User_Serializer
    http_method_names = ['post']

class Password_Reset(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.Email_Serializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        serializer.is_valid(raise_exception=True)

        email = serializer.data['email']
        user = User.objects.filter(email=email).first()
        if user:
            #gera o token
            encoded_pk = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)

            reset_url = reverse(
                "password-reset",
                kwargs = {'encoded_pk': encoded_pk, 'token': token}
            )

            reset_url = f"localhost:8000{reset_url}"
            
            #template do email
            context  = {
                'user': user,
                'reset_url': reset_url,
                'site_name': 'New Style',
            }

            plain_message = strip_tags(render_to_string('message_template_reset_password.html', context))

            #manda o token por email
            send_mail(
                subject='Redefinição de Senha - NewStyle',
                message= plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['vivi.emanuel05@gmail.com'],
                fail_silently=False,
            )

            return response.Response(
                {
                    'menssage':
                    'Link para resetar a senha foi enviado para o email'
                },
                status=status.HTTP_200_OK,
            )
        
        else:
            return response.Response(
                {
                    'mensage':
                    'Usuário não existe'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
class Reset_Password(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class =  serializers.Reset_Password_Serializer

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data = request.data, context = {'kwargs': kwargs}
        )

        serializer.is_valid(raise_exception=True)

        return response.Response(
            {
                'menssage': 
                'Reset da senha foi concluida'
            },
            status=status.HTTP_200_OK,

        )