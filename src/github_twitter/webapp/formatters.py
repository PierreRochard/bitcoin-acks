from bs4 import BeautifulSoup

from markupsafe import Markup


def body_formatter(view, context, model, name):
    body = getattr(model, name)
    soup = BeautifulSoup(body)
    text = soup.get_text()
    if text:
        return text[0:100] + '...'
    else:
        return ''


def pr_link_formatter(view, context, model, name):
    value = getattr(model, name)
    return Markup('<a href="{0}">{1}</a>'.format(model.html_url, value))


def user_link_formatter(view, context, model, name):
    return Markup('<a href="{0}">{1}</a>'.format(model.user.html_url, model.user.login))
