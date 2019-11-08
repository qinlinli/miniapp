# -*- coding: utf-8 -*-
'''
定义字段验证器

未来有需要添加新的 validator ::

    class NewValidator(BaseValidator):

        def __call__(self, form, field):
            data = field.data
            if not validate(data):
                raise ValidatorError(self.message)

B.T.W
# TODO
重新 review 这里发现- - validator 都没有用上 self.message 属性
'''
import re
import string
import decimal
import datetime
import operator
from functools import wraps

from gateway.inout_verify.form import codes


class ValidatorError(Exception):
    pass


def none_pass():
    def wrapper(f):
        @wraps(f)
        def decorated(self, form, field, *args, **kwargs):
            if field.data is None:
                return
            return f(self, form, field, *args, **kwargs)
        return decorated
    return wrapper


class BaseValidator(object):

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        raise NotImplementedError()


class InputRequired(BaseValidator):

    def __call__(self, form, field):
        data = field.data
        if not (data or data == 0):
            raise ValidatorError(self.message or '%s 不能为空' % field.label,
                                 codes.CODE_MISSING_FIELD)


class InputRequiredOutZero(BaseValidator):

    def __call__(self, form, field):
        data = field.data
        if not data:  # 零也不通过情况
            raise ValidatorError(self.message or '%s 不能为空' % field.label,
                                 codes.CODE_MISSING_FIELD)


class Mobile(BaseValidator):

    @none_pass()
    def __call__(self, form, field):
        data = field.data
        mobile_pattern = re.compile('(?:^1[3,4,5,6,7,8,9]\d{9}$)|(?:^$)')
        if not mobile_pattern.match(data):
            raise ValidatorError(self.message or
                                 '手机号格式不对',
                                 codes.CODE_INVALID_MOBILE_NUMBER)


class DigitAndLetterAndHyphenAndUnderscore(BaseValidator):

    @none_pass()
    def __call__(self, form, field):
        data = field.data
        pattern = re.compile('^\w[\w-]*$')
        if data is None or not pattern.match(data):
            raise ValidatorError(self.message or
                                 '%s只能为数字、字母、下划线的组合'
                                 % field.label,
                                 codes.CODE_INVALID_REQUEST_DATA)


class ChineseChar(BaseValidator):

    @none_pass()
    def __call__(self, form, field):
        data = field.data
        pattern = re.compile(u'([\u4e00-\u9fa5]*$)')
        if not pattern.match(data):
            raise ValidatorError(self.message or
                                 '%s只能为为中文汉字' % field.label,
                                 codes.CODE_INVALID_REQUEST_DATA)


class Integer(BaseValidator):

    @none_pass()
    def __call__(self, form, field):
        data = field.data
        try:
            int(data)
        except (ValueError, TypeError):
            raise ValidatorError(
                self.message or '%s必需为数字' % field.label,
                codes.CODE_INVALID_REQUEST_DATA)


class PositiveInteger(BaseValidator):

    @none_pass()
    def __call__(self, form, field):
        data = field.data
        try:
            positive = int(data)
            if positive < 0:
                raise ValidatorError(
                    self.message or '%s必需为大于0的数字' % field.label,
                    codes.CODE_INVALID_REQUEST_DATA)
        except (ValueError, TypeError):
            raise ValidatorError(
                self.message or '%s必需为大于0的数字' % field.label,
                codes.CODE_INVALID_REQUEST_DATA)


class Decimal(BaseValidator):

    def __call__(self, form, field):
        data = field.data
        try:
            decimal.Decimal(data)
        except decimal.InvalidOperation:
            raise ValidatorError(
                self.message or '%s 必需为数字或小数' % field.label,
                codes.CODE_INVALID_REQUEST_DATA)


class MinLength(BaseValidator):

    def __init__(self, length, message=None):
        super(MinLength, self).__init__(message)
        self.length = length

    @none_pass()
    def __call__(self, form, field):
        data = field.data
        if data is None or len(data) < self.length:
            raise ValidatorError(
                self.message or '%s字符长度应不小于 %s 位' %
                (field.label, self.length),
                codes.CODE_DATA_TOO_SHORT)


class MaxLength(BaseValidator):

    def __init__(self, length, message=None):
        super(MaxLength, self).__init__(message)
        self.length = length

    @none_pass()
    def __call__(self, form, field):
        if field.data is None or len(field.data) > self.length:
            raise ValidatorError(
                self.message or '%s 字符长度应不大于 %s 位' %
                (field.label, self.length),
                codes.CODE_DATA_TOO_LONG)


class DigitOnly(BaseValidator):

    @none_pass()
    def __call__(self, form, field):
        data = field.data
        assert isinstance(data, basestring)    # FIXME: dont use assert
        if not all(imap(lambda c: c.isdigit(), data)):
            raise ValidatorError(
                self.message or '%s只能为数字' % field.label,
                codes.CODE_INVALID_REQUEST_DATA)


