import os
import string
import datetime
import pytz
import re

import settings
from django.http import HttpResponse
from feedgen.feed import FeedGenerator
from util import hss


pacific = pytz.timezone('America/Los_Angeles')


class BencastFeedGenerator(FeedGenerator):
    def __init__(self, title, prefix, *args, **kwargs):
        super(FeedGenerator, self).__init__()

def configure_feed(feed, title, prefix):
    feed.prefix = prefix
    feed.load_extension('podcast')
    feed.podcast.itunes_category('Comedy')
    feed.id(title.lower().replace(' ', '-'))
    feed.title(title)
    feed.author({'name': 'Ben', 'email': ''})
    feed.link(href='http://www.bugben.com', rel='alternate')
    feed.subtitle('Ben\'s personal podcast feed.')
    feed.language('en')
    feed.podcast.itunes_image(settings.BASE_URL+'/static/' + prefix + '.jpg')

def get_description(date):
    path = 'static/desc/%s-%s-%s.txt' % (date.year, date.month, date.day)
    if os.path.isfile(path):
        f = open(path, 'r')
        return f.read()
    print 'description not cached. fetching: ' % date
    f = open(path, 'wb')
    description = hss.get_show_description(date)
    f.write(description)
    f.flush()
    f.close()
    return description

def al_feed(request):
    title = string.translate('Negvr Ynatr Cbqpnfg', rot13)
    fg = FeedGenerator()
    configure_feed(fg, title, 'al')
    audio_files = os.listdir('static/al')
    for audio_file in audio_files:
        try:
            fe = fg.add_entry()
            fe.id(audio_file)
            print audio_file
            ep_title, date, _, _, _ = [x.strip() for x in audio_file.split('_')]
            date = date.split('.')[0]
            year, month, day = [int(d) for d in date.split('-')]
            dt = pacific.localize(datetime.datetime(year, month, day, 0, 0, 0))
            fe.published(dt)
            fe.title('%s: %s/%s/%s' % (ep_title, month, day, year))
            fe.description('%s: %s/%s/%s' % (ep_title, month, day, year))
            fe.enclosure(settings.BASE_URL + '/static/al/%s' % audio_file, 0, 'audio/mp4a-latm')
        except Exception as e:
            print 'Error processing file: %s' % audio_file
            print str(e)
    return HttpResponse(fg.rss_str(pretty=True), content_type='application/rss+xml')


def hh_feed(request):
    title = string.translate('Gur Uvfgbel bs Ubjneq Fgrea', rot13)
    fg = FeedGenerator()
    configure_feed(fg, title, 'hh')
    audio_files = os.listdir('static/hh')
    for audio_file in audio_files:
        try:
            fe = fg.add_entry()
            fe.id(audio_file)
            matches = re.findall('Stern-(...._.._..).*cf\-(.*).mp3', audio_file)
            date, ep_title = matches[0]
            year, month, day = [int(d) for d in date.split('_')]
            dt = pacific.localize(datetime.datetime(year, month, day, 0, 0, 0))
            fe.published(dt)
            title = '%s: %s/%s/%s' % (ep_title, month, day, year)
            title = title.replace('_', ' ')
            title = title.replace('(', ' ')
            title = title.replace(')', ' ')
            fe.title(title)
            fe.description(title)
            fe.enclosure(settings.BASE_URL + '/static/hh/%s' % audio_file, 0, 'audio/mp4a-latm')
        except:
            print 'Error processing file: %s' % audio_file
    return HttpResponse(fg.rss_str(pretty=True), content_type='application/rss+xml')

def hs_feed(request):
    title = string.translate('Gur Ubjneq Fgrea Fubj', rot13)
    fg = FeedGenerator()
    configure_feed(fg, title, 'hs')
    audio_files = os.listdir('static/hs')
    for audio_file in audio_files:
        try:
            fe = fg.add_entry()
            fe.id(audio_file)
            ep_title, date = [x.strip() for x in audio_file.split('-')]
            date = date.split('.')[0]
            year, month, day = [int(d) for d in date.split('_')]
            dt = datetime.datetime(year, month, day, 0, 0, 0)
            description = get_description(dt)
            dt = pacific.localize(dt)
            fe.published(dt)
            fe.title('%s: %s/%s/%s' % (ep_title, month, day, year))
            fe.description(description)
            fe.enclosure(settings.BASE_URL + '/static/hs/%s' % audio_file, 0, 'audio/mp4a-latm')
        except Exception as e:
            print 'Error processing file: %s' % audio_file
            print str(e)
            print e.message
    return HttpResponse(fg.rss_str(pretty=True), content_type='application/rss+xml')


rot13 = string.maketrans(
    "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
    "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")
