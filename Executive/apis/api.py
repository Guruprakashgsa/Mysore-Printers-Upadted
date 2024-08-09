import Agent
from App.apis.serializers import AttendanceSerializer
from App.models import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
import Executive
from backend.permissions import *
from django.db.models.functions import ExtractMonth, ExtractYear
from datetime import timedelta,datetime
import calendar
from django.db.models import Sum
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

@api_view(['GET'])
@permission_classes([IsAuthenticatedAndInAdminorExecutiveGroup])
def executive_working_summary(request):
    user_id = request.GET.get('id')
    period = request.GET.get('period', "6")
    
    if not all([user_id, period]):
        return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = Userprofile.objects.get(pk=user_id)
    except Userprofile.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        months = int(period)
        end_date = datetime.now()
        
        start_date = end_date.replace(day=1)
        for _ in range(months - 1):
            start_date = (start_date - timedelta(days=1)).replace(day=1)
        
        locations = Location.objects.filter(user=user, check_in_time__range=(start_date, end_date))
        total_employees = Userprofile.objects.count()
        total_collections = PaymentCollectionReport.objects.aggregate(total_collected=Sum('AmountCollected'))['total_collected'] or 0
        
        net_sales = NetSale.objects.filter(Date__range=(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        net_sales = net_sales.annotate(
            month=ExtractMonth('Date'),
            year=ExtractYear('Date')
        ).values('year', 'month').annotate(total_net_sales=Sum('Total_net_sales')).order_by('year', 'month')
        
        monthly_sales_data = {}
        current_date = start_date
        while current_date <= end_date:   
            month_key = calendar.month_abbr[current_date.month]
            monthly_sales_data[month_key] = 0
            current_date = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)  

        for sale in net_sales:
            month_key = calendar.month_abbr[sale['month']]
            monthly_sales_data[month_key] = sale['total_net_sales']

        # Calculate monthly collections for the current month and the previous month
        current_month_start = end_date.replace(day=1)
        previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        previous_month_end = current_month_start - timedelta(days=1)
        
        current_month_collections = PaymentCollectionReport.objects.filter(
            Date__range=(current_month_start, end_date)
        ).aggregate(monthly_collected=Sum('AmountCollected'))['monthly_collected'] or 0

        previous_month_collections = PaymentCollectionReport.objects.filter(
            Date__range=(previous_month_start, previous_month_end)
        ).aggregate(monthly_collected=Sum('AmountCollected'))['monthly_collected'] or 0
        
        response_data = {
            'total_employee': total_employees,
            'total_collections': total_collections,
            'monthly_sales': monthly_sales_data,
            'montly_collection':{
                'current_month_collections': current_month_collections,
                'previous_month_collections': previous_month_collections,
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
"""""""""
@api_view(['GET'])
@permission_classes([IsAuthenticatedAndInAdminorExecutiveGroup])
def location_list(request): 
     if request.method == 'GET':
        Agent=Userprofile.objects.filter(agentexecutive=Executive)
        serializers=LocationSerializer (Agent, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
     
     """""""""
@api_view(['GET'])
@permission_classes([IsAuthenticatedAndInExecutiveGroup])
def list_locations_by_executive(request):
    try:
        executive_name = request.GET.get('id')
        print(executive_name)
        agents = Userprofile.objects.filter(agent_executive_id=executive_name, role='agent')

        if not agents.exists():
            return Response({'detail': 'No agents found for this executive.'}, status=status.HTTP_404_NOT_FOUND)

        locations = Location.objects.filter(user__in=agents)

        if not locations.exists():
            return Response({'detail': 'No locations found for agents managed by this executive.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


@api_view(['GET'])
@permission_classes([IsAuthenticatedAndInAdminorExecutiveGroup])
def collection_list(request):
  
    user = request.GET.get('id')
    try:
        collection = Userprofile.objects.get(pk = user)

        payment_data = PaymentCollectionReport.objects.filter(Executive=collection)

        if payment_data.exists():
            serializer = CollectionReportSerializer(payment_data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No active data found for this user'}, status=status.HTTP_404_NOT_FOUND)
    
    except PaymentCollectionReport.DoesNotExist:
        return Response({'error': 'No active data found for this user'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
@permission_classes([IsAuthenticatedAndInAdminorExecutiveGroup])
def executive_collection_agent_report(request):
    user = request.GET.get('name')
    if not user:
        return Response({'error': 'Name parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
       
        data = AgentCollectionReport.objects.filter(executive=user)
    except Exception as e:
        return Response({'error': f'Error retrieving data: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = AgentReportSerializer(data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticatedAndInAdminorExecutiveGroup])
def executive_collection_territory_report(request):
    executive_name = request.GET.get('executive_name')
    print(executive_name)

    try:
        data = TerritoryCollectionReport.objects.filter(Executive = executive_name)
    except Exception as e:
        return Response({'error': f'Error creating payment data: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = TerritorySerializer(data, many=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticatedAndInAdminorExecutiveGroup]) #TODO
def supply_report_list(request):
    reports = SupplyReport.objects.all()
    serializer = SupplyReportSerializer(reports, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)