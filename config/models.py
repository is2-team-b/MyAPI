from django.db import models
from mongoengine import Document, EmbeddedDocument, fields

# Create your models here.

class User(Document):
    name = fields.StringField(required=True)
    wins = fields.IntField
    losses = fields.IntField

class Match(Document):
    result: fields.StringField
    map: fields.StringField
    myCharacter: fields.StringField
    difficulty: fields.StringField