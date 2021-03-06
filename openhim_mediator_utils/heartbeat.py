import requests
import urllib3

from uptime import uptime
from apscheduler.schedulers.background import BackgroundScheduler


class Heartbeat:
    def __init__(self, auth, **kwargs):
        self.auth = auth
        self.options = kwargs['options']
        self.__scheduler = BackgroundScheduler()
        self.__job = None
        self.conf = kwargs['conf']

    def _send(self, force_config=False):
        body = {'uptime': uptime()}
        if force_config or self.options['force_config']:
            body['config'] = True

        if not self.options['verify_cert']:
            urllib3.disable_warnings(
                urllib3.exceptions.InsecureRequestWarning
            )

        mediators_url = f"{self.options['apiURL']}/mediators/{self.conf['urn']}/heartbeat"
        response = requests.post(
            url=mediators_url,
            verify=self.options['verify_cert'],
            json=body,
            headers=self.auth.gen_auth_headers()
        )

        if response.status_code is not 200:
            raise Exception(
                f"Heartbeat unsuccessful, received status code of {response.status_code}"
            )

    def activate(self):
        self.auth.authenticate()
        if not self.__job:
            self.__job = self.__scheduler.add_job(
                self._send,
                'interval',
                seconds=self.options['interval'] or 10
            )
            self.__scheduler.start()

    def deactivate(self):
        if self.__job is not None:
            self.__job.remove()

    def fetch_config(self):
        self.auth.authenticate()
        return self._send(True)
