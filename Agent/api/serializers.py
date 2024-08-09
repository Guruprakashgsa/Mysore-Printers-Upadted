from rest_framework import serializers, status
from App.models import *
from django.contrib.auth.hashers import make_password, check_password
 

class AppUserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()


    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        try:
            user = Userprofile.objects.get(email=email)
        except Userprofile.DoesNotExist:
            raise serializers.ValidationError({'error': 'User does not exist.'}, code=status.HTTP_404_NOT_FOUND)

        if not check_password(password, user.password):
            raise serializers.ValidationError({'error': 'Invalid credentials.'}, code=status.HTTP_401_UNAUTHORIZED)
        attrs['user'] = user
        return attrs
    
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class ProfileSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Userprofile
        fields = ['id', 'name', 'email', 'phonenumber', 'user_location', 'role', 'created', 'userID','profile_image']
        read_only_fields = ['userID', 'created']


class UserprofilesaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Userprofile
        fields = ['id', 'name' , 'email', 'profile_image', 'phonenumber', 'user_location']
