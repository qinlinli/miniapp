import time, json, base64, hmac, hashlib, copy
import requests
from urllib.parse import urljoin, urlparse


def get_header(method, data, all_url, ak, sk, ts):
    ts = ts or int(time.time())
    qs = {}
    secret_key = sk

    # 准备数据
    to_encrypt = copy.copy(qs)
    to_encrypt['ts'] = ts
    if method == 'GET':
        to_encrypt.update(data)
    elif method == 'POST':
        to_encrypt['body'] = json.dumps(data)

    # 排序
    to_encrypt = to_encrypt.items()
    to_encrypt = sorted(to_encrypt, key=lambda x: x[0])

    # 串联
    to_encrypt = ['%s=%s' % (_[0], _[1]) for _ in to_encrypt]
    string = '&'.join(to_encrypt)
    url = urlparse(all_url).path
    string += url
    print(string)
    # string = 'body={"title":"这是一个测试","desc":null,"contact":"18913138918","mobile":null,"address":"苏州玲珑湾花园1-201","project_code":"32050001","house_code":null,"business_type":"BUCR030108","report_user_mobile":"18913131313","report_user_type":"1","appointment_time":"2019-03-22 15:01:01","image":null}&ts=1553225272/api/partner/tasks/crm'

    # hmac python2
    # encrypted = hmac.new(secret_key, string, hashlib.sha256).digest()

    # hmac python3
    encrypted = hmac.new(bytearray(secret_key, 'utf-8'), bytearray(string, 'utf-8'), hashlib.sha256).digest()
    print(hmac.new(bytearray(secret_key, 'utf-8'), bytearray(string, 'utf-8'), hashlib.sha256).hexdigest())
    # base64
    token = base64.urlsafe_b64encode(encrypted)

    # python3
    token = token.decode('utf-8')
    print(token)

    header = {
        'X-3rd-Auth-Version': '2',
        'X-TS': str(ts),
        'X-AccessKey': ak,
        'Authorization': 'Bearer %s' % token,
    }
    return string, token, header




