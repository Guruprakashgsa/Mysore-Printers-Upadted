from App.models import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken


@api_view(['POST'])
def app_user_login(request):
    if request.method == 'POST':
        serializer = AppUserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            fcm_token = request.data.get('fcm_token')
            if fcm_token:
                user.fcm_token = fcm_token
                user.save()

            return Response({
                'refresh': str(refresh),
                'access': str(access),
                'name': user.name,
                'email': user.email,
                'phonenumber': user.phonenumber,
                'user_location': user.user_location,
                'role': user.role,
                'user_id': user.id,
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)