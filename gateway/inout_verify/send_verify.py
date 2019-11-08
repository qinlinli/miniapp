from sanic_openapi import doc
from gateway.inout_verify.inout import Input, Output
from gateway.inout_verify.form.form import Form
from gateway.inout_verify.form.validators import InputRequired, ValidatorError
from gateway.inout_verify.form import codes


class ListInput(Input):

    rule = {
        'per_page': doc.String(description='每页多少条', default='20', label='per_page'),
        'page': doc.String(description='第几页', default='1', label='page'),
    }


class DetailInput(Input):

    def a(field_data):
        raise ValidatorError('id测试不能为空',codes.CODE_MISSING_FIELD)

    rule = {
        'id': doc.String(description='id', required=True, label='id', validators=[InputRequired], func=a),
    }


class ListOut(Output):

    rule = {
        'name': doc.String(description='123', default='adf', ),
        'url': doc.String(description='123', default='123444', ),
    }


class SendInput(Input):
    rule = {
        'name': doc.String(description='名称', label='名称',),
        'url': doc.String(description='地址', label='地址', required=True, validators=[InputRequired]),
        'method': doc.String(description='方式', label='方式', required=True, validators=[InputRequired]),
        'ak': doc.String(description='ak', label='ak', required=True, validators=[InputRequired]),
        'sk': doc.String(description='sk', label='sk', required=True, validators=[InputRequired]),
        'params': doc.String(description='参数', label='参数',),
        'timestamp': doc.String(description='时间戳', label='时间戳',),
    }
