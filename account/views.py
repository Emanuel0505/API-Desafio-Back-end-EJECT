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

from .models import User, Address, card
from . import serializers
from ecommerce.permissions import IsCustomer

class User_register(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class =  serializers.User_Serializer
    http_method_names = ['post']

class User_update(generics.RetrieveUpdateAPIView):
    permission_classes = {IsAuthenticated}
    queryset = User.objects.all()
    serializer_class = serializers.User_update_Serializer
    http_method_names = ['get', 'put', 'patch']

    def get_object(self):
        return self.request.user
    
class Address_Viewsets(viewsets.ModelViewSet):
    permission_classes = [IsCustomer]
    serializer_class = serializers.Address_Serializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        queryset = Address.objects.all()
        user = self.request.user

        if user.is_staff:
            return queryset
        
        return queryset.filter(user=user) 

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class Forgot_Password(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.Email_Serializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        serializer.is_valid(raise_exception=True)

        email = serializer.data['email']
        user = User.objects.filter(email=email).first()
        if user:
            # generates the token
            encoded_pk = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)

            reset_url = reverse(
                "password-reset",
                kwargs = {'encoded_pk': encoded_pk, 'token': token}
            )

            reset_url = f"localhost:8000{reset_url}"
            
            # email template
            context  = {
                'user': user,
                'reset_url': reset_url,
                'site_name': 'New Style',
            }

            plain_message = strip_tags(render_to_string('message_template_reset_password.html', context))

            # sends the token via email
            send_mail(
                subject='Password Reset - NewStyle',
                message= plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email,],
                fail_silently=False,
            )

            return response.Response(
                {
                    'message':
                    'Link to reset password has been sent to email'
                },
                status=status.HTTP_200_OK,
            )
        
        else:
            return response.Response(
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
                'message': 
                'Password reset has been completed'
            },
            status=status.HTTP_200_OK,

        )
    
class Card_viewset(viewsets.ModelViewSet):
    permission_classes = [IsCustomer, IsAuthenticated]
    serializer_class = serializers.Card_Serializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        queryset = card.objects.all()
        return queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    