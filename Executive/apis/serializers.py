from App.models import *
from rest_framework import serializers


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


class AgentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentCollectionReport
        fields = "__all__"


class TerritorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TerritoryCollectionReport
        fields = "__all__"


class SupplyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplyReport
        fields = ['SEname', 'BPcode', 'Date', 'SumofPv']

