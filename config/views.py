from django.shortcuts import render
from rest_framework_mongoengine import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from .models import *
from .serializers import *
import requests
import random
import wsgiref.util

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    '''
    Contains information about inputs/outputs of a single program
    that may be used in Universe workflows.
    '''
    lookup_field = 'name'
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()

    def create(self, request, pk=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(name=request.data['name'])
                serializer = UserSerializer(user)
                return Response(serializer.data)
            except User.DoesNotExist:
                serializer.save()
                user = User.objects.get(name=request.data['name'])
                serializer = UserSerializer(user)
                return Response(serializer.data, status=201)
        else:
            return Response(serializer.data, status=400)

class MatchViewSet(viewsets.ModelViewSet):
    '''
    Contains information about inputs/outputs of a single program
    that may be used in Universe workflows.
    '''
    lookup_field = '_id'
    serializer_class = MatchSerializer

    def get_queryset(self):
        return Match.objects.all()

    def create(self, request, pk=None):
        serializer = MatchSerializer(data=request.data)
        if serializer.is_valid():
            try:
                if 'id' in request.data:
                    match = Match.objects.get(id=request.data['id'])
                    serializer = MatchSerializer(match)
                    return Response(serializer.data)
                else:
                    raise Match.DoesNotExist
            except Match.DoesNotExist:
                serializer.save()
                return Response(serializer.data, status=201)
        else:
            return Response(serializer.data, status=400)

class LoginViewSet(viewsets.ModelViewSet):
    '''
    Contains information about inputs/outputs of a single program
    that may be used in Universe workflows.
    '''

    serializer_class = LoginSerializer

    def create(self, request, pk=None):
        serializer = LoginSerializer(data=request.data)
        baseUrl = wsgiref.util.application_uri(self.request.environ)
        if serializer.is_valid():
            payload = {'name': request.data['userName']}
            userResponse = requests.post(baseUrl + 'api/user/', json=payload)
            if userResponse.status_code == 201 or userResponse.ok:
                scenario = random.choice(['ocean_wall.png', 'river.png'])
                difficulty = random.randint(30, 60)
                payload = {'userName': userResponse.json()['name'],
                           'userId': userResponse.json()['id'],
                           'scenario': scenario,
                           'characterName': request.data['characterName'],
                           'difficulty': difficulty}
                matchResponse = requests.post(baseUrl + 'api/match/', json=payload)
                if matchResponse.status_code == 201:
                    return Response(matchResponse.json())
                else:
                    return Response(serializer.data, status=400)
            else:
                return Response(serializer.data, status=400)
        else:
            return Response(serializer.data, status=400)





