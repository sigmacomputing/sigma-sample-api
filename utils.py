import time

import requests


def get_base_url(cloud: str, env: str):
    print(env)
    print(cloud)
    base_url = ''
    if env == 'dev':
        base_url = 'http://127.0.0.1:8081'
    elif cloud == 'gcp':
        if env == 'staging':
            base_url = 'https://api.staging.sigmacomputing.io'
        elif env == 'prod' or env == 'production':
            base_url = 'https://api.sigmacomputing.com'
    elif cloud == 'aws':
        if env == 'staging':
            base_url = 'https://staging-aws-api.sigmacomputing.io'
        elif env == 'prod' or env == 'production':
            base_url = 'https://aws-api.sigmacomputing.com'
    return base_url


def get_access_token(base_url, client_id, client_secret):
    """ Gets the access token from Sigma
        :client_id:     Client ID generated from Sigma
        :client_secret: Client secret generated from Sigma
        :returns:       Access token
    """
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(f"{base_url}/v2/auth/token", data=payload)
    data = response.json()
    return data["access_token"]


def get_headers(access_token):
    """ Gets headers for API requests
        :access_token:  Generated access token
        :returns:       Headers for API requests
    """
    return {"Authorization": "Bearer " + access_token}


class SigmaClient():
    def __init__(self, env, cloud, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = get_base_url(cloud, env)
        self.headers = self._get_headers()

    def _get_headers(self):
        return get_headers(get_access_token(self.base_url, self.client_id, self.client_secret))

    def post(self, path, **kwargs):
        return self._exec(requests.post, path, **kwargs)

    def get(self, path, **kwargs):
        return self._exec(requests.get, path, **kwargs)

    def put(self, path, **kwargs):
        return self._exec(requests.put, path, **kwargs)

    def delete(self, path, **kwargs):
        return self._exec(requests.delete, path, **kwargs)

    def patch(self, path, **kwargs):
        return self._exec(requests.patch, path, **kwargs)

    def _exec(self, func, path, retries=5, exc=None, **kwargs):
        if retries < 0:
            raise exc
        try:
            url = f'{self.base_url}/{path}'
            headers: dict = kwargs.pop('headers', {})
            headers.update(self.headers)
            response = func(url, headers=headers, **kwargs)
            if response.status_code == 401:
                self.headers = self._get_headers()
                headers.update(self.headers)
                response = func(url, headers=headers, **kwargs)
            return response
        except requests.exceptions.ConnectionError as e:
            time.sleep(1)
            return self._exec(func, path, retries - 1, exc=e, **kwargs)
