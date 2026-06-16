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
    """Register a new customer account.

    Public endpoint used to create a user with the account serializer validation.
    Supports only POST and returns the created user payload on success.
    """
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class =  serializers.User_Serializer
    http_method_names = ['post']

class User_update(generics.RetrieveUpdateAPIView):
    """Retrieve and update the authenticated user's own profile.

    Requires authentication. Supports GET, PUT, and PATCH against the current
    user object returned by ``get_object``.
    """
    permission_classes = {IsAuthenticated}
    queryset = User.objects.all()
    serializer_class = serializers.User_update_Serializer
    http_method_names = ['get', 'put', 'patch']

    def get_object(self):
        """Return ``request.user`` so the route always targets the owner profile."""
        return self.request.user
    
class Address_Viewsets(viewsets.ModelViewSet):
    """Manage saved addresses for the authenticated customer.

    Customers can create, update, list, and delete only their own addresses.
    Staff users can see every address record when the queryset is evaluated.
    """
    permission_classes = [IsCustomer]
    serializer_class = serializers.Address_Serializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        """List all addresses for staff or only the current customer's records."""
        queryset = Address.objects.all()
        user = self.request.user

        if user.is_staff:
            return queryset
        
        return queryset.filter(user=user) 

    def perform_create(self, serializer):
        """Save the new address linked to the authenticated user."""
        serializer.save(user=self.request.user)


class Forgot_Password(generics.GenericAPIView):
    """Start the password reset flow by emailing a reset link.

    Anonymous POST endpoint that accepts an email address, generates a token,
    builds a reset URL, and sends the instructions by email when the user exists.
    """
    permission_classes = [AllowAny]
    serializer_class = serializers.Email_Serializer

    def post(self, request):
        """Validate the email, create the reset token, and send the email."""
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
    """Complete the password reset flow using the token and encoded user id.

    Anonymous PATCH endpoint that receives the password pair and uses the URL
    token data to verify the user before saving the new password.
    """
    permission_classes = [AllowAny]
    serializer_class =  serializers.Reset_Password_Serializer

    def patch(self, request, *args, **kwargs):
        """Validate the reset token and persist the new password."""
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
    """Manage stored payment cards for the authenticated customer.

    Authenticated customers can list, create, update, and delete only their own
    cards. The user relation is injected automatically on create.
    """
    permission_classes = [IsCustomer, IsAuthenticated]
    serializer_class = serializers.Card_Serializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        """Return only card records that belong to the current user."""
        queryset = card.objects.all()
        return queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Attach the authenticated user to the card before saving it."""
        serializer.save(user=self.request.user)
    