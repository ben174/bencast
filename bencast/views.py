import os
import string
import datetime
import pytz

import settings
from django.http import HttpResponse
from feedgen.feed import FeedGenerator


pacific = pytz.timezone('America/Los_Angeles')

def hs_feed(request):
    title = string.translate('Gur Ubjneq Fgrea Fubj', rot13)
    audio_files = os.listdir('static/hs')
    fg = FeedGenerator()
    fg.load_extension('podcast')
    fg.podcast.itunes_category('Comedy')
    fg.id(title.lower().replace(' ', '-'))
    fg.title(title)
    fg.author({'name': 'Ben', 'email': ''})
    fg.link(href='http://www.bugben.com', rel='alternate')
    fg.subtitle('Ben\'s personal podcast feed.')
    fg.language('en')
    fg.podcast.itunes_image(settings.BASE_URL+'/static/hs.jpg')
    fg.podcast.itunes_image(settings.BASE_URL+'/static/hs.jpg')
    for audio_file in audio_files:
        try:
            fe = fg.add_entry()
            fe.id(audio_file)
            ep_title, date = [x.strip() for x in audio_file.split('-')]
            date = date.split('.')[0]
            year, month, day = [int(d) for d in date.split('_')]
            dt = pacific.localize(datetime.datetime(year, month, day, 0, 0, 0))
            fe.published(dt)
            fe.title('%s: %s/%s/%s' % (ep_title, month, day, year))
            fe.description('%s: %s/%s/%s' % (ep_title, month, day, year))
            fe.enclosure(settings.BASE_URL + '/static/hs/%s' % audio_file, 0, 'audio/mp4a-latm')
        except:
            print 'Error processing file: %s' % audio_file
    return HttpResponse(fg.rss_str(pretty=True))


rot13 = string.maketrans(
    "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
    "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")
