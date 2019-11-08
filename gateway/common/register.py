from sanic_jinja2 import SanicJinja2
from peewee_async import Manager, PooledMySQLDatabase

jinja2 = SanicJinja2()

database = PooledMySQLDatabase('gateway', host='10.39.34.123', port=3306, user='puming', password='123456')
objects = Manager(database)


