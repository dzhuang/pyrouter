import json
from datetime import datetime
from urllib.request import urlopen

import requests

from .encrypt import encrypt
from .exceptions import RouterNotCompatible, ValidationError
from .utils import unquote_dict, quote_dict


class RouterClient(object):
    headers = {'Content-Type': 'application/json; charset=UTF-8'}

    def __init__(self, url, password, timeout=5):
        self.validate_url(url)
        self.url = url
        self._password = password

        self._stok = None
        self._timeout = timeout

    @classmethod
    def validate_url(cls, url, timeout=5):
        urlopen(url, timeout=timeout)

    @classmethod
    def test_compatible(cls, url, timeout=5):
        payload = {
            "method": "do",
            "login": {"password": ""}
        }
        response = requests.post(url, json=payload, headers=cls.headers,
                                 timeout=timeout)
        try:
            result = response.json()
            # todo: check public key
        except Exception as e:
            raise RouterNotCompatible()

    @property
    def stok(self):
        if self._stok is not None:
            return self._stok
        self.authenticate()
        return self._stok

    @property
    def _post_url(self):
        return f'{self.url}/stok={self.stok}/ds'

    def _post(self, payload):
        response = requests.post(
            self._post_url, json=quote_dict(payload), headers=self.headers,
            timeout=self._timeout)
        if response.status_code == 200:
            result = response.json()
            return unquote_dict(result)
        return response

    def authenticate(self):
        payload = {
            "method": "do",
            "login": {"password": encrypt(self._password)}
        }
        response = requests.post(
            self.url, json=payload, headers=self.headers,
            timeout=self._timeout)
        try:
            self._stok = response.json()['stok']
        except KeyError:
            raise RouterNotCompatible(
                f"Encrypt Error: {json.dumps(response.json())}"
            )

    def get_all_hosts_info(self):
        payload = {"hosts_info": {"table": "host_info"}, "method": "get"}
        return self._post(payload)

    def get_online_hosts_info(self):
        payload = {"hosts_info":
                       {"table": "online_host"},
                   "network": {"name": "iface_mac"},
                   "method": "get"}
        return self._post(payload)

    def get_online_hosts_info_dict(self):
        online_hosts_info = self.get_online_hosts_info()

        online_hosts_info_dict = dict()

        for d in online_hosts_info["hosts_info"]["online_host"]:
            device_info = list(d.values())[0]
            online_hosts_info_dict[device_info["mac"]] = device_info

        return online_hosts_info_dict

    def reboot(self):
        payload = {"system": {"reboot": None}, "method": "do"}
        return self._post(payload)

    def get_blocked_hosts(self):
        payload = {"hosts_info": {"table": "blocked_host"}, "method": "get"}
        return self._post(payload)

    def get_blocked_hosts_info_dict(self):
        blocked_hosts_info = self.get_online_hosts_info()

        blocked_hosts_info_dict = dict()

        for d in blocked_hosts_info["hosts_info"]["blocked_host"]:
            device_info = list(d.values())[0]
            blocked_hosts_info_dict[device_info["mac"]] = device_info

        return blocked_hosts_info_dict

    def set_block_flag(self, mac, is_blocked):
        self.set_host_info_partial(mac, is_blocked=is_blocked)

    def set_flux_limit(self, mac, down_limit, up_limit):
        self.set_host_info_partial(mac, down_limit=down_limit, up_limit=up_limit)

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
            "table": "limit_time",
            "name": limit_time_name,
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

    def add_forbid_domain(self, forbid_domain_name, domain):
        payload = {
            "hosts_info": {"table": "forbid_domain", "name": forbid_domain_name,
                           "para": {"domain": domain}}, "method": "add"}
        return self._post(payload)

    def delete_forbid_domain(self, forbid_domain_name):
        payload = {"hosts_info": {"name": [forbid_domain_name]}, "method": "delete"}
        return self._post(payload)

    def delete_all_forbid_domains(self):
        payload = {"hosts_info": {"table": "forbid_domain"}, "method": "delete"}
        return self._post(payload)

    def set_host_info(self, mac, name, is_blocked, down_limit, up_limit, forbid_domain, limit_time):

        mac = str(mac)

        if isinstance(is_blocked, bool):
            is_blocked = "1" if is_blocked else "0"

        info_dict = {
            "mac": mac,
            "name": name,
            "is_blocked": is_blocked,
            "down_limit": down_limit,
            "up_limit": up_limit,
            "forbid_domain": forbid_domain,
            "limit_time": limit_time
        }

        payload = {
            "hosts_info": {"set_host_info": info_dict}, "method": "do"}
        return self._post(payload)

    def set_host_info_partial(self, mac, **kwargs):
        if not kwargs:
            return {}

        mac = str(mac)

        host_info = self.get_host_info_by_mac(mac)
        allowed_keys = ["mac", "name", "is_blocked", "down_limit",
                        "up_limit", "forbid_domain", "limit_time"]
        for k in host_info:
            if k not in allowed_keys:
                host_info.pop(k)

        host_info.update(**kwargs)
        return self.set_host_info(**kwargs)

    def set_host_limit_time(self, mac, limit_time):
        return self.set_host_info_partial(mac, limit_time=limit_time)

    def set_host_forbid_domain(self, mac, forbid_domain):
        return self.set_host_info_partial(mac, forbid_domain=forbid_domain)

    def get_all_host_info_dict(self):
        all_host_info = self.get_all_hosts_info()

        all_host_info_dict = dict()

        for d in all_host_info["hosts_info"]["host_info"]:
            device_info = list(d.values())[0]
            all_host_info_dict[device_info["mac"]] = device_info

        return all_host_info_dict

    def get_host_info_by_mac(self, mac):
        mac = str(mac)
        return self.get_all_host_info_dict()[mac]


if __name__ == '__main__':
    client = RouterClient(url="http://192.168.0.1", password="xxx")
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
