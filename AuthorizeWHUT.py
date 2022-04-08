import datetime
import json
import requests
import re
import base64
from urllib.parse import urlparse
from Core.BaseTask import BaseTask
from Core.HCY import HCYRequest
from Core.multi_user import load_users
import netifaces


class AuthorizeManager(BaseTask):
    def __init__(self, _user_cookie: str, _user_name, debug=False):
        self._user_cookie = _user_cookie
        super().__init__("武汉理工校园网认证", "1.1.1.1", user_name)
        if debug:
            self.notify('====================='.join([json.dumps(netifaces.ifaddresses(i), ensure_ascii=False, indent=4)
                                                      for i in netifaces.interfaces()]))
        self.hcy = HCYRequest()
        self.interface = self.select_interfaces(netifaces.interfaces())

    @staticmethod
    def select_interfaces(interfaces):
        for i in interfaces:
            if netifaces.AF_INET in netifaces.ifaddresses(i):
                for j in netifaces.ifaddresses(i)[netifaces.AF_INET]:
                    if j['addr'] != '127.0.0.1':
                        return i
        return None

    def is_connected_wifi(self):
        return self.interface is not None

    @staticmethod
    def based64(password):
        return base64.b64encode(password.encode('utf-8')).decode('utf-8')

    @staticmethod
    def detect_acid(request_result):
        """this function performs javascript below:
        var p=/\/index_([\d]+).html/;
        var arr=p.exec(document.location);
        if(arr[1])
        {
            location="ac_detect.php?"+"ac_id="+arr[1]+"&"+document.location.search.substring(1);
        }
        """
        p = r'/index_([\d]+).html'
        url = urlparse(request_result.url)
        arr = re.search(p, url.path).group(1)
        if arr:
            r = requests.request('get', url[0] + "://" + url[1] + "/ac_detect.php?" + "ac_id=" + arr + "&" + url.query)\
                .text
            return re.search(r'"ac_id" value="(\d+)"', r).group(1), r, url.hostname
        return -1, "", "localhost"

    def sign_in(self):
        acid, html, host = self.detect_acid(requests.request('get', self.get_redirect()))
        self.hcy.build_from_hcy("whut.edu/auth_action.hcy")
        self.hcy.url = "http://" + host + self.hcy.url
        self.hcy.data['username'] = self.query_from_cookie("username", self._user_cookie)
        self.hcy.data['password'] = '{B}' + self.based64(self.query_from_cookie("password", self._user_cookie))
        self.hcy.data['ac_id'] = acid
        self.hcy.data['user_ip'] = re.search(r'"user_ip" value="(.*)"', html).group(1)
        self.hcy.data['nas_ip'] = re.search(r'"nas_ip" value="(.*)"', html).group(1)
        self.hcy.data['user_mac'] = re.search(r'"user_mac" value="(.*)"', html).group(1)
        r = self.hcy.request()
        self.notify(r.text)

    def get_redirect(self):
        """
        有时候是自动302
        有时候是html的跳转代码
        """
        r = self._verify_network()
        if r.history:
            # 302
            return r.url
        else:
            return re.search(r'(https*://.*)\'', r.text).group(1)

    def verify_network(self):
        data = self._verify_network()
        return data.status_code == 204 if data else False

    @staticmethod
    def _verify_network():
        return requests.get('http://connect.rom.miui.com/generate_204')

    def start(self):
        if self.is_connected_wifi():
            net_status = self.verify_network()
            if not net_status:
                self.notify("campus network authorizing.")
                self.sign_in()
            else:
                self.notify("authorized.")
                time_now = datetime.datetime.now()
                # hour-level log
                if time_now.minute >= 5:
                    return
        else:
            self.notify("please connect to a wifi.")
        self.save()


'''
cron:  */5 * * * * python auto_login.py
'''
if __name__ == '__main__':
    for user_name, user_cookie in load_users('whut.edu/user.hcy'):
        AuthorizeManager(_user_cookie=user_cookie, _user_name=user_name, debug=False).start()
