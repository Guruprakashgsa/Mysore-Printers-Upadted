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



class CollectionReportSerializer(serializers.ModelSerializer):
    executive_name = serializers.SerializerMethodField()

    class Meta:
        model = PaymentCollectionReport
        fields = "__all__"
    
    def get_executive_name(self, obj):
        return obj.Executive.name if obj.Executive else None
    
class SupplyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplyReport
        fields = ['SEname', 'BPcode', 'Date', 'SumofPv']


class AgentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentCollectionReport
        fields = "__all__"


class DailyWorkingSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = daily_working_summary
        fields = "__all__" 

class NetSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetSale
        fields = "__all__"


class ProfileSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Userprofile
        fields = ['id', 'name', 'email', 'phonenumber', 'user_location', 'role', 'created', 'userID','profile_image']
        read_only_fields = ['userID', 'created']


class UserprofilesaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Userprofile
        fields = ['id', 'name' , 'email', 'profile_image', 'phonenumber', 'user_location']