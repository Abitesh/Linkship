from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserSerializer


from .models import User

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