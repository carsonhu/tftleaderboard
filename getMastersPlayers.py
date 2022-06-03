"""Get list of Master Players

Attributes:
    api_key (str): Description
    challs (TYPE): Description
    f (TYPE): Description
    filename (str): Description
    gms (TYPE): Description
    masters (TYPE): Description
    my_region (str): Description
    tft_watcher (TYPE): Description
"""

from riotwatcher import TftWatcher, ApiError

# Replace with your riot games API Key
api_key = '---'

tft_watcher = TftWatcher(api_key)

my_region = 'na1'

masters = tft_watcher.league.master(my_region)
gms = tft_watcher.league.grandmaster(my_region)
challs = tft_watcher.league.challenger(my_region)
# masters,gms, chall = [tier, leagueid, queue, name, entries]
# name is just league name, leesin's guardians  
# tier is MASTER
# queue is RANKED_TFT


filename = 'masterList.txt'
f = open("masterList.txt",'w+', encoding='utf-8')
for entry in [*masters['entries'], *gms['entries'], *challs['entries']]:
    print(entry['summonerName'], file=f)
    # save Master list
