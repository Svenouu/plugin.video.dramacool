# -*- coding: utf-8 -*-
"""
    KShows - Korea Drama/TV Shows Streaming Service
"""

import xbmc
import xbmcgui
import urllib2
import urlparse
import re
import requests
import json
from bs4 import BeautifulSoup
import resolver

UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"

def getSoup(url):
    if url.startswith('//'):
        url = 'http:' + url
    req = urllib2.Request(url)
    req.add_header('User-Agent', UserAgent)
    req.add_header('Referer', 'https://kshows.to/')
    resp = urllib2.urlopen(req)
    doc = resp.read()
    resp.close()
    return BeautifulSoup(doc, from_encoding='utf-8')

def parseProgList(main_url):
    soup = getSoup(main_url)

    result = {'link':[]}
    for item in soup.find("ul", {"class":"items"}).findAll("li", {"class":"video-block"}):
        thumb = ""
        if item.a:
            name = item.find("div", {"class":"name"})
            img = item.find("img")
            if img:
                thumb = item.img['src']
            result['link'].append({'title':name.text.strip(), 'url':item.a['href'], 'thumbnail':thumb})

    # navigation
    pagination = soup.find("ul", {"class":"pagination"})
    if pagination:
        cur = pagination.find("li", {"class":"active"})
        li = cur.findPreviousSibling("li")
        if li and li.a and li.a.text.isdigit():
            url = li.a['href']
            result['prevpage'] = url
        li = cur.findNextSibling("li")
        if li and li.a and li.a.text.isdigit():
            url = li.a['href']
            result['nextpage'] = url
    return result

def extract_video_url(url):
    page = getSoup(url)

    iframe = page.find('iframe')
    if iframe:
        vid_url = iframe['src']

        page = getSoup(vid_url)
    
        embedVids = page.findAll("li", {"class":"linkserver"})

        page = None
        if embedVids:
            urlsFound = {}
            for embedVid in embedVids:
                datavideo = embedVid['data-video'] 
                if datavideo:
                    urlsFound[embedVid.text] = datavideo
            if urlsFound:
                dialog = xbmcgui.Dialog()
                ret = dialog.select('Choose source', urlsFound.keys())
                if ret >= 0:
                    return resolver.resolve_video_url(urlsFound.values()[ret])
    return url

if __name__ == "__main__":
    pass

# vim:sts=4:sw=4:et
