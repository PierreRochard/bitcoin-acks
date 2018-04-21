import datetime

import humanize

from markupsafe import Markup


def line_count_formatter(view, context, model, name):
    lines = getattr(model.diff, name.split('.')[-1])
    if 'add' in name:
        color = '#28a745'
        prefix = '+'
    elif 'remove' in name:
        color = '#cb2431'
        prefix = '-'
    else:
        raise Exception('line_count_formatter mismatch')
    return Markup('<div style="color: {0}">{1}{2:,}</div>'.format(color, prefix, lines))


def body_formatter(view, context, model, name):
    full_text = display_text = Markup.escape(model.body)
    max_length = 200
    if len(full_text) > max_length:
        display_text = full_text[0:max_length]
        display_text += '...'
    if full_text:
        return Markup('<div title="{0}">{1}</div>'.format(full_text, display_text))
    else:
        return ''


def humanize_date_formatter(view, context, model, name):
    old_date = getattr(model, name)
    if old_date is not None:
        now = datetime.datetime.now()
        humanized_date = humanize.naturaltime(now - old_date)
        return Markup('<div title="{0}" style="white-space: nowrap; overflow: hidden;">{1}</div>'.format(old_date, humanized_date))
    else:
        return ''


def pr_link_formatter(view, context, model, name):
    value = getattr(model, name)
    return Markup('<a href="{0}">{1}</a>'.format(model.html_url, value))


def user_link_formatter(view, context, model, name):
    return Markup('<div style="white-space: nowrap; overflow: hidden;"><img src="{0}" style="height:16px; border-radius: 50%;"> <a href="{1}" >{2}</a></div>'.format(model.user.avatar_url, model.user.html_url, model.user.login))