class DigitAndLetterOnly(BaseValidator):

    @none_pass()
    def __call__(self, form, field):
        data = field.data
        assert isinstance(data, basestring)    # FIXME: dont use assert

        if not all(imap(lambda c: c.isdigit() or c.isalpha(), data)):
            raise ValidatorError(
                self.message or
                '%s只能由数字或字符组合而成' % field.label,
                codes.CODE_INVALID_REQUEST_DATA)


class DigitAndLetterMixed(BaseValidator):

    @none_pass()
    def __call__(self, form, field):
        data = field.data
        assert isinstance(data, basestring)    # FIXME
        if not set(data) & set(string.digits) \
                or not set(data) & set(string.letters):
            raise ValidatorError(
                self.message or
                '%s需要包含数字和字母' % field.label,
                codes.CODE_INVALID_REQUEST_DATA)


class IdentityIdRequired(BaseValidator):

    @none_pass()
    def __call__(self, form, field):

        IDENTITY_ID_LENGTH = 18
        WEIGHT = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        CHECK = ['1', '0', 'x', '9', '8', '7', '6', '5', '4', '3', '2']

        data = field.data
        assert '__len__' in dir(data)
        data = data.lower()

        if len(data) != IDENTITY_ID_LENGTH:
            raise ValidatorError(
                self.message or
                '%s需要%d位长度' % (field.label, IDENTITY_ID_LENGTH),
                codes.CODE_INVALID_IDENTITY_ID)

        prefix = data[:IDENTITY_ID_LENGTH - 1]
        if not prefix.isdigit():
            raise ValidatorError(
                self.message or "请输入正确的身份证号码",
                codes.CODE_INVALID_IDENTITY_ID)

        prefix = [int(i) for i in prefix]
        dot_product = sum(imap(operator.mul, prefix, WEIGHT))

        if CHECK[dot_product % 11] != data[-1]:
            raise ValidatorError(
                self.message or "请输入正确的身份证号码",
                codes.CODE_INVALID_IDENTITY_ID)


class BeOneOf(BaseValidator):

    def __init__(self, enum, message=None):
        super(BeOneOf, self).__init__(message)
        assert '__contains__' in dir(enum)
        self._enum = enum

    @none_pass()
    def __call__(self, form, field):
        data = field.data
        if data not in self._enum:
            raise ValidatorError(
                self.message or
                '%s只能在(%s)里' % (field.label, ','.join(set(map(str, self._enum)))),
                codes.CODE_INVALID_REQUEST_DATA)


class DatetimeString(BaseValidator):

    def __init__(self, format="%Y-%m-%d %H:%M:%S", **kwargs):
        super(DatetimeString, self).__init__(**kwargs)
        self.format = format

    @none_pass()
    def __call__(self, form, field):
        data = field.data
        if len(data) > 0:
            try:
                # strftime 要求time晚于1900年，校验更准
                datetime.datetime.strptime(
                    data, self.format).strftime(
                    self.format)
            except (TypeError, ValueError):
                raise ValidatorError(
                    self.message or '非法的时间格式, 请使用 %s' % self.format,
                    codes.CODE_INVALID_REQUEST_DATA)


class StartsWith(BaseValidator):

    def __init__(self, startswith, message=None):
        super(StartsWith, self).__init__(message)
        self._startswith = startswith

    @none_pass()
    def __call__(self, form, field):
        data = field.data
        if not data.startswith(self._startswith):
            raise ValidatorError(
                self.message or
                '%s需要以%s开头' % (field.name, str(self._startswith)),
                codes.CODE_INVALID_REQUEST_DATA)


class PasswordValidator(BaseValidator):

    def __call__(self, form, field):
        if field.data is None or not re.match(
                r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9]{6,16}$', field.data):
            raise ValidatorError(
                '密码格式不合法',
                codes.CODE_PASSWORD_INVALID_FORMAT)


class URLValidator(BaseValidator):

    def __call__(self, form, field):
        exp = r'^[a-z]+://(?P<host>[^/:]+)(?P<port>:[0-9]+)?(?P<path>\/.*)?$'

        if field.data:
            if not re.match(exp, field.data, re.IGNORECASE):
                raise ValidatorError(
                    'URL格式不合法',
                    codes.CODE_URL_INVALID_FORMAT
                )


class ChineseCharAndLetter(BaseValidator):

    @none_pass()
    def __call__(self, form, field):
        data = field.data
        pattern = re.compile(u'^([\u4e00-\u9fa5a-zA-Z]+)$')
        if not pattern.match(data):
            raise ValidatorError(self.message or
                                 '%s只能为汉字和字母组合' %
                                 field.label,
                                 codes.CODE_INVALID_REQUEST_DATA)


