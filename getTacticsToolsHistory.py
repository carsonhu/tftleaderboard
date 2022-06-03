"""Gets detailed match history from tactics.tools
"""

import requests
import time
import json
import os

# list of all masters+ players
MASTERS_LIST = "masterList.txt"
DATA_DIR = "data/"


def getMastersPlayersList(filename):
    with open(filename, encoding='utf-8') as f:
        return f.read().splitlines()

def requestFromTacticsTools(name):
    # Get a Player's profile from tactics.tools API
    api_url = "https://legendsapi.com/player-stats-cached-all/na1/{}/65/0".format(name)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"}

    retries = 0
    success = False
    while not success and retries < 5:
        try:
            response = requests.get(api_url, headers=headers)
            success = True
        except requests.exceptions.ConnectionError as errc:
            retries += 1
            print(retries)
    return response.json()

if __name__ == "__main__":
    masters = getMastersPlayersList(MASTERS_LIST)
    print(masters)
    for i in range(len(masters)):
        print(masters[i])

        filename = DATA_DIR + masters[i] + '.json'
        if os.path.isfile(filename) and os.stat(filename).st_size != 0:
            continue
        time.sleep(.5)
        with open(filename, mode='w', encoding='utf-8') as f:
            response = requestFromTacticsTools(masters[i])
            json.dump(response, f)
