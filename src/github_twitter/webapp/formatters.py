import datetime

import humanize
from bs4 import BeautifulSoup

from markupsafe import Markup


def body_formatter(view, context, model, name):
    body = getattr(model, name)
    soup = BeautifulSoup(body)
    text = soup.get_text()
    if text:
        return Markup('<div title="{0}">{1}</div>'.format(text, text[0:100] + '...'))
    else:
        return ''


def humanize_date_formatter(view, context, model, name):
    old_date = getattr(model, name)
    if old_date is not None:
        now = datetime.datetime.now()
        humanized_date = humanize.naturaltime(now - old_date)
        return Markup('<div title="{0}">{1}</div>'.format(old_date, humanized_date))
    else:
        return ''


def pr_link_formatter(view, context, model, name):
    value = getattr(model, name)
    return Markup('<a href="{0}">{1}</a>'.format(model.html_url, value))


def user_link_formatter(view, context, model, name):
    return Markup('<a href="{0}">{1}</a>'.format(model.user.html_url, model.user.login))
