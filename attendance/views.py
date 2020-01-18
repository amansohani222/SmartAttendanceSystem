import math
from datetime import datetime

from django.contrib.auth import logout, login
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from attendance.models import Officer, Present
from attendance.permissions import IsOwner
from attendance.serializer import OfficerSerializer, LoginSerializer


class OfficerViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    permission_classes_by_action = {
        'retrieve': (IsOwner,),
        'update': (IsOwner,),
        'destroy': (IsOwner,),
    }

    queryset = Officer.objects.all()
    serializer_class = OfficerSerializer

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
        data = request.data
        user = Officer(username=data['username'],
                       first_name=data['first_name'], last_name=data['last_name'],
                       phone=data['phone'],
                       email=data['email'], office_latitude=data['office_latitude'],
                       office_longitude=data['office_longitude'], office_time_entry=data['office_time_entry'])
        user.set_password(request.data['password'])
        user.save()
        serializer = self.serializer_class(user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        print("AMAN")
        instance = self.get_object()
        id = instance.id
        try:
            officer = Officer.objects.get(id=id)
            present_date = Present.objects.filter(officer=officer).values('present_date')
            serializer = OfficerSerializer(officer)
            return Response({"officer": serializer.data, "present_date": present_date})
        except Exception:
            return Response({"message": "Please login first"})

    @action(detail=True, methods=['get'])
    def update_attendance(self, request, pk=None):
        officer = Officer.objects.get(id=request.user.id)
        if datetime.now().time() > officer.office_time_entry:
            return Response({"message": "You are absent"})
        else:
            o_lat = float(officer.office_latitude)
            o_lon = float(officer.office_longitude)
            lat = float(request.GET['lat'])
            lon = float(request.GET['lon'])
            d = calc_distance([o_lat, o_lon], [lat, lon])
            if d < 1:
                try:
                    present = Present(present_date=datetime.now(), officer=officer)
                    present.save()
                    return Response({"message": "Present Marked"})
                except Exception:
                    return Response({"message": "Attendance is already marked"})
            else:
                return Response({"message": "You are not at office"})

class LoginView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "id": request.user.id, "status": "success"}, status=200)
        else:
            return Response({"status": "failed"})


class LogoutView(APIView):
    authentication_class = [TokenAuthentication]

    def post(self, request):
        print(request.user.username)
        request.user.auth_token.delete()
        logout(request)
        return Response({"message": "Logout Successfull"}, status=204)


def calc_distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d
