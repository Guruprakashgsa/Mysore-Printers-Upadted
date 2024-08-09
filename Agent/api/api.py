from App.models import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from backend.permissions import *
from django.db.models.functions import ExtractMonth, ExtractYear
from datetime import timedelta,datetime
import calendar
from django.db.models import Sum
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
import pyrebase
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import pytz
from geopy.exc import GeocoderUnavailable
import time


@api_view(['POST'])
def app_user_login(request):
    if request.method == 'POST':
        serializer = AppUserLoginSerializer(data=request.data)
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
                'user_id': user.id,
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

def get_period_in_months(months):
    end_date = timezone.now()
    start_date = end_date.replace(day=1) - timedelta(days=months*30)  
    return start_date, end_date

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def working_summary(request):
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
        start_date, end_date = get_period_in_months(months)
        
        locations = Location.objects.filter(user=user, check_in_time__range=(start_date, end_date))

        # Check if locations exist
        if not locations.exists():
            return Response({
                "working_summary": [],
                "total_distance": "0.0 km",
                "total_time": "0:00:00",
                "locations_visited": []
            }, status=status.HTTP_200_OK)

        serializer = LocationSerializer(locations, many=True)

        # Calculate total distance
        total_distance = sum(
            float(location.total_distance or 0) for location in locations if location.total_distance
        )
        
        # Calculate total time
        total_time_seconds = 0
        for location in locations:
            if location.total_time:
                try:
                    time_parts = location.total_time.split(':')
                    if len(time_parts) == 3:
                        hours = int(time_parts[0])
                        minutes = int(time_parts[1])
                        seconds = int(time_parts[2])
                        total_time_seconds += timedelta(hours=hours, minutes=minutes, seconds=seconds).total_seconds()
                except ValueError:
                    pass  # Handle cases where total_time format is invalid

        total_time = str(timedelta(seconds=total_time_seconds))

        # Collect locations visited
        locations_visited = []
        for location in locations:
            if location.locations_visited:
                locations_visited.extend(
                    location.locations_visited.strip("[]").replace("'", "").split(',')
                )

        response_data = {
            "working_summary": serializer.data,
            "total_distance": f"{total_distance:.1f} km",
            "total_time": total_time,
            "locations_visited": list(set(locations_visited))  # Ensure unique entries
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def get_period_in_months(months):
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=months * 30)  
    return start_date, end_date
    

firebase = {
    "apiKey": "AIzaSyAAW_MmTXiPSFxt9qLwHDPg3EbwrpV1334",
    "authDomain": "mysore-printers.firebaseapp.com",
    "databaseURL": "https://mysore-printers-default-rtdb.firebaseio.com",
    "projectId": "mysore-printers",
    "storageBucket": "mysore-printers.appspot.com",
    "messagingSenderId": "919497914245",
    "appId": "1:919497914245:web:88babce990a7579a8276ec",
    "measurementId": "G-B4PJ14BM9S"

}
firebase  = pyrebase.initialize_app(firebase)
authe = firebase.auth()
database = firebase.database()


def get_coordinates_for_user(user_id):
    try:
        ref = database.child('coordinate').child(user_id)
        data = ref.get().val()

        if data:
            coordinates_list = [v for k, v in data.items() if k.startswith('location_')]
            sorted_coordinates = sorted(coordinates_list, key=lambda x: int(x['timestamp']))

            return sorted_coordinates

        else:
            return None
    except Exception as e:
        print(f"Error fetching coordinates: {e}")
        return None


def calculate_total_distance(coordinates_list):
    total_distance = 0.0
    num_coordinates = len(coordinates_list)

    if num_coordinates < 2:
        return total_distance

    try:
        for i in range(num_coordinates - 1):
            coord1 = coordinates_list[i]
            coord2 = coordinates_list[i + 1]

            distance_between_points = geodesic((coord1['latitude'], coord1['longitude']),
                                               (coord2['latitude'], coord2['longitude'])).kilometers
            total_distance += distance_between_points

        return f"{total_distance:.2f} km"

    except Exception as e:
        print(f"Error calculating distance: {e}")
        return total_distance


def get_location_name(latitude, longitude):
    geolocator = Nominatim(user_agent="mobile_app_api")
    location = geolocator.reverse((latitude, longitude), exactly_one=True)
    return location.address if location else "Unknown location"

