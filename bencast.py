from flask import Flask, Response, request
from bencast.util import hss

import os
import string
import datetime
import pytz
import re

from feedgen.feed import FeedGenerator

pacific = pytz.timezone('America/Los_Angeles')

class BencastFeedGenerator(FeedGenerator):
    def __init__(self, title, prefix, *args, **kwargs):
        super(FeedGenerator, self).__init__()

app = Flask(__name__)

'''
import boto3
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
bucket = s3.Bucket('bencast')
for key in bucket.objects.filter(Prefix='hh/', Delimiter='/'):
'''

import boto
import boto.s3.connection
import environment

conn = boto.connect_s3(
    aws_access_key_id = environment.ACCESS_KEY_ID,
    aws_secret_access_key = environment.SECRET_ACCESS_KEY,
)
bucket = conn.get_bucket('bencast')



@app.route("/")
def home():
    return "Go away."

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
    feed.podcast.itunes_image('/static/' + prefix + '.jpg')

def get_description(date):
    path = 'static/desc/%s-%s-%s.txt' % (date.year, date.month, date.day)
    if os.path.isfile(path):
        f = open(path, 'r')
        return f.read()
    print 'description not cached. fetching: %s' % date
    f = open(path, 'wb')
    description = hss.get_show_description(date)
    f.write(description)
    f.flush()
    f.close()
    return description

@app.route("/al")
def al_feed():
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
            fe.enclosure(request.url_root + '/static/al/%s' % audio_file, 0, 'audio/mp4a-latm')
        except Exception as e:
            print 'Error processing file: %s' % audio_file
            print str(e)
    return Response(fg.rss_str(pretty=True), mimetype='application/rss+xml')


@app.route("/hh")
def hh_feed():
    title = string.translate('Gur Uvfgbel bs Ubjneq Fgrea', rot13)
    fg = FeedGenerator()
    configure_feed(fg, title, 'hh')

    for key in bucket.list("hh/", ""):
        audio_file = key.key[3:]
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
            fe.enclosure(key.generate_url(expires_in=300), 0, 'audio/mp4a-latm')
        except:
            print 'Error processing file: %s' % audio_file
    return Response(fg.rss_str(pretty=True), mimetype='application/rss+xml')

@app.route("/hs")
def hs_feed():
    title = string.translate('Gur Ubjneq Fgrea Fubj', rot13)
    fg = FeedGenerator()
    configure_feed(fg, title, 'hs')
    audio_files = os.listdir('static/hs')
    for audio_file in audio_files:
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
        fe.enclosure(request.url_root + '/static/hs/%s' % audio_file, 0, 'audio/mp4a-latm')
    return Response(fg.rss_str(pretty=True), mimetype='application/rss+xml')


rot13 = string.maketrans(
    "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
    "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")

if __name__ == "__main__":
    app.run(debug=True)
