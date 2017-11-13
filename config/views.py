from rest_framework_mongoengine import viewsets
from rest_framework.response import Response
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

    def update(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(name=request.data['name'])
                user.wins += request.data['win']
                user.losses += request.data['loss']
                user.matchesId = user.matchesId if user.matchesId is not None else []
                user.matchesId.append(request.data['matchId'])
                serializer = UserSerializer(user)
                serializer.save()
                return Response(serializer.data)
            except User.DoesNotExist:
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

    def update(self, request, *args, **kwargs):
        serializer = MatchSerializer(data=request.data)
        if serializer.is_valid():
            try:
                if 'id' in request.data:
                    match = Match.objects.get(id=request.data['id'])
                    match.result = request.data['result']
                    match.status = request.data['status']
                    serializer = MatchSerializer(match)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    raise Match.DoesNotExist
            except Match.DoesNotExist:
                return Response(serializer.data, status=201)
        else:
            return Response(serializer.data, status=400)


class StageViewSet(viewsets.ModelViewSet):
    '''
    Contains information about inputs/outputs of a single program
    that may be used in Universe workflows.
    '''
    lookup_field = '_id'
    serializer_class = MatchSerializer

    def get_queryset(self):
        return Match.objects.all()

    def create(self, request, pk=None):
        serializer = StageSerializer(data=request.data)
        if serializer.is_valid():
            try:
                if 'id' in request.data:
                    stage = Stage.objects.get(id=request.data['id'])
                    serializer = StageSerializer(stage)
                    return Response(serializer.data)
                else:
                    raise Stage.DoesNotExist
            except Stage.DoesNotExist:
                serializer.save()
                return Response(serializer.data, status=201)
        else:
            return Response(serializer.data, status=400)

    def update(self, request, *args, **kwargs):
        serializer = StageSerializer(data=request.data)
        if serializer.is_valid():
            try:
                if 'id' in request.data:
                    stage = Stage.objects.get(id=request.data['id'])
                    stage.result = request.data['result']
                    stage.status = request.data['status']
                    serializer = StageSerializer(stage)
                    serializer.save()
                    return Response(serializer.data)
                else:
                    raise Stage.DoesNotExist
            except Stage.DoesNotExist:
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
        base_url = wsgiref.util.application_uri(self.request.environ)
        if serializer.is_valid():
            payload = {'name': request.data['userName']}
            user_response = requests.post(base_url + 'api/user/', json=payload)
            if user_response.status_code == 201 or user_response.ok:
                return self.post_response(user_response, request, serializer, base_url)
            else:
                return Response(serializer.data, status=400)
        else:
            return Response(serializer.data, status=400)

    def post_response(self, user_response, request, serializer, base_url):
        stage_responses = []
        for scenario, difficulty in self.get_scenarios_difficulties():
            payload = self.get_stage_payload(user_response, scenario, request, difficulty)
            stage_response = requests.post(base_url + 'api/stage/', json=payload)
            if stage_response.status_code == 201:
                return Response(serializer.data, status=400)
            stage_responses.append(stage_response)
        payload = self.get_match_payload(user_response, stage_responses, request)
        match_response = requests.post(base_url + 'api/match/', json=payload)
        if match_response.status_code == 201:
            return Response(self.get_login_payload(map(lambda x: x.json(), stage_responses), match_response.json()))
        else:
            return Response(serializer.data, status=400)

    def get_scenarios_difficulties(self):
        scenarios = random.shuffle(['ocean_wall.png', 'river.png'])
        difficulty1 = random.randint(30, 59)
        difficulty2 = random.randint(difficulty1 + 10, 80)
        difficulties = [difficulty1, difficulty2]
        return scenarios, difficulties

    def get_stage_payload(self, user_response, scenario, request, difficulty):
        return {'userName': user_response.json()['name'],
                   'userId': user_response.json()['id'],
                   'scenario': scenario,
                   'characterName': request.data['characterName'],
                   'difficulty': difficulty,
                   'status': 'playing'}

    def get_match_payload(self, user_response, stage_responses, request):
        return {'userName': user_response.json()['name'],
                           'userId': user_response.json()['id'],
                           'stagesId': map(lambda x: x.json()['id'], stage_responses),
                           'characterName': request.data['characterName'],
                           'status': 'playing'}

    def get_login_payload(self, stages_payload, match_payload):
        match_payload.pop('stageId', None)
        match_payload['stages'] = stages_payload
        return match_payload

    def update(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        base_url = wsgiref.util.application_uri(self.request.environ)
        if serializer.is_valid():
            payload = self.get_user_upt_payload(request)
            user_response = requests.put(base_url + 'api/user/', json=payload)
            if user_response.ok:
                return self.put_response(request)
            else:
                return Response(serializer.data, status=400)
        else:
            return Response(serializer.data, status=400)

    def put_response(self, request, serializer, base_url):
        payload = self.get_match_upt_payload(request)
        match_response = requests.put(base_url + 'api/match/', json=payload)
        if match_response.ok:
            for stage in request.data['match']['stages']:
                payload = self.get_stage_upt_payload(stage)
                stage_response = requests.put(base_url + 'api/stage/', json=payload)
                if stage_response.status_code == 201:
                    return Response(serializer.data, status=400)
            payload = {'validate': 'ok'}
            return Response(payload)

    def get_user_upt_payload(self, request):
        return {'id': request.data['userId'],
                'matchId': request.data['match']['id'],
                'win': 1 if request.data['match']['result'] > 0 else 0,
                'loss': 1 if request.data['match']['result'] < 0 else 0}

    def get_match_upt_payload(self, request):
        return {'id': request.data['match']['id'],
                'result': 'victory' if request.data['match']['result'] > 0 else 'loss',
                'status': request.data['match']['status']}

    def get_stage_upt_payload(self, stage):
        return {'id': stage['id'],
                'result': 'victory' if stage['result'] > 0 else 'loss',
                'status': stage['status']}








