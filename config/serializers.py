from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework.serializers import ModelSerializer
from .models import *


class UserSerializer(DocumentSerializer):
    class Meta:
        model = User
        fields = '__all__'

class MatchSerializer(DocumentSerializer):
    class Meta:
        model = Match
        fields = '__all__'

class LoginSerializer(ModelSerializer):
    class Meta:
        model = Login
        fields = '__all__'