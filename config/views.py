from rest_framework_mongoengine import viewsets
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
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

    def partial_update(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(name=request.data['name'])
                user.wins += int(request.data['win'])
                user.losses += int(request.data['loss'])
                user.matchesId.append(request.data['matchId'])
                user.save()
                serializer = UserSerializer(user)
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
    lookup_field = 'id'
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

    def partial_update(self, request, *args, **kwargs):
        serializer = MatchSerializer(data=request.data)
        try:
            if 'id' in request.data:
                match = Match.objects.get(id=request.data['id'])
                match.result = request.data['result']
                match.status = request.data['status']
                match.save()
                serializer = MatchSerializer(match)
                return Response(serializer.data)
            else:
                raise Match.DoesNotExist
        except Match.DoesNotExist:
            return Response(serializer.data, status=201)
        except Exception:
            return Response(serializer.data, status=400)


class StageViewSet(viewsets.ModelViewSet):
    '''
    Contains information about inputs/outputs of a single program
    that may be used in Universe workflows.
    '''
    lookup_field = 'id'
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

    def partial_update(self, request, *args, **kwargs):
        serializer = StageSerializer(data=request.data)
        try:
            if 'id' in request.data:
                stage = Stage.objects.get(id=request.data['id'])
                stage.result = request.data['result']
                stage.status = request.data['status']
                stage.save()
                serializer = StageSerializer(stage)
                return Response(serializer.data)
            else:
                raise Stage.DoesNotExist
        except Stage.DoesNotExist:
            return Response(serializer.data, status=201)
        except Exception:
            return Response(serializer.data, status=400)


class LoginViewSet(viewsets.ModelViewSet):
    '''
    Contains information about inputs/outputs of a single program
    that may be used in Universe workflows.
    '''

    lookup_field = 'id'
    serializer_class = LoginSerializer

    def get_queryset(self):
        return Login.objects.all()

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
        scenarios_difficulties = self.get_scenarios_difficulties()
        for scenario, difficulty in zip(scenarios_difficulties[0], scenarios_difficulties[1]):
            payload = self.get_stage_payload(user_response, scenario, request, difficulty)
            stage_response = requests.post(base_url + 'api/stage/', json=payload)
            if stage_response.status_code is not 201:
                return Response(serializer.data, status=400)
            stage_responses.append(stage_response)
        payload = self.get_match_payload(user_response, stage_responses, request)
        match_response = requests.post(base_url + 'api/match/', json=payload)
        if match_response.status_code == 201:
            serializer.save()
            return Response(self.get_login_payload(list(map(lambda x: x.json(), stage_responses)),
                                                   match_response.json(), serializer.data['id']))
        else:
            return Response(serializer.data, status=400)

    def get_scenarios_difficulties(self):
        scenarios = ['ocean_wall.png', 'river.png']
        random.shuffle(scenarios)
        difficulty1 = random.randint(30, 59)
        difficulty2 = random.randint(difficulty1 + 10, 80)
        difficulties = [difficulty1, difficulty2]
        return [scenarios, difficulties]

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
                           'stagesId': list(map(lambda x: x.json()['id'], stage_responses)),
                           'characterName': request.data['characterName'],
                           'status': 'playing'}

    def get_login_payload(self, stages_payload, match_payload, login_id):
        match_payload['matchId'] = match_payload['id']
        del match_payload['id']
        del match_payload['stagesId']
        match_payload['stages'] = stages_payload
        match_payload['loginId'] = login_id
        return match_payload

    def update(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        base_url = wsgiref.util.application_uri(self.request.environ)
        if serializer.is_valid():
            payload = self.get_user_upt_payload(request)
            user_response = requests.patch(base_url + 'api/user/' + request.data['userName'] + '/', json=payload)
            if user_response.ok:
                return Response(self.patch_response(request, serializer, base_url))
            else:
                return Response(serializer.data, status=400)
        else:
            return Response(serializer.data, status=400)

    def patch_response(self, request, serializer, base_url):
        payload = self.get_match_upt_payload(request)
        match_response = requests.patch(base_url + 'api/match/' + request.data['match']['id'] + '/', json=payload)
        if match_response.ok:
            for stage in request.data['match']['stages']:
                payload = self.get_stage_upt_payload(stage)
                stage_response = requests.patch(base_url + 'api/stage/' + stage['id'] + '/', json=payload)
                if stage_response.status_code == 201:
                    return Response(serializer.data, status=400)
            return {'validate': 'ok'}

    def get_user_upt_payload(self, request):
        return {'id': request.data['userId'],
                'name': request.data['userName'],
                'matchId': request.data['match']['id'],
                'win': 1 if request.data['match']['result'] == 'win' else 0,
                'loss': 1 if request.data['match']['result'] == 'loss' else 0}

    def get_match_upt_payload(self, request):
        return {'id': request.data['match']['id'],
                'result': request.data['match']['result'],
                'status': request.data['match']['status']}

    def get_stage_upt_payload(self, stage):
        return {'id': stage['id'],
                'result': stage['result'],
                'status': stage['status']}


class ConfigViewSet(viewsets.ModelViewSet):
    '''
    Contains information about inputs/outputs of a single program
    that may be used in Universe workflows.
    '''
    lookup_field = 'id'
    serializer_class = ConfigSerializer

    def get_queryset(self):
        return Config.objects.all()

    def create(self, request, pk=None):
        serializer = ConfigSerializer(data=request.data)
        if serializer.is_valid():
            try:
                if 'id' in request.data:
                    config = Stage.objects.get(id=request.data['id'])
                    serializer = ConfigSerializer(config)
                    return Response(serializer.data)
                else:
                    raise Config.DoesNotExist
            except Config.DoesNotExist:
                serializer.save()
                return Response(serializer.data, status=201)
        else:
            return Response(serializer.data, status=400)

    def update(self, request, *args, **kwargs):
        serializer = ConfigSerializer(data=request.data)
        try:
            if 'id' in request.data:
                config = Config.objects.get(id=request.data['id'])
                config.numEnemies = request.data['numEnemies']
                config.difficulty = request.data['difficulty']
                config.scenarioOrder = request.data['scenarioOrder']
                config.save()
                serializer = ConfigSerializer(config)
                return Response(serializer.data)
            else:
                raise Config.DoesNotExist
        except Config.DoesNotExist:
            return Response(serializer.data, status=201)
        except Exception:
            return Response(serializer.data, status=400)


class ConfigView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'config.html'

    def get(self, request):
        return Response({'lol': 1})


