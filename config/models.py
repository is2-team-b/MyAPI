from django.db import models
from mongoengine import Document, EmbeddedDocument, fields

# Create your models here.


class User(Document):
    id = fields.ObjectIdField
    name = fields.StringField(required=True)
    wins = fields.IntField(default=0)
    losses = fields.IntField(default=0)
    matchesId = fields.ListField(default=[])


class Match(Document):
    id = fields.ObjectIdField
    userName = fields.StringField(required=True)
    userId = fields.ObjectIdField(required=True)
    result = fields.StringField(default='')
    stagesId = fields.ListField(required=True)
    characterName = fields.StringField(required=True)
    status = fields.StringField(required=True)


class Stage(Document):
    id = fields.ObjectIdField
    userName = fields.StringField(required=True)
    userId = fields.ObjectIdField(required=True)
    result = fields.StringField(default='')
    scenario = fields.StringField(required=True)
    characterName = fields.StringField(required=True)
    difficulty = fields.IntField(required=True)
    status = fields.StringField(required=True)


class Login(Document):
    id = fields.ObjectIdField
    name = fields.StringField
    characterName = fields.StringField
    userId = fields.ObjectIdField
    match = fields.DictField


class Config(Document):
    id = fields.ObjectIdField
    numEnemies = fields.IntField(required=True)
    difficulty = fields.IntField(required=True)
    scenariosOrder = fields.ListField(required=True)