def get_location(latitude, longitude):
    geolocator = Nominatim(user_agent="mobile_app_api")
    retries = 3
    for _ in range(retries):
        try:
            location = geolocator.reverse((latitude, longitude), exactly_one=True)
            return location.raw['address']['neighbourhood'] if location else "Unknown location"
        except GeocoderUnavailable:
            time.sleep(2)  # wait before retrying
    return "Location service unavailable"


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_in(request):
    user_id = request.data.get('id')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')

    if not all([user_id, latitude, longitude]):
        return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = Userprofile.objects.get(pk=user_id)
    except Userprofile.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    check_in_time_now = timezone.now() 
    offset = pytz.FixedOffset(330)
    check_in_time_with_offset = check_in_time_now.astimezone(offset)
    # formatted_date_time = check_in_time_with_offset.strftime('%Y-%m-%d %H:%M:%S')
    formatted_date_time = check_in_time_with_offset.strftime('%Y-%m-%d %H:%M:%S')

    location_address = get_location_name(latitude, longitude) 
    try:
        location = Location.objects.create(
            user=user,
            check_in_location = location_address,
            check_in_time= formatted_date_time
        )
    except Exception as e:
        return Response({'error': f'Error creating location data: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = LocationSerializer(location)
    return Response(serializer.data, status=status.HTTP_201_CREATED)




def make_aware(datetime_obj):
        if timezone.is_naive(datetime_obj):
            return timezone.make_aware(datetime_obj, timezone.get_default_timezone())
        return datetime_obj



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_out(request):
    user_id = request.data.get('id')
    try:
        user = Userprofile.objects.get(pk=user_id)
    except Userprofile.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        location = Location.objects.filter(user=user, check_out_time__isnull=True).latest('check_in_time')

    except Location.DoesNotExist:
        return Response({'error': 'No active check-in found for this user'}, status=status.HTTP_404_NOT_FOUND)

    coordinates_list = get_coordinates_for_user(user_id)

    if not coordinates_list:
        return Response({'error': 'No coordinates found for this user'}, status=status.HTTP_404_NOT_FOUND)

# **********************************EACH LOCATION NAME******************************
    
    location_names = []
    for coordinate in coordinates_list:
        lat, lon = coordinate['latitude'], coordinate['longitude']
        location_name = get_location(lat, lon)
        location_names.append(location_name)

    
    location.locations_visited = location_names

    last_coordinate = coordinates_list[-1]
    location.check_out_location =  get_location_name(last_coordinate['latitude'],last_coordinate['longitude'])
    
    
    check_out_time_now = timezone.now() 
    offset = pytz.FixedOffset(330)
    check_out_time_with_offset = check_out_time_now.astimezone(offset)
    formatted_date_time = check_out_time_with_offset.strftime('%Y-%m-%d %H:%M:%S')
    location.check_out_time = formatted_date_time
    check_out_time = location.check_out_time
    # check_in_time = make_aware(location.check_in_time)
    # print(location.check_out_time)
    check_in_time_now = location.check_in_time
    check_in_time_with_offset = check_in_time_now.astimezone(offset)
    formatted_date_time = check_in_time_with_offset.strftime('%Y-%m-%d %H:%M:%S')
    location.check_in_time = formatted_date_time
    check_in_time = location.check_in_time
    print(check_in_time)
    print(check_out_time)
    check_in_time = datetime.strptime(check_in_time, '%Y-%m-%d %H:%M:%S')
    if isinstance(check_out_time, str):
        check_out_time = datetime.strptime(check_out_time, '%Y-%m-%d %H:%M:%S')
    total_time = check_out_time - check_in_time
    location.total_time = total_time

    location.total_distance = calculate_total_distance(coordinates_list)
    location.save()

    database.child('coordinate').child(user_id).remove()

    serializer = LocationSerializer(location)
    return Response(serializer.data, status=status.HTTP_200_OK)




def get_period_in_months(months):
    end_date = timezone.now()
    start_date = end_date.replace(day=1) - timedelta(days=months*30)  
    return start_date, end_date

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def summary_report(request):
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
        start_date, end_date = get_period_in_months(months)

        locations = Location.objects.filter(user=user, check_in_time__range=(start_date, end_date))
        serializer = LocationSerializer(locations, many=True)

        print(f"User ID: {user_id}")
        print(f"Period: {period}")
        print(f"Start Date: {start_date}")
        print(f"End Date: {end_date}")
        print(f"Locations Count: {locations.count()}")

        
        total_distance = sum(float(location.total_distance or 0) for location in locations)
        
        total_time_seconds = 0
        for location in locations:
            if location.total_time:
                time_parts = location.total_time.split(':')
                hours = int(time_parts[0])
                minutes = int(time_parts[1])
                seconds = int(time_parts[2])
                total_time_seconds += timedelta(hours=hours, minutes=minutes, seconds=seconds).total_seconds()

        total_time = str(timedelta(seconds=total_time_seconds))
    
        # Collect locations visited
        locations_visited = set()
        for location in locations:
            if location.locations_visited:
                locations_visited.update(location.locations_visited.strip("[]").replace("'", "").split(','))

        response_data = {
            'working_summary': serializer.data,
            'total_distance': total_distance,
            'total_time': total_time,
            'locations_visited': list(locations_visited)
        }

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





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