class ChineseCharAndDigitAndLetter(BaseValidator):

    @none_pass()
    def __call__(self, form, field):
        data = field.data
        pattern = re.compile(u'^([\u4e00-\u9fa5a-zA-Z\d]+)$')
        if not pattern.match(data):
            raise ValidatorError(self.message or
                                 '%s只能为汉字、字母和数字的组合' %
                                 field.label,
                                 codes.CODE_INVALID_REQUEST_DATA)


class Email(BaseValidator):

    @none_pass()
    def __call__(self, form, field):
        data = field.data
        pattern = re.compile(u'^.+@([^.@][^@]+)$', re.IGNORECASE)
        if not pattern.match(data):
            raise ValidatorError(self.message or
                                 '请输入正确的邮箱地址',
                                 codes.CODE_INVALID_REQUEST_DATA)


class DatabaseIdValidator(BaseValidator):
    """用来验证数据库 id"""

    def __init__(self, message=None, valid_min_value=1):
        """
        :param str message: 错误消息
        :param int valid_min_value: 合法的最小值，默认为 1（这里包括给定的值）
        """
        super(DatabaseIdValidator, self).__init__(message=message)
        self.min_value = valid_min_value

    def __call__(self, form, field):
        data = field.data
        if not isinstance(data, (int, long)):
            raise ValidatorError(
                self.message or u'id 类型错误', codes.CODE_INVALID_REQUEST_DATA)
        if data < self.min_value:
            raise ValidatorError(
                self.message or u'id 范围错误', codes.CODE_INVALID_REQUEST_DATA)


class Coerce(BaseValidator):
    """用来在验证链上进行强制类型转换的验证器。
    会尝试使用 `coerce_func` 对给定的 Field 进行类型转换，将输入的类型转换为需要的类型，
    并保存在对定的字段上
    如果 `coerce_func` 抛出 `TypeError` 或者 `ValueError`，就认为类型转换失败，
    这个时候验证器会退出并抛出 `ValidationError`。
    这个主要是配合 `request.args` 使用，将字符串类型的查询参数转换为对应的类型，方便进一步
    验证。

    例如：

    .. code:: py

        class SomeForm(Form):
            type = Field(u'类型', validators=[Coerce(int)])

    这个验证器，会尝试将 `type` 的值转化为 `int`，并保存在 `form.type.data` 上。
    如果输入是 `1` 或者 `'1'`，那么转换之后 `form.type.data` 为 `1`，
    如果输入是 `'a'`，转换为失败，会抛出 `ValidationError` 异常。
    """

    def __init__(self, coerce_func, message=None):
        """
        :param function coerce_func: 进行类型转换的函数（其实任何 callable 对象都可以）
        :param unicode message: 错误消息
        """
        super(Coerce, self).__init__(message)
        self.coerce_func = coerce_func

    def __call__(self, form, field):
        try:
            data = self.coerce_func(field.data)
        except (TypeError, ValueError):
            message = self.message or u"{} 值错误".format(field.name)
            raise ValidatorError(message, codes.CODE_INVALID_REQUEST_DATA)
        field.data = data


class ProjectCode(BaseValidator):

    def __call__(self, form, field):
        data = str(field.data)
        pattern = re.compile('^\d{8}$')
        if not pattern.match(data):
            raise ValidatorError(self.message or '项目编码错误',
                                 codes.CODE_INVALID_REQUEST_DATA)


class Type(BaseValidator):

    def __init__(self, types, message=None):
        super(Type, self).__init__(message=message)
        self.types = types

    def __call__(self, form, field):
        if not isinstance(field.data, self.types):
            raise ValidatorError(self.message or '数据类型错误',
                                 codes.CODE_INVALID_REQUEST_DATA)


class Range(BaseValidator):

    def __init__(self, lower_bound=None, upper_bound=None, message=None):
        super(Range, self).__init__(message=message)
        if lower_bound is None and upper_bound is None:
            raise ValueError(
                "lower_bound and upper_bound should not be None at the same time.")
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def __call__(self, form, field):
        if field.data > self.upper_bound:
            raise ValidatorError(
                self.message or '{} 数据应小于等于 {}'.format(
                    field.name,
                    self.upper_bound),
                codes.CODE_INVALID_REQUEST_DATA)
        if field.data < self.lower_bound:
            raise ValidatorError(
                self.message or '{} 数据应大于等于 {}'.format(
                    field.name,
                    self.lower_bound),
                codes.CODE_INVALID_REQUEST_DATA)


class TableIdCheck(BaseValidator):
    # 验证表id 是否存在
    def __init__(self, message=None):
        super(TableIdCheck, self).__init__(message=message)

    def __call__(self, form, field):
        table = ''
        if int(form.input_type.data) == 1:
            return
        elif int(form.input_type.data) == 2:
            table = Asset
        elif int(form.input_type.data) == 3:
            table = AssetFile
        if not field.data.isdigit() or (not table.query.get_or_404(int(field.data))):
            raise ValidatorError(self.message or '%s 参数有误' % field.label,
                                 codes.CODE_INVALID_REQUEST_DATA)
