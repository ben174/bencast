import datetime
import string

import pytz
import re
from flask import Flask, Response
from functools import wraps
from flask import request, Response
import boto

from util.feed import BencastFeedGenerator
from util.fs import get_keys
from util.hss import get_description
import environment

conn = boto.connect_s3(
    aws_access_key_id = environment.ACCESS_KEY_ID,
    aws_secret_access_key = environment.SECRET_ACCESS_KEY,
)
bucket = conn.get_bucket('bencast')


pacific = pytz.timezone('America/Los_Angeles')

app = Flask(__name__)


def check_auth(username, xwrd):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == environment.USERNAME and xwrd == environment.PASSWORD

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def home():
    return "Go away."


@app.route("/al")
@requires_auth
def al_feed():
    title = string.translate('Negvr Ynatr Cbqpnfg', rot13)
    fg = BencastFeedGenerator()
    fg.configure(title, 'al')
    for item in bucket.list(prefix='hh/'):
        audio_file = item.key[3:]
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
            fe.enclosure('http://listen.bugben.com/proxy/al/{}'.format(audio_file), 0, 'audio/mp4a-latm')
        except Exception as e:
            print 'Error processing file: %s' % audio_file
            print str(e)
    return Response(fg.rss_str(pretty=True), mimetype='application/rss+xml')


@app.route("/hh")
@requires_auth
def hh_feed():
    title = string.translate('Gur Uvfgbel bs Ubjneq Fgrea', rot13)
    fg = BencastFeedGenerator()
    fg.configure(title, 'hh')

    for item in bucket.list(prefix='hh/'):
        audio_file = item.key[3:]
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
            fe.enclosure('http://listen.bugben.com/proxy/hh/{}'.format(audio_file), 0, 'audio/mp4a-latm')
        except:
            print 'Error processing file: %s' % audio_file
    return Response(fg.rss_str(pretty=True), mimetype='application/rss+xml')

@app.route("/hs")
@requires_auth
def hs_feed():
    title = string.translate('Gur Ubjneq Fgrea Fubj', rot13)
    fg = BencastFeedGenerator()
    fg.configure(title, 'hs')
    for item in bucket.list(prefix='hs/'):
        audio_file = item.key[3:]
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
        fe.enclosure('http://listen.bugben.com/proxy/hs/{}'.format(audio_file), 0, 'audio/mp4a-latm')
    return Response(fg.rss_str(pretty=True), mimetype='application/rss+xml')


@app.route('/proxy/<path:path>')
@requires_auth
def static_proxy(path):
    key = boto.s3.key.Key(bucket)
    key.key = path

    try:
        key.open_read()
        headers = dict(key.resp.getheaders())
        return Response(key, headers=headers)
    except boto.exception.S3ResponseError as e:
        return flask.Response(e.body, status=e.status, headers=key.resp.getheaders())


rot13 = string.maketrans(
    "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
    "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")

# precache
for item in bucket.list(prefix='hs/'):
    try:
        audio_file = item.key[3:]
        ep_title, date = [x.strip() for x in audio_file.split('-')]
        date = date.split('.')[0]
        year, month, day = [int(d) for d in date.split('_')]
        dt = datetime.datetime(year, month, day, 0, 0, 0)
        dt = pacific.localize(dt)
        print 'Caching description for: {} ({})'.format(ep_title, date)
        description = get_description(dt)
    except:
        print 'Error processing: {}'.format(item.key)

if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
    )
