import datetime
import os

import environment

from lxml import html
import requests
import boto


conn = boto.connect_s3(
    aws_access_key_id = environment.ACCESS_KEY_ID,
    aws_secret_access_key = environment.SECRET_ACCESS_KEY,
)
bucket = conn.get_bucket('bencast')

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

cache = {}

def get_description(date):
    path = 'desc/%s-%s-%s.txt' % (date.year, date.month, date.day)

    # try local cache
    ret = cache.get(path)
    if ret:
        return ret

    # try s3 cache
    key = bucket.get_key(path)
    if key:
        ret = key.read()
        cache[path] = ret
        return ret

    # scrape description and cache it
    print 'Scraping description for: {}'.format(date)
    ret = get_show_description(date)
    key = boto.s3.key.Key(bucket)
    key.key = path
    key.set_contents_from_string(ret)
    cache[path] = ret

    return ret
