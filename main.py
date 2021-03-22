# -*- coding: utf-8 -*-
import praw
import time
import os
import portali as pt
import bot_login
import time
import meaningcloud
import nltk
from nltk import word_tokenize, sent_tokenize
from prawcore.exceptions import ResponseException
from praw.exceptions import APIException
from prawcore.exceptions import PrawcoreException
import traceback
import pdb
import get_title as t
import re
import pdb
# meaning cloud API
license_key = "3668d6e355b00b38ff7d1b46c45c97de"
get_fibo = False


number_categories = 3
# @param topics_relevance - Relevance used for filtering entities and concepts
topics_relevance = 80

cluster_score_threshold = 50

# statements
bot_statement = "***Ja sam bot protiv clickbaita, ako smatrate da je ovaj članak kvalitetan podržite ga klikom!***" + \
    "\n" + "**Cilj je prepustiti odluku 'klika' na temelju članka, ne naslova.**" + "\n\n"
end_statement = "*Greška ili imaš prijedlog za poboljšanje? Pošalji mi [pm](https://www.reddit.com/message/compose/?to=bot_protiv_clickbait)*"
error_statement = "hmm, nesto se dogodilo"
too_long_statement = "**Ovo je sažetak članka**:" + "\n\n"
upute = "Ako smatrate da je ovaj clanak clickbait upišite **!clickbait** i suprotno **!notclickbait** (u normalnom fontu)." + "\n" + "Glasanje je ograničeno na jedan glas po korisniku za svaki članak."

# nltk.download('punkt')
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')


