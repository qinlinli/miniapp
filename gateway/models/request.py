import peewee
from datetime import datetime
from gateway.common.register import database

class Request(peewee.Model):
    class Meta:
        database = database

    id = peewee.IntegerField
    name = peewee.CharField(64)
    url = peewee.CharField(255)
    method = peewee.CharField(64)
    ak = peewee.CharField(128)
    sk = peewee.CharField(128)
    params = peewee.TextField()
    timestamp = peewee.CharField(128)
    created = peewee.DateTimeField(default=datetime.now)
    updated = peewee.DateTimeField(default=datetime.now)
    deleted = peewee.BooleanField(default=False)