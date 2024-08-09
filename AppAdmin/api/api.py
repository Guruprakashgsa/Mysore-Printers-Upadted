from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from App.models import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.permissions import BasePermission
from backend.permissions import *
from AppAdmin.api.serializers import *
from datetime import timedelta,datetime
from django.db.models.functions import ExtractMonth, ExtractYear
import calendar
from django.db.models import Sum
from django.utils import timezone
import pandas as pd
from collections import defaultdict
from django.http import JsonResponse
from django.conf import settings
import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import os
from dotenv import load_dotenv
from django.shortcuts import get_object_or_404

load_dotenv()


@api_view(['POST'])
@permission_classes([IsAuthenticatedAndInAdminGroup])
def Registration(request):
    if request.method == 'POST':
        email = request.data.get('email')
        serializer = RegistrationSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token


            return Response({
                'refresh': str(refresh),
                'access': str(access),
                'name': user.name,
                'email': user.email,
                'phonenumber': user.phonenumber,
                'user_location': user.user_location,
                'role': user.role,
                'executive_name': user.agent_executive,
                'id':user.pk
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticatedAndInAdminGroup])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({'detail': 'Password updated successfully'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticatedAndInAdminGroup])
def Admin_Dashboard(request):
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
        end_date = timezone.now()
        
        # Calculate start_date based on months
        start_date = end_date.replace(day=1)
        for _ in range(months - 1):
            start_date = (start_date - timedelta(days=1)).replace(day=1)
        
        # Get total collections
        total_collections = PaymentCollectionReport.objects.aggregate(total_collected=Sum('AmountCollected'))['total_collected'] or 0
        
        # Get net sales data
        net_sales = NetSale.objects.filter(Date__range=(start_date, end_date))
        net_sales = net_sales.annotate(
            month=ExtractMonth('Date'),
            year=ExtractYear('Date')
        ).values('year', 'month').annotate(total_net_sales=Sum('Total_net_sales')).order_by('year', 'month')
        
        monthly_sales_data = {}
        current_date = start_date
        while current_date <= end_date:
            month_key = current_date.strftime('%m-%Y')
            monthly_sales_data[month_key] = 0
            current_date = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)

        for sale in net_sales:
            month_key = f'{sale["month"]:02d}-{sale["year"]}'
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
        
        # Calculate percentage change
        if previous_month_collections > 0:
            percentage_change = ((current_month_collections - previous_month_collections) / previous_month_collections) * 100
        else:
            percentage_change = 0
        
        response_data = {
            'total_employee': Userprofile.objects.count(),
            'total_collections': total_collections,
            'monthly_sales': monthly_sales_data,
            'monthly_collection': {
                'current_month_collections': current_month_collections,
                'previous_month_collections': previous_month_collections,
                'percentage_change': round(percentage_change, 2)  # Round to 2 decimal places
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticatedAndInAdminGroup])
def lists(request):
    if request.method == 'GET':
        users = Userprofile.objects.exclude(role='admin')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
@api_view(['GET'])
@permission_classes([IsAuthenticatedAndInAdminGroup])
def user_edit_data(request):
    id = request.GET.get("id")
    
    if not id:
        return Response({'error': 'ID parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = Userprofile.objects.get(pk=id)
    except Userprofile.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserEditDataSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedAndInAdminGroup])
def user_detail(request):

    try:
        id = request.data.get('id')
        user = Userprofile.objects.get(pk=id)
    except Userprofile.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PATCH':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        user.delete()
        return Response({'detail': 'User data deleted successfully'},status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticatedAndInAdminGroup])