class Bot():
    """docstring for Bot"""

    def __init__(self):
        self.subr = ["croatia"]
        self.portali_dic = {"vecernji.hr": pt.vecernji_parser,
                            "amp.index.hr": pt.ampindex_parser,
                            "www.index.hr": pt.index_parser,
                            "www.jutarnji.hr": pt.jutarnji_parser,
                            "www.rtl.hr": pt.rtl_parser,
                            "24sata.hr": pt.d24sata_parser,
                            "hr.n1info.com": pt.n1_parser,
                            "telegram.hr": pt.telegram_parser,
                            "hrvatska-danas.com": pt.hr_danas_parser,
                            "www.dnevnik.hr": pt.dnevnik_parser,
                            "slobodnadalmacija.hr": pt.slobodna_parser,
                            "glasistre.hr": pt.glasistre_parser,
                            "nacional.hr": pt.nacional_parser,
                            "www.net.hr": pt.nethr_parser,
                            "tportal.hr": pt.tportal_parser,
                            "sportnet.rtl.hr": pt.sportnet_parser,
                            "maxportal.hr": pt.maxportal_parser,
                            "bug.hr": pt.bug_parser,
                            "dalmatinskiportal.hr": pt.dalportal_parser,
                            "poslovni.hr": pt.poslovni_parser,
                            "kamenjar.com": pt.kamenjar_parser,
                            "direktno.hr": pt.direktno_parser
                            }
        self.timer = 3
        self.posts_replied_to = self.save_comments()

    def post_tracker(self, sub_id):
        self.posts_replied_to.append(sub_id)
        with open("posts_track.txt", "a") as f:
            f.write(sub_id + "\n")
        print(f"{sub_id} added to blacklist")

    def save_comments(self):
        if not os.path.isfile("posts_track.txt"):
            posts_replied_to = []
        else:
            with open("posts_track.txt", "r") as f:
                posts_replied_to = f.read()
                posts_replied_to = posts_replied_to.split("\n")
                posts_replied_to = list(filter(None, posts_replied_to))
        return posts_replied_to

    def getSummarization(self, text, sentences):
        # We are going to make a request to the Summarization API
        summary = ''
        summarization_response = meaningcloud.SummarizationResponse(
            meaningcloud.SummarizationRequest(license_key,
                                              sentences=sentences,
                                              txt=text).sendReq())
        if summarization_response.isSuccessful():
            summary = summarization_response.getSummary()

        else:
            print("\tOops! Request to Summarization was not succesful: (" 
                + summarization_response.getStatusCode() + ') ' 
                + summarization_response.getStatusMsg())

        return summary.replace("[...]", "[...]" + "\n\n" + ">")

    def broj_recenica(self):
        self.recenice = tokenizer.tokenize(self.clanak)
        target_sentence = 0
        if len(self.recenice) < 30:
            target_sentence = int(round(len(self.recenice) / 3))
        elif len(self.recenice) >= 30:
            target_sentence = 10
        return target_sentence

    def duplicate(self, sub_id):
        is_duplicate = False
        submission = r.submission(id=sub_id)
        for comment in submission.comments:
            if comment.author == "bot_protiv_clickbait":
                is_duplicate = True
        return is_duplicate

    def find_url(string):
        # findall() has been used
        # with valid conditions for urls in string
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        url = re.findall(regex, string)
        return [x[0] for x in url]

    def verify_url(self, url, sub_id):
        if ".jpg" in url[-5:]:
            self.post_tracker(sub_id)
        else:
            return True

    def post_summary(self):
        self.posts_replied_to = self.save_comments()
        for submission in r.subreddit("croatia").stream.submissions():
            self.submission = submission
            for key in self.portali_dic:
                if key in self.submission.url and submission.id not in self.posts_replied_to:
                    try:
                        self.clanak = self.portali_dic[key](self.submission.url)
                        recenice = tokenizer.tokenize(self.clanak)
                        dupla = self.duplicate(submission.id)
                        link_slike = self.verify_url(submission.url, submission.id) #check extension of url, skip if url is to a file extension

                    except AttributeError:
                        print("new error handling")
                        self.post_tracker(submission.id)
                        continue

                    if dupla is False and link_slike is True:
                        if len(recenice) <= 10:
                            self.content = f"{self.clanak}" +"\n" + f"[originalni link]({submission.url})" +"\n\n" + upute + "\n\n" + f"{end_statement}"
                            self.repost()
                            self.content = f"{self.clanak}" +"\n" + f"[originalni link]({submission.url})" +"\n\n" + f"{bot_statement}" + "\n" + f"{end_statement}" + "\n\n" + self.link2vote
                            self.reply = submission.reply(self.content)
                            self.post_tracker(submission.id)
                            time.sleep(self.timer)
                        else:
                            self.sazetak = self.getSummarization(self.clanak, self.broj_recenica())
                            self.content = too_long_statement + "\n\n" + f">{self.sazetak}" + "\n\n" + f"[originalni link]({submission.url})" + "\n\n" + upute + "\n\n" + f"{end_statement}"
                            self.own_sub = self.repost()
                            if self.own_sub is False:
                                continue
                                continue
                            else:
                                self.content = too_long_statement + "\n\n" + f">{self.sazetak}" + "\n\n" + f"[originalni link]({submission.url})" + "\n\n" + f"{bot_statement}" + "\n" + f"{end_statement}" + "\n\n" + self.link2vote
                                self.reply = submission.reply(self.content)
                                self.post_tracker(submission.id)
                                time.sleep(self.timer)


    def repost(self):
        r.validate_on_submit = True
        try:
            html_title = t.find_title(self.submission.url)
            subreddit = r.subreddit("bot_protiv_clickbait").submit(title=html_title, url=self.submission.url)
            sub_link = r.submission(id=subreddit)
            print(sub_link.id)
            stick_comment = sub_link.reply(self.content)
            stick_comment.mod.distinguish(sticky=True)
            self.link2vote = f"[Ovdje](https://old.reddit.com/r/bot_protiv_clickbait/comments/{sub_link.id}) možeš glasat je li članak clickbait ili ne."
            return self.link2vote
        except AttributeError as a:
            self.post_tracker(self.submission.id)
            return False


r = bot_login.login()
bot = Bot()


while True:
    try:
        bot.post_summary()
    except praw.exceptions.RedditAPIException as error:
        time.sleep(300)
        print("pauza")
        continue

    except PrawcoreException:
        time.sleep(300)
        print('prawcore')
        continue
    except ConnectionResetError:
        time.sleep(300)
    except AttributeError as a:
        print(a)
        traceback.print_exc()
        print(bot.submission.url)
        time.sleep(30)
        bot.post_tracker(bot.submission.url)
        print("exception added")
        continue




'''
to fix
use library to convert html to markdown
https://old.reddit.com/r/croatia/comments/k256fy/zbog_pogor%C5%A1ane_situacije_s_koronavirusom_od_30/gds4oqz/
'''


#add another script to manually exclude