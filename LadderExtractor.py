# goal:
# say we want to get top 10 timelapse per 15 minute interval
# 1st: look through everyone. for each timestamp, get each player's rank
# for each timestamp, sort list by LP (masters+ only)
# if player is in top [30], add to whitelist
# once we have full whitelist, filter only to those players
# this player list now in our excel sheet
import json
import os
import PlayerExtractor
import numpy as np
import xlsxwriter
import csv
from collections import Counter
from datetime import datetime, timedelta
from consts import DATA_DIR, START_DATE, END_DATE
class LadderExtractor(object):
    def filterRankList(self, sortedRankDict, topThreshold):
        # key: date
        # value: list (name, (league, LP))
        # topThreshold: threshold of top players to filter through
        playerSet = set()
        for key in sortedRankDict.keys():
            topPlayers = [s[0] for s in sortedRankDict[key]][-topThreshold:]
            playerSet.update(topPlayers)
        return playerSet
  
    def sortFullRankList(self, rankList):
        # input: datedicts: Key = Name, value = dict{date, (league, LP)}
        # warning that this is an expensive operation so don't do it to filter by seconds
        # for each key in value dict, we create a new sorted list of LPs

        # bro it's a one-time expense Copium
        keys = list(list(rankList.values())[0].keys())

        rankDict = {}
        for key in keys: # for each date, we want to return a sorted list of keys
            sortedList = sorted(rankList.items(), key = lambda item: item[1][key][1])
            filteredList = filter(lambda item: item[1][key][0] != 0 and ('MASTER' in item[1][key][0] or 'CHALLENGER' in item[1][key][0]), sortedList)
            filtered = [(s[0],s[1][key]) for s in list(filteredList)]
            rankDict[key] = filtered
        return rankDict

    def getFullRankList(self, interval, playerList=None):
        dateDicts = {}
        if playerList == None:
            files = os.listdir(DATA_DIR)
        else:
            # we have the names
            files = [name + ".json" for name in playerList]
        for filename in files:
            player_extractor = PlayerExtractor.PlayerExtractor(filename)
            if not player_extractor.playerDict:
                continue
            dateDicts[player_extractor.name] = player_extractor.getPlayerLPs(START_DATE,
                                                     END_DATE,
                                                     interval)
        return dateDicts

    def getTopPlayers(self, interval, topThreshold):
        # with the list of top players we get the finer version
        fullRankList = self.getFullRankList(interval)
        rankDict = self.sortFullRankList(fullRankList)
        topPlayers = self.filterRankList(rankDict, topThreshold)
        return topPlayers

    def getKingOfLeague(self, interval, league):
        fullRankList = self.getFullRankList(interval)

        keys = list(list(fullRankList.values())[0].keys())

        kingCounter = Counter()
        for key in keys:
            # for each date, find the king
            #print([fullRankList[name][key][0] for name in fullRankList])
            leaguePlayers = [(name, fullRankList[name][key][1]) for name in fullRankList.keys() if fullRankList[name][key][0] == league]
            if len(leaguePlayers) > 0:
                kingCounter[max(leaguePlayers, key = lambda item: item[1])[0]] += interval.total_seconds() / (3600*24)
        return kingCounter

    def getGatekeeperOfLeague(self, interval):
        fullRankList = self.getFullRankList(interval)
        gatekeeperCounter = {}
        for name, dateDict in fullRankList.items():
            if name not in gatekeeperCounter:
                gatekeeperCounter[name] = [0,0]
            leagues = [lp[0] for lp in dateDict.values()]
            for i in range(len(leagues) - 1):
                if leagues[i] == "CHALLENGER I" and leagues[i+1] == "GRANDMASTER I":
                    gatekeeperCounter[name][0] += 1    
                elif leagues[i] == "GRANDMASTER I" and leagues[i+1] == "MASTER I":
                    gatekeeperCounter[name][1] += 1
        return gatekeeperCounter



    def createCSV(self, csv_file, topList, sortedList, top_threshold):
        #topList: key Name, value: (Date, (league, LP))
        #csvfile: 1 column for each date
        keys = list(list(topList.values())[0].keys())
        headers_arr = [date.strftime("%m/%d/%Y, %H:%M:%S") for date in list(keys)]
        headers_arr = ['Name', 'Icon'] + headers_arr
        #print(headers_arr)

        # datetime (NOTE: ASSUMES ALL DATES ARE EQUALLY SPACED)
        # want to convert this into terms of days
        dt = (keys[1] - keys[0]).total_seconds() / (3600 * 24)
        workbook = xlsxwriter.Workbook('lp_history.xlsx')
        worksheet = workbook.add_worksheet('LP')
        worksheet1st = workbook.add_worksheet('First')
        worksheet.write_row(0, 0, headers_arr)
        worksheet.freeze_panes(1, 0)

        worksheet1st.write_row(0, 0, headers_arr)
        worksheet1st.freeze_panes(1, 0)
        index = 0

        topPlayers = self.getTopPlayerDurationDict(sortedList, top_threshold)

        for name, val in topList.items():
            new_entry = []
            new_entry.append(name)

            # get icon
            filename = name + ".json"
            player_extractor = PlayerExtractor.PlayerExtractor(filename)
            new_entry.append(player_extractor.profilePic())

            new_entry2 = new_entry.copy()
            new_entry2 += list(np.cumsum([(name in topPlayers[key]) * dt for key in keys]))
            new_entry += [v[1] for v in val.values()]
            worksheet.write_row(index+1, 0, new_entry)
            worksheet1st.write_row(index+1, 0, new_entry2)
            index += 1
        workbook.close()
        return 0

    # def getTopPlayerDurationDict(self, sortedList):
    #     # we just want to get top player duration for each
    #     # this is dict tho
    #     topDictionary = {}
    #     for key in sortedList:
    #         if len(sortedList[key]) > 0:
    #             if len(sortedList[key]) > 1 and sortedList[key][-1][1][1] == sortedList[key][-2][1][1]:
    #                 print(sortedList[key][-1], sortedList[key][-2])
    #             topPlayer = sortedList[key][-1]
    #             topDictionary[key] = topPlayer[0]
    #             #topDictionary[topPlayer[0]] += 1/48 # 30 minutes
    #         else:
    #             topDictionary[key] = 0
    #     return topDictionary

    def getTopPlayerDurationDict(self, sortedList, top_threshold):
        # we just want to get top player duration for each
        # this is dict tho
        topDictionary = {}
        for key in sortedList:
            if key not in topDictionary:
                topDictionary[key] = []
            if len(sortedList[key]) > 0:
                for i in range(top_threshold):
                    if len(sortedList[key]) >= i + 1:
                        topPlayer = sortedList[key][-i-1]
                        topDictionary[key].append(topPlayer[0])
        return topDictionary

    def getTopPlayerDuration(self, interval, sortedList):
        # we just want to get top player duration for each
        topCounter = Counter()        
        for key in sortedList:
            if len(sortedList[key]) > 0:
                topPlayer = sortedList[key][-1]
                topCounter[topPlayer[0]] += interval.total_seconds() / (3600 * 24) # 30 minutes
        return topCounter
    
    def getTopPlayerDurations(self, interval, sortedList, top_threshold):
        # we just want to get top player duration for each
        topCounter = Counter()        
        for key in sortedList:
            if len(sortedList[key]) > 0:
                for i in range(top_threshold):
                    if len(sortedList[key]) >= i + 1:
                        topPlayer = sortedList[key][-i-1]
                        topCounter[topPlayer[0]] += interval.total_seconds() / (3600 * 24) # 30 minutes
        return topCounter

def create_counter_csv(counter, textfile):
    with open(textfile, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for key, count in counter.items():
            writer.writerow([key, count])


if __name__ == "__main__":
    ladderExtractor = LadderExtractor()
    potentialTop10s = ladderExtractor.getTopPlayers(timedelta(hours=12), 50)
    #print(potentialTop10s)
    # after this you want to get the full rank list (interval: 30 mins) for these players
    interval = timedelta(minutes = 30)
    top10FullRankList = ladderExtractor.getFullRankList(interval, potentialTop10s)
    sortedList = ladderExtractor.sortFullRankList(top10FullRankList)
    ladderExtractor.createCSV("a", top10FullRankList, sortedList, 10)

    # getting top player duration    
    counter = ladderExtractor.getTopPlayerDurations(interval, sortedList, 10)
    create_counter_csv(counter, "top10list.csv")
    #with open("counter.txt", mode='w', encoding='utf-8') as f:
    #    print(counter, file=f)
