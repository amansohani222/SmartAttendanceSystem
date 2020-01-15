import math
from datetime import datetime

from django.contrib.auth import logout
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from attendance.models import Officer, Absence
from attendance.permissions import IsOwner
from attendance.serializer import OfficerSerializer


class OfficerViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = Officer.objects.all()
    serializer_class = OfficerSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.dict()
        user = Officer(username=data['username'], first_name=data['first_name'], last_name=data['last_name'],
                       phone=data['phone'],
                       email=data['email'], office_latitude=data['office_latitude'],
                       office_longitude=data['office_longitude'], office_time_entry=data['office_time_entry'])
        user.set_password(request.data['password'])
        user.save()
        serializer = self.get_serializer(user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        id = instance.id
        try:
            officer = Officer.objects.get(id=id)
            absent_date = Absence.objects.filter(officer=officer).values('absence_date')
            serializer = OfficerSerializer(officer)
            return Response({"officer": serializer.data, "absence_date": absent_date})
        except Exception:
            return Response({"message": "Please login first"})

    @action(detail=True, methods=['get'])
    def update_attendance(self, request, pk=None):
        officer = Officer.objects.get(id=request.user.id)
        if datetime.now().time() > officer.office_time_entry:
            absence = Absence(absence_date=datetime.now(), officer=officer)
            absence.save()
            return Response({"message": "Sorry you are late! Absent Marked"})
        else:
            o_lat = float(officer.office_latitude)
            o_lon = float(officer.office_longitude)
            lat = float(request.GET['lat'])
            lon = float(request.GET['lon'])
            d=calc_distance([o_lat, o_lon], [lat, lon])
            if d<0.01:
                officer.total_attendance += 1
                officer.save()
                return Response({"status": "Present Updated"})
            else:
                return Response({"status": "Try again"})


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
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d