from sanic import Sanic
from gateway.views import register_app
from gateway.common.register import jinja2
from sanic_openapi import swagger_blueprint

app = Sanic(__name__)

register_app(app)
jinja2.init_app(app)

app.blueprint(swagger_blueprint)
app.static('/static', './gateway/static')
import sys
sys.stdout.flush()

app.run(host='0.0.0.0', port=8000, debug=True)