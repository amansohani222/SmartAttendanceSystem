from django.contrib.auth import authenticate
from rest_framework import serializers, exceptions
from attendance.models import Officer, Present


class OfficerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officer
        fields = '__all__'

class PresentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Present
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get("username", "")
        password = data.get("password", "")

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data["user"] = user
                else:
                    raise exceptions.ValidationError("User is not active")
            else:
                raise exceptions.ValidationError("Username or password do not match")
        else:
            raise exceptions.ValidationError("Must provide username and exception")
        return data