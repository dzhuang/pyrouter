
import requests
import json
from datetime import datetime
from urllib.parse import quote, unquote


class RouterNotCompatible(Exception):
    pass


class ValidationError(Exception):
    pass


def unquote_dict(d):
    if not isinstance(d, dict):
        return d
    for k, v in d.items():
        if isinstance(v, dict):
            v = unquote_dict(v)
        elif isinstance(v, str):
            v = unquote(v)
        elif isinstance(v, list):
            for i, _v in enumerate(v):
                v[i] = unquote_dict(_v)
        d[k] = v
    return d


def quote_dict(d):
    if not isinstance(d, dict):
        return d
    for k, v in d.items():
        if isinstance(v, dict):
            v = quote_dict(v)
        elif isinstance(v, str):
            v = quote(v)
        elif isinstance(v, list):
            for i, _v in enumerate(v):
                v[i] = quote_dict(_v)
        else:
            # for example, when the value is an int
            v = quote(str(v))
        d[k] = v
    return d


class TpLinkClient(object):
    headers = {'Content-Type': 'application/json; charset=UTF-8'}

    def __init__(self, url, password):
        self.url = url
        self._password = password

        self._stok = None

    @property
    def stok(self):
        if self._stok is not None:
            return self._stok
        self.authenticate()
        return self._stok

    def encrypt_password(self):
        input1 = "RDpbLfCPsJZ7fiv"
        input3 = ("yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43"
                  "odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9a"
                  "Yb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70T"
                  "OoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUy"
                  "VeU3sfQ1xtXcPcf1aT303wAQhv66qzW")
        len1 = len(input1)
        len2 = len(self._password)
        len3 = len(input3)
        output = ''
        if len1 > len2:
            length = len1
        else:
            length = len2
        index = 0
        while index < length:
            cl = 187
            cr = 187
            if index >= len1:
                cr = ord(self._password[index])
            elif index >= len2:
                cl = ord(input1[index])
            else:
                cl = ord(input1[index])
                cr = ord(self._password[index])
            index += 1
            output += chr(ord(input3[cl ^ cr]) % len3)
        return output

    @property
    def _post_url(self):
        return f'{self.url}/stok={self.stok}/ds'

    def _post(self, payload):
        response = requests.post(
            self._post_url, json=quote_dict(payload), headers=self.headers)
        if response.status_code == 200:
            result = response.json()
            return unquote_dict(result)
        return response

    def authenticate(self):
        encrypted_password = self.encrypt_password()
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        payload = {"method": "do", "login": {"password": encrypted_password}}
        response = requests.post(self.url, json=payload, headers=headers)
        try:
            self._stok = response.json()['stok']
        except KeyError:
            raise RouterNotCompatible(
                f"Encrypt Error: {json.dumps(response.json())}"
            )

    def get_all_host_info(self):
        payload = {"hosts_info": {"table": "host_info"}, "method": "get"}
        return self._post(payload)

    def reboot(self):
        payload = {"system": {"reboot": None}, "method": "do"}
        return self._post(payload)

    def get_blocked_devices(self):
        payload = {"hosts_info": {"table": "blocked_host"}, "method": "get"}
        return self._post(payload)

    def set_flux_limit(self, mac, name, down_limit, up_limit, is_blocked=0):
        """
        for example:
            data = {
            "mac": "22-28-6D-95-FD-C9",
            "is_blocked": "0",
            "name": "myiPad",
            "down_limit": "0",
            "up_limit": "0"}

        :param mac:
        :param name:
        :param down_limit: 0 means no limit
        :param up_limit: 0 means no limit
        :param is_blocked:
        :return:
        """
        down_limit = str(down_limit)
        up_limit = str(up_limit)
        is_blocked = str(is_blocked)
        assert is_blocked in ["0", "1"]
        payload = {
            "hosts_info": {
                "set_flux_limit": {
                    "mac": mac,
                    "is_blocked": is_blocked,
                    "name": name,
                    "down_limit": down_limit,
                    "up_limit": up_limit}},
            "method": "do"}
        return self._post(payload)

    def add_limit_time(
            self, limit_time_name, desc_name, start_time, end_time,
            mon=1, tue=1, wed=1, thu=1, fri=1, sat=1, sun=1):
        datetime_pattern = "%H:%M"
        try:
            _start_time = datetime.strptime(start_time, datetime_pattern)
            _end_time = datetime.strptime(end_time, datetime_pattern)
        except ValueError as e:
            msg = (f'start_time and end_time should be in the format of '
                   f'"hh:mm", the error message is: {str(e)}')
            raise ValidationError(msg)
        else:
            if _end_time <= _start_time:
                msg = 'end_time should be latter than start_time'
                raise ValidationError(msg)

        for v in [mon, tue, wed, thu, fri, sat, sun]:
            if str(v) not in ["0", "1"]:
                raise ValidationError(f"{v} should be 0 or 1")

        payload = {"hosts_info": {
            "table": "limit_time", "name": limit_time_name,
            "para": {
                "name": desc_name,
                "mon": mon,
                "tue": tue,
                "wed": wed,
                "thu": thu,
                "fri": fri,
                "sat": sat,
                "sun": sun,
                "start_time": start_time,
                "end_time": end_time}},
            "method": "add"}
        return self._post(payload)

    def query_limit_time(self):
        payload = {"hosts_info": {"table": "limit_time"}, "method": "get"}
        return self._post(payload)

    def delete_limit_time(self, limit_time_name):
        payload = {"hosts_info": {"name": [limit_time_name]}, "method": "delete"}
        return self._post(payload)

    def delete_all_limit_time(self):
        payload = {"hosts_info": {"table": "limit_time"}, "method": "delete"}
        return self._post(payload)


if __name__ == '__main__':
    client = TpLinkClient(url="http://192.168.0.1", password="xxx")
    # print(client.stok)
    # result = client.get_all_host_info()
    # result = client.get_blocked_devices()
    result = client.query_limit_time()
    print(result)

    result = client.add_limit_time(
        limit_time_name="my_time",
        desc_name="what ever",
        start_time="00:00", end_time="1:00")
    print(result)

    result = client.query_limit_time()
    print(result)

    result = client.delete_limit_time(limit_time_name="my_time")
    print(result)

    result = client.query_limit_time()
    print(result)
