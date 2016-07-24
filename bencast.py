import datetime
import string

import pytz
import re
from flask import Flask, Response
from util.feed import BencastFeedGenerator
from util.fs import get_keys
from util.hss import get_description

pacific = pytz.timezone('America/Los_Angeles')

app = Flask(__name__)



@app.route("/")
def home():
    return "Go away."


@app.route("/al")
def al_feed():
    title = string.translate('Negvr Ynatr Cbqpnfg', rot13)
    fg = BencastFeedGenerator()
    fg.configure(title, 'al')
    for key in get_keys('al'):
        audio_file = key.key[3:]
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
            fe.enclosure(key.generate_url(expires_in=300), 0, 'audio/mp4a-latm')
        except Exception as e:
            print 'Error processing file: %s' % audio_file
            print str(e)
    return Response(fg.rss_str(pretty=True), mimetype='application/rss+xml')


@app.route("/hh")
def hh_feed():
    title = string.translate('Gur Uvfgbel bs Ubjneq Fgrea', rot13)
    fg = BencastFeedGenerator()
    fg.configure(title, 'hh')

    for key in get_keys('hh'):
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
    fg = BencastFeedGenerator()
    fg.configure(title, 'hs')
    for key in get_keys('hs'):
        audio_file = key.key[3:]
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
        fe.enclosure(key.generate_url(expires_in=300), 0, 'audio/mp4a-latm')
    return Response(fg.rss_str(pretty=True), mimetype='application/rss+xml')


rot13 = string.maketrans(
    "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
    "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")

if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
    )
