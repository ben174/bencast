import datetime

import os
from lxml import html
import requests


def weekday_to_xpath(index):
    paths = [
        (2, 1),
        (2, 2),
        (4, 1),
        (4, 2),
        (6, 1),
    ]
    return '/html/body/table/tr[%s]/td[%s]' % paths[index]

def date_to_url(date):
    date = date_to_monday(date)
    y, m, d = str(date.year)[-2:], date.month, date.day
    return 'http://marksfriggin.com/news{}/{}-{}.htm'.format(y, m, d)

def date_to_monday(in_date):
    return in_date + datetime.timedelta(days=-in_date.weekday())

def get_show_description(query_date):
    url = date_to_url(query_date)
    page = requests.get(url)
    tree = html.fromstring(page.text)
    xpath = weekday_to_xpath(query_date.weekday())
    elem = tree.xpath(xpath)[0]
    return elem.text_content().strip()


def get_description(date):
    path = 'static/desc/%s-%s-%s.txt' % (date.year, date.month, date.day)
    if os.path.isfile(path):
        f = open(path, 'r')
        return f.read()
    print 'description not cached. fetching: %s' % date
    f = open(path, 'wb')
    description = get_show_description(date)
    f.write(description)
    f.flush()
    f.close()
    return description
