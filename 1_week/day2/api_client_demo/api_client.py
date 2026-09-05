import requests

class SimpleAPIClient:
    def __init__(self,
                 base_url:str,
                 timeout:int=10,
                 api_key:str|None=None):
        self.base_url=base_url.rstrip("/")
        self.timeout=timeout
        self.api_key=api_key
    def _build_headers(self)->dict:
        headers={
            "Content-Type": "application/json"
        }
        if self.api_key is not None:
            headers["Authorization"]=(f"Bearer {self.api_key}")
        return headers

    def get(self,
            path:str,
            params:dict|None=None,)->dict|None:
        url=self.base_url+path
        try:
            response = requests.get(url=url,
                                    headers=self._build_headers(),
                                    params=params,
                                    timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.Timeout as ee:
            print(f"Get请求超时{ee}")
            return None
        except requests.RequestException as e:
            print(f"GET请求失败{e}")
            return None

    def post(self,
             path:str,
             body:dict|None=None,)->dict|None:
        url=self.base_url+path
        try:
            response = requests.post(url=url,
                                     headers=self._build_headers(),
                                     json=body,
                                     timeout=self.timeout)
            response.raise_for_status()
            data=response.json()
            return data
        except requests.Timeout as ee:
            print(f"POST请求超时{ee}")
            return None
        except requests.RequestException as e:
            print(f"POST请求失败{e}")
