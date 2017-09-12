from django.shortcuts import render
from rest_framework_mongoengine import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer

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
        if (serializer.is_valid()):
            try:
                user = User.objects.get(name=request.data['name'])
                serializer = UserSerializer(user)
                return Response(serializer.data)
            except User.DoesNotExist:
                serializer.save()
                return Response(serializer.data, status=201)
        else:
            return Response(serializer.data, status=400)






