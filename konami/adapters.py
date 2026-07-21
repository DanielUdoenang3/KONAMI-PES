from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.models import User

def is_admin_user(user):
    """
    Helper to check if a user is an admin by is_staff, is_superuser,
    or profile role == 'admin'.
    """
    if user.is_staff or user.is_superuser:
        return True
    if hasattr(user, 'profile') and user.profile and user.profile.role == 'admin':
        return True
    return False

class CustomAccountAdapter(DefaultAccountAdapter):
    def pre_login(self, request, user, **kwargs):
        if is_admin_user(user):
            messages.error(
                request, 
                "Admin and Staff accounts cannot log in as regular users. Please sign in via the Admin portal."
            )
            raise ImmediateHttpResponse(redirect("staff_login"))
        return super().pre_login(request, user, **kwargs)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        email = sociallogin.account.extra_data.get('email') or user.email
        
        if email:
            try:
                db_user = User.objects.get(email=email)
                if is_admin_user(db_user):
                    messages.error(
                        request, 
                        "This Google account is associated with an Admin profile and cannot log in as a regular user."
                    )
                    raise ImmediateHttpResponse(redirect("staff_login"))
            except User.DoesNotExist:
                pass
                
        return super().pre_social_login(request, sociallogin)
