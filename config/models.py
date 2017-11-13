from django.db import models
from mongoengine import Document, EmbeddedDocument, fields

# Create your models here.


class User(Document):
    id = fields.ObjectIdField
    name = fields.StringField(required=True)
    wins = fields.IntField
    losses = fields.IntField
    matches = fields.ListField


class Match(Document):
    id = fields.ObjectIdField
    userName = fields.StringField(required=True)
    userId = fields.ObjectIdField(required=True)
    result = fields.StringField
    stagesId = fields.ListField(required=True)
    characterName = fields.StringField(required=True)
    status = fields.StringField(required=True)


class Stage(Document):
    id = fields.ObjectIdField
    userName = fields.StringField(required=True)
    userId = fields.ObjectIdField(required=True)
    result = fields.StringField
    scenario = fields.StringField(required=True)
    characterName = fields.StringField(required=True)
    difficulty = fields.StringField(required=True)
    status = fields.StringField(required=True)


class Login(models.Model):
    name = fields.StringField(required=True)
    characterName = fields.StringField(required=True)