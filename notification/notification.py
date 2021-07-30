import os
import json
import threading
import aiohttp
import asyncio
from django.conf import settings

class SingletonMetaClass(type):
    """
    Metaclass for single class
    """
    instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__call__(*args, **kwargs)
        return cls.instance


class NotificationWorker(metaclass=SingletonMetaClass):

    def __init__(self):
        self._thread = threading.Thread(target=self.__run_loop)
        self._thread.daemon = True
        self.loop = None

    def __run_loop(self):
        self.loop = asyncio.get_event_loop_policy().new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start(self):
        self._thread.start()

    def get_loop(self):
        if self.loop is not None:
            return self.loop
        return None


class Notification(metaclass=SingletonMetaClass):
    """
    Notification class use to publish notification on notification service via rest APIs.
    """
    __session = None

    TYPE_EMAIL = 'E'
    TYPE_MSG = 'M'
    TYPE_PUSH = 'P'
    TYPE_FEED = 'F'
    TYPE_HOME = 'H'

    EVENT_SIGNUP = 'SignUp'
    EVENT_LOGIN = 'Login'
    EVENT_FORGOT_PWD = 'ForgotPassword'
    EVENT_CONTACT_INVITE = 'InviteContact'
    EVENT_RECIEVE_DEAL_REQUEST = 'RecieveDealRequest'
    EVENT_NEW_MESSAGE = 'RecievedNewMessage'

    def __init__(self):
        self.host = settings.NOTIFICATION_HOST
        self.api = settings.NOTIFICATION_API

    async def __get_session(self):
        if self.__session is None:
            timeout = aiohttp.ClientTimeout(total=60)
            self.__session = aiohttp.ClientSession(timeout=timeout)
        return self.__session

    async def __publish(self, url, payload):
        # call get session coroutine
        session = await self.__get_session()
        print('url', url)
        print('data', json.dumps(payload))
        async with session.post(url, data=json.dumps(payload), headers={'content-type': 'application/json', 'Authorization': ''}) as response:
            print('******res', await response.text())
            return response


    @staticmethod
    def __get_event_loop():
        try:
            loop = asyncio.get_event_loop()
            return loop
        except RuntimeError as e:
            return asyncio.new_event_loop()

    def publish(self, title, body, to_user, _type, event):
        # TODO remove seen
        payload = {'title': title, 'body': body, 'to_user': to_user, 'event': event, 'type': _type, 'seen': 'False'}
        url = os.path.join(self.host, self.api)
        print(f'url {url}')
        print(f'payload {payload}')
        notification_worker = NotificationWorker()
        loop = notification_worker.get_loop()
        if loop is not None:
            asyncio.run_coroutine_threadsafe(self.__publish(url, payload), loop=loop)







