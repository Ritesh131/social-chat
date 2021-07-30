import redis
import json

POOL = redis.ConnectionPool(host='session', port=6379, db=1, password=None, socket_timeout=None)


class RemoteTokenStorage(object):

    client = None

    def __init__(self):
        try:
            self.client = redis.Redis(connection_pool=POOL)
            self.client.client_list()
        except Exception as e:
            raise e

    def set_token(self, token, user_id):
        self.client.set(token, json.dumps({"user_id": user_id}))

    def get_token(self, token):
        user = self.client.get(token)
        if user:
            user = json.loads(user)
        return user
