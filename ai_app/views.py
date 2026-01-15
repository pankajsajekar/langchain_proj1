from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class login_view(APIView):

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)

        refresh = RefreshToken.for_user(user)

        response_data = {
            "username": username,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

        if user is not None:
            return Response(response_data, status=200)
        else:
            return Response({"message": "Invalid credentials"}, status=401)