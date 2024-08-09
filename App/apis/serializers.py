from rest_framework import serializers, status
from django.contrib.auth.hashers import make_password, check_password
from App.models import *
from django.utils import timezone



class RegistrationSerializer(serializers.ModelSerializer):
    agent_executive_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Userprofile
        fields = ('name', 'phonenumber', 'user_location', 'role', 'email', 'agent_executive', 'agent_executive_id')

    def validate(self, data):
        if data['role'] == 'agent':
            if not data.get('agent_executive_id'):
                raise serializers.ValidationError("Agent executive ID must be provided if the role is 'agent'")
            
            try:
                executive = Userprofile.objects.get(pk=data['agent_executive_id'], role='executive')
                data['agent_executive'] = executive.name
            except Userprofile.DoesNotExist:
                raise serializers.ValidationError("The specified executive does not exist")
        
        return data

    def create(self, validated_data):  # Remove the agent_executive_id from validated_data
        created_date = timezone.now().strftime('%d-%m-%Y')
        password = make_password(created_date)
        user = Userprofile.objects.create(
            name=validated_data['name'],
            phonenumber=validated_data['phonenumber'],
            user_location=validated_data['user_location'],
            role=validated_data['role'],
            email=validated_data['email'],
            agent_executive=validated_data.get('agent_executive')  
        )
        user.password = password
        user.save()
        return user
    


class LoginSerializer(serializers.Serializer):
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



class ChangePasswordSerializer(serializers.Serializer):
    id = serializers.CharField()
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        id = data.get('id')
        current_password = data.get('current_password')

        try:
            user = Userprofile.objects.get(pk=id)
        except Userprofile.DoesNotExist:
            raise serializers.ValidationError("User with this name does not exist.")

        if not check_password(current_password, user.password):
            raise serializers.ValidationError("Current password is not correct.")

        data['user'] = user
        return data

    def save(self, *kwargs):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        user.password = make_password(new_password)
        user.save()
        return user
    


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Userprofile
        fields = ['id', 'name', 'email', 'phonenumber', 'user_location', 'role', 'userID','agent_executive','created']
        read_only_fields = ['userID', 'created']


class UserEditDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = Userprofile
        fields = ("name", "email", "agent_executive","phonenumber", "id", "role", "user_location")


class ExecutiveNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Userprofile
        fields = ['id','name']

class SupplyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplyReport
        fields = ['SEname', 'BPcode', 'Date', 'SumofPv']


class TerritorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TerritoryCollectionReport
        fields = "__all__"

        
class AttendanceSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    class Meta:
        model = Location
        fields = '__all__'

    def get_name(self, obj):
        return obj.user.name if obj.user else None
    
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Ensure that 'Date' is formatted as a date string
        representation['Date'] = instance.Date.strftime('%Y-%m-%d')
        return representation

class CollectionReportSerializer(serializers.ModelSerializer):
    executive_name = serializers.SerializerMethodField()

    class Meta:
        model = PaymentCollectionReport
        fields = "__all__"
    
    def get_executive_name(self, obj):
        return obj.Executive.name if obj.Executive else None
    
class AgentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentCollectionReport
        fields = "__all__"

class NetSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetSale
        fields = "__all__"

class PlantEditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantEdition
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['content', 'notification_image', 'role', 'title', 'status']

class ProfileSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Userprofile
        fields = ['id', 'name', 'email', 'phonenumber', 'user_location', 'role', 'created', 'userID','profile_image']
        read_only_fields = ['userID', 'created']


class UserprofilesaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Userprofile
        fields = ['id', 'name' , 'email', 'profile_image', 'phonenumber', 'user_location']
