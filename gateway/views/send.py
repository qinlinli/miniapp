from sanic import Blueprint, request
from sanic.response import json
from json import loads, dumps
import aiohttp
import json as _json
from sanic_openapi import doc
import time

from gateway.common.register import jinja2

from gateway.common.build_header import get_header
from gateway.models.request import Request
from gateway.common.register import objects
from collections import OrderedDict
from gateway.inout_verify import send_verify
from gateway.common.utils.api import success, fail
from gateway.inout_verify.form import codes
from dask import delayed

bp = Blueprint('send', 'send')



def marshal(data, fields, envelope=None):
    """Takes raw data (in the form of a dict, list, object) and a dict of
    fields to output and filters the data based on those fields.

    :param data: the actual object(s) from which the fields are taken from
    :param fields: a dict of whose keys will make up the final serialized
                   response output
    :param envelope: optional key that will be used to envelop the serialized
                     response


    >>> data = { 'a': 100, 'b': 'foo' }
    >>> mfields = { 'a': fields.Raw }

    >>> marshal(data, mfields)
    OrderedDict([('a', 100)])

    >>> marshal(data, mfields, envelope='data')
    OrderedDict([('data', OrderedDict([('a', 100)]))])

    """

    if isinstance(data, (list, tuple)) or data.__dict__.get('_rows'):
        return [marshal(d, fields) for d in data]
    items = ((k, marshal(data, v) if isinstance(v, dict)
              else v.func(getattr(data, k, v.default)) if v.func else getattr(data, k, v.default))
             for k, v in fields.items())
    return OrderedDict(items)


def form_validate(form_validate):
    def test(func):
        def inner(*args, **kwargs):
            request_data = args[0]
            request_params = dict()
            if request_data.args:
                request_params.update(request_data.args)
            if request_data.form:
                request_params.update(request_data.form)
            else:
                if request_data.json:
                    request_params.update(request_data.json)
            validate_obj = form_validate()
            validate_res = validate_obj.validate(request_params)

            if not validate_res:
                error, code = validate_obj.get_error()
                return fail(codes.HTTP_BAD_REQUEST, code, error)

            return func(*args, **kwargs)
        return inner
    return test


@bp.route('/', ['GET', 'POST'])
@form_validate(send_verify.SendInput().build_rule())
async def send(request):
    data = request.json
    method = data.get('method')
    ak = data.get('ak')
    sk = data.get('sk')
    all_url = data.get('url')
    params = loads(data.get('params'))
    print(params)
    timestamp = data.get('timestamp')

    str, token, headers = get_header(method, params, all_url, ak, sk, timestamp)
    start = time.time()
    async with aiohttp.ClientSession() as session:
        if method == 'GET':
            async with session.get(all_url, headers=headers, params=params) as resp:
                response = await resp.json()
        elif method == 'POST':
            async with session.post(all_url, headers=headers, json=params) as resp:
                response = await resp.text()
    end = time.time()
    print(end-start)
    import sys
    sys.stdout.flush()
    res = {
        'str': str,
        'token': token,
        'response': response
    }
    return json(res)


@bp.route('/create', ['POST'])
@form_validate(send_verify.SendInput().build_rule())
async def create(request):
    data = request.json
    request_data = await objects.create(Request, **data)
    return json(request_data)


@bp.route('/detail', ['GET'])
# @form_validate(send_verify.DetailInput().build_rule())
async def detail(request):
    _id = request.args.get('id', 1)
    request_data = await objects.get(Request, id=_id)
    return jinja2.render('send/detail.html', request, data=request_data)


@bp.route('/lists', ['GET', 'POST'])
@doc.inout(send_verify.ListInput, send_verify.ListOut)
@form_validate(send_verify.ListInput().build_rule())
async def lists(request):

    page = request.args.get('page', 1)
    request_data = await objects.execute(Request.select().order_by(Request.id.desc()).paginate(page, 10))
    return jinja2.render('/send/list.html', request, request_data= request_data)


@bp.route('/edit', ['POST'])
async def edit(request):
    data = request.json
    request_data = await objects.create(Request, **data)
    return json(request_data)


@bp.route('/index')
async def index(request):
    return jinja2.render('index.html', request)

