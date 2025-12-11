import requests

try:
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    RETRY_AVAILABLE = True
except ImportError:
    RETRY_AVAILABLE = False


class Stream:
    def __init__(self, token):
        self.s = requests.session()
        # Configure retry strategy for better reliability (if available)
        if RETRY_AVAILABLE:
            retry_strategy = Retry(
                total=3,
                backoff_factor=0.3,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.s.mount("http://", adapter)
            self.s.mount("https://", adapter)
        
        # Set default timeout for all requests (can be overridden per request)
        self.default_timeout = 10
        
        self.s.headers.update({
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) StreamlabsDesktop/1.17.0 Chrome/122.0.6261.156 Electron/29.3.1 Safari/537.36",
            "authorization": f"Bearer {token}"
        })

    def search(self, game):
        if not game:
            return []
        game = game[:25] # If the game name exceeds 25 characters, the API will return error 500
        url = f"https://streamlabs.com/api/v5/slobs/tiktok/info?category={game}"
        try:
            response = self.s.get(url, timeout=self.default_timeout)
            response.raise_for_status()
            info = response.json()
            info["categories"].append({"full_name": "Other", "game_mask_id": ""})
            return info["categories"]
        except requests.exceptions.RequestException as e:
            print(f"Search error: {e}")
            return [{"full_name": "Other", "game_mask_id": ""}]

    def start(self, title, category, audience_type='0'):
        url = "https://streamlabs.com/api/v5/slobs/tiktok/stream/start"
        files=(
            ('title', (None, title)),
            ('device_platform', (None, 'win32')),
            ('category', (None, category)),
            ('audience_type', (None, audience_type)),
        )
        try:
            response = self.s.post(url, files=files, timeout=15)
            response.raise_for_status()
            data = response.json()
            self.id = data["id"]
            return data["rtmp"], data["key"]
        except (KeyError, requests.exceptions.RequestException) as e:
            print(f"Start stream error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    print("Response:", e.response.json())
                except:
                    print("Response:", e.response.text)
            return None, None

    def end(self):
        url = f"https://streamlabs.com/api/v5/slobs/tiktok/stream/{self.id}/end"
        try:
            response = self.s.post(url, timeout=self.default_timeout)
            response.raise_for_status()
            data = response.json()
            return data.get("success", False)
        except requests.exceptions.RequestException as e:
            print(f"End stream error: {e}")
            return False
    
    def getInfo(self):
        url = "https://streamlabs.com/api/v5/slobs/tiktok/info"
        try:
            response = self.s.get(url, timeout=self.default_timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Get info error: {e}")
            return {}