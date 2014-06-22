# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, json
import xbmcplugin, xbmcgui
#from xml.dom import minidom
import xml.etree.ElementTree as ET

def getHTML(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3', 'Content-Type':'application/x-www-form-urlencoded'}
    conn = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))
    
    html = conn.read()
    conn.close()
    
    return html

def isLinkUseful(needle):
    haystack = ['/?do=archive', 'http://www.linecinema.org/', 'http://www.animult.tv/', 
    '/faq.html', '/agreement.html', '/copyright.html', '/reklama.html', '/contacts.html']
    return needle not in haystack

def getMainMenu():
    addDir('Каналы', 'http://podfm.ru/', 10, None)
    addDir('Подкасты', 'http://podfm.ru/rss/programs/rss.xml', 15, None)

def Categories(url):
    html = getHTML(url)
    genre_links = re.compile('<li><a href="(http://podfm.ru/cat/\d+/)"   >').findall(html)
    genre_name = re.compile('<span class="cnt"><span class="namehref">(.+?)</span></span>').findall(html)
    for i in range(0, len(genre_links)):
        addDir(genre_name[i], genre_links[i] + 'rss/rss.xml', 20, None)

def getPodcasts(url):
    html = getHTML(url)
    root = ET.fromstring(html)
    for item in root.find('channel').findall('item'):
        try:
            image = re.compile('src="(.+?)"').findall(item.find('description').text)[0]
            link = item.find('podfm:linkrss', namespaces={'podfm': 'http://podfm.ru/RSS/extension'}).text
            title = item.find('title').text
            addDir(title.encode('utf-8'), link, 20, image)
        except:
            pass


def Tracks(url, page=1):
    html = getHTML(url)
    root = ET.fromstring(html)
    count = 20
    index = 0
    addDir('<< Главная', url, None, None, 1)
    for item in root.find('channel').findall('item'):
        try:
            if index >= ((int(page)-1) * count):
                image = item.find('itunes:image', namespaces={'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}).get('href')
                link = item.find('enclosure').get('url')
                title = item.find('title').text
                addLink(title, link, image)
            index += 1
            if index >= (int(page) * count) + count:
                 addDir('Вперёд >>', url, 20, None, int(page) + 1)
                 break
        except:
            pass
    #xmldoc = minidom.parseString(html)
    #itemlist = xmldoc.getElementsByTagName('channel')[0].getElementsByTagName('item')
    
    #index = 20
    #addLink('TEST', 'http://n9.radio-t.com/rtfiles/rt_podcast396.mp3', None)
    #for item in itemlist:
    #    index-=1
    #    if index > 0:
    #        addLink(item.getElementsByTagName('title')[0].firstChild.nodeValue, item.getElementsByTagName('enclosure')[0].attributes["url"].firstChild.nodeValue, item.getElementsByTagName('itunes:image')[0].attributes["href"].firstChild.nodeValue)

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
                            
    return param


def addLink(title, url, picture):
    if picture == None:
        item = xbmcgui.ListItem(title, iconImage='DefaultAudio.png', thumbnailImage='')
    else:
        item = xbmcgui.ListItem(title, iconImage='DefaultAudio.png', thumbnailImage=picture)
    item.setInfo( type='Music', infoLabels={'Title': title} )
    #item.setInfo(type="Music", infoLabels={"Size": stream['bitrate'] * 1024})
    item.setProperty("IsPlayable", "true")
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=item)


def addDir(title, url, mode, picture, page = None):
    if picture == None:
        item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage='')
    else:
        item = xbmcgui.ListItem(title, iconImage='DefaultFolder.png', thumbnailImage=picture)
    sys_url = sys.argv[0] + '?title=' + urllib.quote_plus(title) + '&url=' + urllib.quote_plus(url) + '&mode=' + urllib.quote_plus(str(mode))
    if page != None :
        sys_url += '&page=' + str(page)
    item.setInfo(type='Audio', infoLabels={'Title': title})
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys_url, listitem=item, isFolder=True)


params = get_params()
url    = None
title  = None
mode   = None
page = 1

try:
    title = urllib.unquote_plus(params['title'])
except:
    pass
try:
    url = urllib.unquote_plus(params['url'])
except:
    pass
try:
    mode = int(params['mode'])
except:
    pass
try:
    page = int(params['page'])
except:
    pass

if mode == None:
    getMainMenu()
if mode == 10:
    Categories(url)
if mode == 15:
    getPodcasts(url)
elif mode == 20:
    Tracks(url, page)

#elif mode == 25:
#    Studios(url, title)

#elif mode == 30:
#    Videos(url, title)

xbmcplugin.endOfDirectory(int(sys.argv[1]))