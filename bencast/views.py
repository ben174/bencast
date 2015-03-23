import os

from django.http import HttpResponse
from feedgen.feed import FeedGenerator


def feed(request):
    audio_files = os.listdir('static')
    fg = FeedGenerator()
    fg.load_extension('podcast')
    fg.podcast.itunes_category('Technology', 'Podcasting')
    for audio_file in audio_files:
        print audio_file
        fe = fg.add_entry()
        fe.id('http://h.bo.gg:8111/static/%s' % audio_file)
        title, date = [x.strip() for x in audio_file.split('-')]
        fe.title(title + ': ' + date)
        fe.description(title + ': ' + date)
        fe.enclosure('http://h.bo.gg:8111/static/%s' % audio_file, 0, 'audio/mp4a-latm')
    fg.id('howard-stern-show')
    fg.title('The Howard Stern Show')
    fg.author({'name': 'Ben Friedland', 'email': ''})
    fg.link(href='http://bugben.com', rel='alternate')
    fg.subtitle('Ben\'s personal podcast feed.')
    fg.language('en')
    return HttpResponse(fg.rss_str(pretty=True))
