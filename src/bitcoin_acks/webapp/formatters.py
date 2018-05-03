import datetime

import humanize

from markupsafe import Markup


def line_count_formatter(view, context, model, name):
    lines = getattr(model, name)
    if name == 'additions':
        color = '#28a745'
        prefix = '+'
    elif name == 'deletions':
        color = '#cb2431'
        prefix = '-'
    else:
        raise Exception('line_count_formatter mismatch')
    return Markup('<div style="color: {0}">{1}{2:,}</div>'.format(color, prefix, lines))


def body_formatter(view, context, model, name):
    if 'details' in context.name:
        return Markup(model.body)
    full_text = display_text = Markup.striptags(model.body)
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
        now = datetime.datetime.utcnow()
        humanized_date = humanize.naturaltime(now - old_date)
        return Markup('<div title="{0}" style="white-space: nowrap; overflow: hidden;">{1}</div>'.format(old_date, humanized_date))
    else:
        return ''


def pr_link_formatter(view, context, model, name):
    value = getattr(model, name)
    return Markup('<a href="{0}">{1}</a>'.format(model.html_url, value))


def author_link_formatter(view, context, model, name):
    if model.author is None:
        return ''
    return Markup('<div style="white-space: nowrap; overflow: hidden;"><img src="{0}" style="height:16px; border-radius: 50%;"> <a href="{1}" >{2}</a></div>'.format(model.author.avatar_url, model.author.url, model.author.login))


def ack_comment_count_formatter(view, context, model, name):
    comments = getattr(model, 'comments')
    output = ''
    authors = []
    for comment in comments:
        if comment.author.login in authors:
            continue

        if comment.corrected_ack is None:
            ack = comment.auto_detected_ack
        else:
            ack = comment.corrected_ack

        if ack == 'Concept ACK':
            label = 'label-primary'
        elif ack == 'Tested ACK':
            label = 'label-success'
        elif ack == 'utACK':
            label = 'label-warning'
        elif ack == 'NACK':
            label = 'label-danger'
        else:
            raise Exception('unrecognized ack')

        is_stale = model.last_commit_short_hash and model.last_commit_short_hash not in comment.body
        if ack == 'Tested ACK' and is_stale:
            style = 'background-color: #2d672d;'
        elif ack == 'utACK' and is_stale:
            style = 'background-color: #b06d0f'
        else:
            style = ''

        full_text = Markup.escape(comment.body)
        output += '<a href={comment_url} style="color: #FFFFFF; text-decoration: none;">' \
                  '<div style="white-space: nowrap; overflow: hidden;">' \
                  '<img src="{avatar_url}" style="height:16px; border-radius: 50%;">' \
                  ' <span title="{full_text}" class="label {label}" style="{style}">{author_login}</span>' \
                  '</div>' \
                  '</a>'.format(full_text=full_text,
                                label=label,
                                avatar_url=comment.author.avatar_url,
                                author_login=comment.author.login,
                                comment_url=comment.url,
                                style=style)
        authors.append(comment.author.login)
    return Markup(output)


def mergeable_formatter(view, context, model, name):
    if model.merged_at is not None or model.closed_at is not None:
        return ''
    text = getattr(model, name).capitalize()
    if text == 'Mergeable':
        label = 'label-success'
    elif text == 'Conflicting':
        label = 'label-danger'
    elif text == 'Unknown':
        label = 'label-default'
    else:
        raise Exception('unrecognized mergeable status')
    return Markup(' <span class="label {0}">{1}</span>'.format(
        label,
        text))


def last_commit_state_formatter(view, context, model, name):
    if model.merged_at is not None or model.closed_at is not None:
        return ''
    text = getattr(model, name)
    if text == 'Expected' or text == 'Success':
        label = 'label-success'
    elif text == 'Error' or text == 'Failure':
        label = 'label-danger'
    elif text == 'Pending':
        label = 'label-default'
    elif text is None:
        return ''
    else:
        raise Exception('unrecognized last commit status')
    return Markup('<span title="{0}" class="label {1}">{2}</span>'.format(
        model.last_commit_state_description,
        label,
        text))


def labels_formatter(view, context, model, name):
    labels = getattr(model, name)
    output = ''
    for label in labels:
        output += '<a href={label_url} style="color: #FFFFFF; text-decoration: none;">' \
                  '<div style="white-space: nowrap; overflow: hidden;">' \
                  ' <span class="label" style="background-color: #{label_color};" >{label_name}</span>' \
                  '</div>' \
                  '</a>'.format(label_name=label.name,
                                label_url='#',
                                label_color=label.color)
    return Markup(output)
