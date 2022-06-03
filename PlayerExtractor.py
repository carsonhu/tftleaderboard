"""Extract Player Data:

This file should get the list of matches

Get Player LP's according to preassigned timestamp list

Get Player's icon

to filter out data:
sort data every hour.
get list of top 50 at every hour (only 2000 hours)
remove all players who were never top 50.
"""
import json
import os
from datetime import datetime, timedelta
from consts import DATA_DIR, START_DATE, END_DATE

class PlayerExtractor(object):
    def __init__(self, filename):
        self.name = os.path.splitext(filename)[0]
        self.filename = DATA_DIR + filename
        self.playerDict = {}
        with open(self.filename, mode='r', encoding='utf-8') as f:
            self.playerDict = json.load(f)
        
        # Convert timestamp to date time
        if 'rankHistory' in self.playerDict:
            rankHistory = self.playerDict['rankHistory']
            for rank in rankHistory:
                rank[0] = datetime.fromtimestamp(int(rank[0]/1000.0))            

    def rankHistory(self):
        return self.playerDict['rankHistory']

    def profilePic(self):
        current_patch="12.6.1"
        icon_id = self.playerDict['playerInfo']['profileIconId']
        url = "http://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png".format(current_patch, icon_id)
        return url

    def getRank(self, rank):
        # rank[1] = division
        # rank[2] = LP
        if 'MASTER' in rank[1] or 'CHALLENGER' in rank[1]:
            return (rank[1], rank[2])
        else:
            # below masters gets set to 0 lp
            return (rank[1], 0)

    def getPlayerLPs(self, start_date, end_date, increment):
        # TODO: Really need to write test cases for this
        # for each entry you have (league, LP)
        # if there are none you have (None, 0)
        if not self.playerDict:
            return {}

        dateDict = {} # what LP is the player by this date?
        current_date = start_date
        history_pointer = 0
        previous_entry = (0,0)

        while current_date < end_date:
            if history_pointer < len(self.rankHistory()) and self.rankHistory()[history_pointer][0] < current_date:
                while self.rankHistory()[history_pointer][0] < current_date:
                    dateDict[current_date] = self.getRank(self.rankHistory()[history_pointer])
                    previous_entry = dateDict[current_date]
                    history_pointer += 1
                    if history_pointer >= len(self.rankHistory()):
                        break
            else:
                dateDict[current_date] = previous_entry
            current_date += increment
        return dateDict

if __name__ == "__main__":
    player_extractor = PlayerExtractor("Luishas.json")
    dateDict = player_extractor.getPlayerLPs(START_DATE,
                                             END_DATE,
                                             timedelta(minutes=1))
    #print(player_extractor.filename)
    print(dateDict)
