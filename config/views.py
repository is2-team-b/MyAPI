from django.shortcuts import render
from rest_framework_mongoengine import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
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

    @detail_route(methods=['post'])
    def create_user(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
            return JSONResponse(user)
        except User.DoesNotExist:
            data = JSONParser().parse(request)
            serializer = UserSerializer(data=data)
            if(serializer.is_valid()):
                serializer.save()
                return JSONResponse(serializer, status=201)
            else:
                return JSONResponse(serializer, status=400)

class JSONResponse(Response):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


