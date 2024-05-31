import requests
import os
from pprint import pprint

url = "https://api.princeofcrypto.com/v1/{}"

X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")


headers = {
    "x-api-key": X_API_KEY,
    "x-api-secret": X_API_SECRET,
    "Content-Type": "application/json",
}


def get_current_watchlist():
    url_get = url.format("coin/watch")
    response = requests.get(url_get, headers=headers)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    pprint(get_current_watchlist())
