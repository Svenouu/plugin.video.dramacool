# -*- coding: utf-8 -*-
"""
    KShows
"""
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
from xbmcgui import ListItem
from xbmcplugin import addDirectoryItem, endOfDirectory
from xbmcswift2 import Plugin
import urllib
import sys
import os
import re
from YDStreamExtractor import getVideoInfo

addon = xbmcaddon.Addon()
plugin = Plugin()
_L = plugin.get_string

plugin_path = addon.getAddonInfo('path')
url_root = 'https://kshows.to'
lib_path = os.path.join(plugin_path, 'resources', 'lib')
sys.path.append(lib_path)

import kshows

tPrevPage = u"[B]<%s[/B]" % _L(30100)
tNextPage = u"[B]%s>[/B]" % _L(30101)

@plugin.route('/')
def main_menu():
    addDirectoryItem(
                plugin.handle,
                plugin.url_for('search_list', searchTerms='-', page='-'),
                ListItem(label='Search'), True)
    addDirectoryItem(
                plugin.handle,
                plugin.url_for('prog_list', cate='-', page='-'),
                ListItem(label='Recently Added Sub'), True)
    addDirectoryItem(
                plugin.handle,
                plugin.url_for('prog_list', cate='recently-added-raw', page='-'),
                ListItem(label='Recently Added Raw'), True)
    addDirectoryItem(
                plugin.handle,
                plugin.url_for('prog_list', cate='movies', page='-'),
                ListItem(label='Drama - Movies'), True)
    addDirectoryItem(
                plugin.handle,
                plugin.url_for('prog_list', cate='kshow', page='-'),
                ListItem(label='Kshows'), True)
                
    xbmcplugin.endOfDirectory(plugin.handle)

@plugin.route('/search/<searchTerms>/<page>/')
def search_list(searchTerms, page):
    if searchTerms == '-':
        keyboard = xbmc.Keyboard()
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            search_list(keyboard.getText(), '-')
    else:
        if page == '-' :
            pageN = 1 
        else:
            pageN = int(page)

        url = url_root + '/search.html?keyword=%s&page=%d' % (searchTerms, pageN)

        result = kshows.parseProgList(url)
        createVideoDirectory(result, searchTerms, pageN, True)
    return main_menu()


@plugin.route('/category/<cate>/<page>/')
def prog_list(cate, page):
    if cate == '-' :
        category = ''
    else:
        category = cate
    if page == '-' :
        pageN = 1 
    else:
        pageN = int(page)
    
    if pageN == 1 :
        url = url_root + '/%s' % (category)
    else:
        url = url_root + '/%s?page=%d' % (category, pageN)

    result = kshows.parseProgList(url)
    
    createVideoDirectory(result, cate, pageN, False)

def createVideoDirectory(result, cateOrSearchTerms, pageN, isSearch):
    listing = []
    for video in result['link']:
        list_item = xbmcgui.ListItem(label=video['title'], thumbnailImage=video['thumbnail'])
        list_item.setInfo('video', {'title': video['title']})
        url = plugin.url_for('play_video', url=video['url'])
        is_folder = True
        listing.append((url, list_item, is_folder))
    
    xbmcplugin.addDirectoryItems(plugin.handle, listing, len(listing))
    
    if 'prevpage' in result:
        if isSearch:
            addDirectoryItem(
                plugin.handle,
                plugin.url_for('search_list', searchTerms=cateOrSearchTerms, page=pageN-1),
                ListItem(tPrevPage), True)
        else:
            addDirectoryItem(
                plugin.handle,
                plugin.url_for('prog_list', cate=cateOrSearchTerms, page=pageN-1),
                ListItem(tPrevPage), True)
    if 'nextpage' in result:
        if isSearch:
            addDirectoryItem(
                plugin.handle,
                plugin.url_for('search_list', searchTerms=cateOrSearchTerms, page=pageN+1),
                ListItem(tNextPage), True)
        else:
            addDirectoryItem(
                plugin.handle,
                plugin.url_for('prog_list', cate=cateOrSearchTerms, page=pageN+1),
                ListItem(tNextPage), True)

    xbmcplugin.endOfDirectory(plugin.handle)

@plugin.route('/play/<url>/')
def play_video(url):
    if url_root not in url:
        url = url_root + url
    url = kshows.extract_video_url(url)
    info = None
    
    if not url.startswith("plugin://"):
        info = getVideoInfo(url, quality=3, resolve_redirects=True)
    if info:
        streams = info.streams()
        plugin.log.debug("num of streams: %d" % len(streams))
        from xbmcswift2 import xbmc, xbmcgui
        pl = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
        pl.clear()
        for stream in streams:
            li = xbmcgui.ListItem(stream['title'], iconImage="DefaultVideo.png")
            li.setInfo( 'video', { "Title": stream['title'] } )
            pl.add(stream['xbmc_url'], li)
        xbmc.Player().play(pl)
    else:
        plugin.log.warning('Fallback to '+url)
        plugin.play_video({'path':url, 'is_playable':True})
    return plugin.finish(None, succeeded=False)     # trick not to enter directory mode

if __name__ == "__main__":
    plugin.run()

# vim:sw=4:sts=4:et
