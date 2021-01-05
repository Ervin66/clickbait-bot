# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests


def find_title(url):
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        title = soup.find('title')
        if len(title.text) > 300:
            title.text = title.text[:299]

        return title.text
    except AttributeError:
        headers = {}
        headers['User-agent'] = "HotJava/1.1.2 FCS"
        s = requests.session()
        r = s.get(url, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")
        title = soup.find('title')
        if len(title.text) > 300:
            title.text = title.text[:299]
        return title.text
