from sanic.response import json
from gateway.inout_verify.form import codes

def success(data, http_code=codes.HTTP_OK):
    return json({'code': http_code, 'result': data})

def fail(http_code, request_code, error):
    return json({'code': request_code, 'error': error}, status=http_code)