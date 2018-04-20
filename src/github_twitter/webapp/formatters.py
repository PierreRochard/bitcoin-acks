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


def user_formatter(view, context, model, name):
    user = getattr(model, name)
    return user.login
