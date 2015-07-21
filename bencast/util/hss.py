import datetime

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

query_date = datetime.date(2015, 07, 8)
print get_show_description(query_date)

