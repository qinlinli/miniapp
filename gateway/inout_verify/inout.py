from gateway.inout_verify.form.form import Form
from gateway.inout_verify.form.validators import ValidatorError

class InOut:
    def build_rule(self, rule=None):
        if not rule:
            rule = self.rule
        class_name = self.__class__.__name__
        class_name = type(class_name, (Form,), dict())

        if not hasattr(class_name, '__rule__'):
            setattr(class_name, '__rule__', rule)

        for name, filed in rule.items():
            if isinstance(filed, dict):
                setattr(class_name, name, self.build_rule(filed))
            elif isinstance(filed, list):
                setattr(class_name, name, [self.build_rule(filed[0])])
            setattr(class_name, name, filed)
        return class_name


class Input(InOut):
    #  in
    content_type = None
    location = 'query'
    required = False
    rule = None

    def input(self):
        return {
            'rule': self.build_rule(),
            'content_type': self.content_type,
            'required': self.required,
            'location': self.location,
        }


class Output(InOut):
    # out
    description = None
    content_type = 'application/json'
    rule = None

    def output(self):
        return {
            'rule': self.build_rule(),
            'content_type': self.content_type,
            'description': self.description,
        }