def executivelists(request):
    try:
        executives = Userprofile.objects.filter(role='executive')
        serializer = ExecutiveNameSerializer(executives, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
@permission_classes([IsAuthenticatedAndInAdminGroup])
def location_list(request): 
     if request.method == 'GET':
        locations = Location.objects.all()
        serializer = AttendanceSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
     


@api_view(['POST'])
@permission_classes([IsAuthenticatedAndInAdminGroup])
def upload_file(request):
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    uploaded_file = request.FILES['file']
    file_name = uploaded_file.name.lower()
    filetype = request.data.get('filetype')

    try:
        if file_name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif file_name.endswith('.xls'):
            df = pd.read_excel(uploaded_file)
        elif file_name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            return JsonResponse({'error': 'Unsupported file format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

    if  filetype == 'supplyreport':
        return handle_sales_report(df)
    elif filetype == 'totalcollection':
        return handle_total_collection(df)
    elif filetype == 'netsale':
        return handle_netsale(df)
    elif filetype == 'territorycollection':
        return handle_territorycollection(df)
    else:
        return JsonResponse({'error': 'Unrecognized filetype name'}, status=400)

def handle_sales_report(df):
    try:
        for _, row in df.iterrows():
            SupplyReport.objects.create(
                ManagerName=row['Manager_Name'],      
                RegionalManager=row['Regional_Manager'],
                SEname=row['SE_Name'],
                BPcode=row['BP_Code'],
                Date=row['Date'],
                SumofPv=row['Sum_of_PV_Total']
            )
        return JsonResponse({'message': 'Supply report data uploaded successfully'}, status=201)
    except Exception as e:
        return JsonResponse({'error': f'File missing column name: {str(e)}'}, status=400)


def handle_territorycollection(df):
    try:
        for _, row in df.iterrows():
            TerritoryCollectionReport.objects.create(
                Executive=row['Executive'],      
                Territory=row['Territory'],
                SalesEmployee=row['SalesEmployee'],
                TotalDues=row['TotalDues'],
                Balance=row['Balance'],
                Collected=row['Collected'],
                Collection=row['Collection']
            )
        return JsonResponse({'message': 'Territory report data uploaded successfully'}, status=201)
    except Exception as e:
        return JsonResponse({'error': f'File missing column name: {str(e)}'}, status=400)
    

    
def handle_netsale(df):
    try:
        for _, row in df.iterrows():
            NetSale.objects.create(
                Manager=row['Manager'],
                AgentName=row['AgentName'],
                Territory=row['Territory'],
                DropPoint=row['DropPoint'],
                Total_net_sales=row['Total_net_sales'],
                Executive=row['Executive'],
                Publication=row['Publication'],
                Date = row['Date']
            )
        return JsonResponse({'message': 'netsale collection data uploaded successfully'}, status=201)
    except Exception as e:
        return JsonResponse({'error': f'File missing column name: {str(e)}'}, status=400)

def handle_total_collection(df):
    try:
        for _, row in df.iterrows():
            AgentCollectionReport.objects.create(
                agent=row['Agent'],
                month=row['Month'],
                bill_amount=row['Bill_Amount'],
                other_adjustment=row['Other_Adjustment'],
                amount_collected=row['Amount_Collected'],
                total_dues=row['Total_Dues'],
                balance_amount=row['Balance_Amount'],
                executive=row['Executive']
            )
        return JsonResponse({'message': 'Agentcollectionreport data uploaded successfully'}, status=201)
    except Exception as e:
        return JsonResponse({'error': f'File missing column name: {str(e)}'}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def daily_summary(request):
    datas = daily_working_summary.objects.all()
    serializer =  DailyWorkingSummarySerializer(datas , many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticatedAndInAdminGroup]) 
def admin_collection_list(request):

    try:
        payment_data = PaymentCollectionReport.objects.all()

        if payment_data.exists():
            serializer = CollectionReportSerializer(payment_data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No active data found'}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
@permission_classes([IsAuthenticatedAndInAdminorExecutiveGroup]) 
def supply_report_list(request):
    reports = SupplyReport.objects.all()
    serializer = SupplyReportSerializer(reports, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticatedAndInAdminGroup])
def admin_collection_data(request):
    datas = AgentCollectionReport.objects.all()
    serializer = AgentReportSerializer(datas, many=True)
    return Response (serializer.data, status= status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticatedAndInAdminorExecutiveGroup])
def netsales(request):
    period = request.GET.get('period', "6")  
    months = int(period)
    end_date = datetime.now()
    
    # Calculate start_date based on the period
    start_date = end_date.replace(day=1)
    for _ in range(months - 1):
        start_date = (start_date - timedelta(days=1)).replace(day=1)

    
    net_sales = NetSale.objects.filter(Date__range=(start_date, end_date))
    net_sales = net_sales.annotate(
        month=ExtractMonth('Date'),
        year=ExtractYear('Date')
    ).values('year', 'month').annotate(total_net_sales=Sum('Total_net_sales')).order_by('year', 'month')
    
    # Prepare monthly sales data
    monthly_sales_data = {}
    current_date = start_date
    while current_date <= end_date:
        month_key = current_date.strftime('%m-%Y')  # Format as MM-YYYY
        monthly_sales_data[month_key] = 0
        current_date = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)

    for sale in net_sales:
        month_key = f"{sale['month']:02d}-{sale['year']}"
        monthly_sales_data[month_key] = sale['total_net_sales']
    
    serializer = NetSaleSerializer(NetSale.objects.all(), many=True)
    
    return Response(
        {   
            'net_sale_data': serializer.data,
            'monthly_sales_data': monthly_sales_data
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_plant_edition(request):

    plant_editions = PlantEdition.objects.all()
    if not plant_editions.exists():
        return Response({'error': 'No LVD Data found '}, status=status.HTTP_404_NOT_FOUND)

    serializer = PlantEditionSerializer(plant_editions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticatedAndInAdminorExecutiveGroup])
def ProfileSettingView(request):
    try:
        pk = request.GET.get("id")
        user_profile = get_object_or_404(Userprofile, pk=pk)
        serializer = ProfileSettingSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def ProfileSave(request):
    try:
        user = request.data.get("id")
    
        user_data = get_object_or_404(Userprofile, pk=user)
       
        serializer = UserprofilesaveSerializer(user_data, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticatedAndInAdminGroup])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({'detail': 'Password updated successfully'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Notifications_web(request):
    datas = Notification.objects.all()
    serializer = NotificationSerializer(datas, many =True)
    return Response(serializer.data, status= status.HTTP_200_OK)



def get_recipient_fcm_tokens( recipient_type):
        if recipient_type == 'all users':
            users = Userprofile.objects.filter(fcm_token__isnull=False)
            return [user.fcm_token for user in users]
        
        else:
            return []

def get_access_token():
    """Retrieve a valid access token that can be used to authorize requests.    
    :return: Access token.
    """
    credentials = service_account.Credentials.from_service_account_file(settings.GOOGLE_APPLICATION_CREDENTIALS, scopes=['https://www.googleapis.com/auth/firebase.messaging'])
    request = Request()
    credentials.refresh(request)
    return credentials.token

def send_fcm_notification(tokens, title, body, image):
    access_token = get_access_token()
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json; UTF-8',
    }
    payload = {
        "message": {
            "notification": {
                "title": title,
                "body": body,
                "image": image
            }
        }
    }
    results = []
    for token in tokens:
        payload["message"]["token"] = token
        response = requests.post(settings.FCM_URL, headers=headers, json=payload)
        if response.status_code == 200:
            results.append({"token": token, "status": "success"})
        else:
            results.append({"token": token, "status": "failed", "response": response.text})
            # Log the error response
            print(f"Failed to send notification to {token}: {response.status_code} - {response.text}")
    return results


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def NotificationsFCMHTTP(request):
    if request.method == 'GET':
        notifications = Notification.objects.all()
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            notification_status = serializer.validated_data.get("status", "pending")
            if notification_status != "pending":
                title = serializer.validated_data.get('title', 'No Title')
                body = serializer.validated_data.get('content', 'No Body')
                recipient = serializer.validated_data.get('role')
                recipient_tokens = get_recipient_fcm_tokens(recipient)

                if recipient_tokens:
                    
                    notification = serializer.save()
                    image = request.build_absolute_uri(notification.image.url)  

                    result = send_fcm_notification(recipient_tokens, title, body, image)

                    return Response({"detail": "Notification sent successfully!"}, status=status.HTTP_200_OK)
                return Response({"detail": "No user found"}, status=status.HTTP_400_BAD_REQUEST)

            # Save the notification as pending
            serializer.save()
            return Response({"detail": "Notification added successfully"}, status=status.HTTP_201_CREATED)
        return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)