from sanic_openapi.doc import Field
from gateway.inout_verify.form.validators import ValidatorError

class MateForm(type):
    def __new__(cls, names, base, attrs):
        mapping = dict()
        for k, v in attrs.items():
            if isinstance(v, Field):
                mapping[k] = v
        attrs['__mapping__'] = mapping
        return super().__new__(cls, names, base, attrs)


class Form():

    errors = []

    def get_error(self):
        if not self.errors:
            return '无错误'
        else:
            return self.errors[0]

    def validate(self, request_data=None, fields=None):

        fields = fields if fields else self.__rule__
        for name, field in fields.items():

            if isinstance(field, list):
                if request_data.get(name, []):
                    for one in request_data.get(name, []):
                        return self.validate(one, field[0])
            elif isinstance(field, dict):
                return self.validate(request_data.get(name, dict()), field)
            try:
                field.data = request_data.get(name, None)
                if field.validators:
                    for one in field.validators:
                        one()('', field)
                        if field.func:
                            field.func(field)
            except ValidatorError as e:

                self.errors.append(e.args)
        return bool(not self.errors)



