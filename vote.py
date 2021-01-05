# -*- coding: utf-8 -*-

import praw
import requests
from bs4 import BeautifulSoup
import pandas as pd
import bot_login
import json
import time
 

class VoteCount():
    """docstring for VoteCOunt"""

    def __init__(self):
        self.portali_dic = {"vecernji.hr": "Večernji",
                            "amp.index.hr": "Index",
                            "www.index.hr": "Index",
                            "www.jutarnji.hr": "Jutarnji",
                            "www.rtl.hr": "RTL",
                            "24sata.hr": "24 sata",
                            "hr.n1info.com": "N1 info",
                            "telegram.hr": "telegram",
                            "hrvatska-danas.com": "Hrvatska-Danas",
                            "dnevnik.hr": "Dnevnik.hr",
                            "slobodnadalmacija.hr": "Slobodna Dalmacija",
                            "glasistre.hr": "Glas Istre",
                            "nacional.hr": "Nacional",
                            "www.net.hr": "Net.hr",
                            "tportal.hr": "Tportal",
                            "sportnet.rtl.hr": "Sportnet RTL",
                            "maxportal.hr": "MaxPortal",
                            "bug.hr": "bug.hr"
                            "dalmatinskiportal.hr": "Dalmatinski Portal"
                            }

        with open('user.json') as f:
            self.user_dic = json.load(f)        

        # self.df = pd.DataFrame(
            # columns=["sub_id", "submission url", "portal", "good vote", "bad vote"])
        self.df = pd.read_csv("out.csv", header=0, index_col=0)


    def listen(self):
        for comment in r.subreddit("bot_protiv_clickbait").stream.comments(pause_after=2):
            if comment is None:
                time.sleep(600)
                break

            try:
                if "!clickbait" in comment.body:
                    if comment.author not in self.user_dic[comment.link_id[3:]]:
                    # if comment.author not in self.user_df.loc[self.user_df.sub_id ==comment.link_id[3:]]:
                        self.df.loc[self.df.sub_id == comment.link_id[3:], ["bad vote"]] += 1
                        self.user_dic[comment.link_id[3:]].append(str(comment.author))
                        self.df.to_csv("out.csv")
                        with open('user.json', 'w') as f:
                            json.dump(self.user_dic, f)

                if "!notclickbait" in comment.body:
                    if comment.author not in self.user_dic[comment.link_id[3:]]:
                        self.df.loc[self.df.sub_id == comment.link_id[3:], ["good vote"]] += 1
                        self.user_dic[comment.link_id[3:]].append(str(comment.author))
                        self.df.to_csv("out.csv")
                        with open('user.json', 'w') as f:
                            json.dump(self.user_dic, f)
            except KeyError:
                self.user_dic[comment.link_id[3:]] = []
                continue




    def append2df(self):
        for submission in r.subreddit("bot_protiv_clickbait").stream.submissions(pause_after=2):
            if submission is None:
                time.sleep(600)
                break
            for key in self.portali_dic:
                if key in submission.url:
                    if submission.id not in self.df["sub_id"].values:
                        s_goodvote = 0
                        s_badvote = 0
                        data = pd.Series({"sub_id": submission.id,
                                          "submission url": submission.url,
                                          "portal": self.portali_dic[key],
                                          "good vote": s_goodvote,
                                          "bad vote": s_badvote})
                        self.df.loc[len(self.df)] = data
                        self.user_dic[submission.id] = []
                        self.df.to_csv("out.csv")
                        with open('user.json', 'w') as f:
                            json.dump(self.user_dic, f)



r = bot_login.login()

v = VoteCount()
while True:
    v.append2df()
    v.listen()