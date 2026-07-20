from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserSerializer


from .models import User

from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm 
from .forms import UserRegisterForm

def get_tokens_for_user(user: User) -> dict:
    """
    Helper: generate refresh + access tokens for a given user.
    """
    refresh = RefreshToken.for_user(user)  # SimpleJWT helper[web:223][web:229]
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(APIView):
    """
    POST /api/auth/register/

    Registers a new user and returns:
    - user data
    - JWT access + refresh tokens
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        user_data = UserSerializer(user).data
        tokens = get_tokens_for_user(user)

        return Response(
            {
                'user': user_data,
                'tokens': tokens,
            },
            status=status.HTTP_201_CREATED,
        )
    
# --- HTML WEB VIEWS ---
def register(request):
    # This will render the HTML registration form later
    return render(request, 'users/register.html', {'title': 'Register'})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'title': 'Profile'
    }
    return render(request, 'users/profile.html', context)

def logout_view(request):
    """
    Safely terminates the user session and redirects to the home page.
    """
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('links-home')

from .models import Profile

@login_required
def profile(request):
    # Use get_or_create to ensure the profile exists
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile) # Use the 'profile' variable
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile) # Use the 'profile' variable

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'title': 'Profile'
    }
    return render(request, 'users/profile.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in, {username}!')
            return redirect('login') # Ensure you have a 'login' URL name defined
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})