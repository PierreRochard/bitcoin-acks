import datetime

import humanize
from markupsafe import Markup
import webcolors

from bitcoin_acks.constants import ReviewDecision
from bitcoin_acks.models import Bounties


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
    max_length = 100
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
        now = datetime.datetime.now(datetime.timezone.utc)
        try:
            humanized_date = humanize.naturaltime(now - old_date)
        except TypeError:
            raise

            return ''
        return Markup('<div title="{0}" style="white-space: nowrap; overflow: hidden;">{1}</div>'.format(old_date, humanized_date))
    else:
        return ''


def pr_link_formatter(view, context, model, name):
    if isinstance(model, Bounties):
        model = model.pull_request
        name = name.split('.')[-1]
    closed_icon = '<div style="white-space: nowrap; overflow: hidden;" >{link} <svg style="fill: #cb2431;" width="12" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M11 11.28V5c-.03-.78-.34-1.47-.94-2.06C9.46 2.35 8.78 2.03 8 2H7V0L4 3l3 3V4h1c.27.02.48.11.69.31.21.2.3.42.31.69v6.28A1.993 1.993 0 0 0 10 15a1.993 1.993 0 0 0 1-3.72zm-1 2.92c-.66 0-1.2-.55-1.2-1.2 0-.65.55-1.2 1.2-1.2.65 0 1.2.55 1.2 1.2 0 .65-.55 1.2-1.2 1.2zM4 3c0-1.11-.89-2-2-2a1.993 1.993 0 0 0-1 3.72v6.56A1.993 1.993 0 0 0 2 15a1.993 1.993 0 0 0 1-3.72V4.72c.59-.34 1-.98 1-1.72zm-.8 10c0 .66-.55 1.2-1.2 1.2-.65 0-1.2-.55-1.2-1.2 0-.65.55-1.2 1.2-1.2.65 0 1.2.55 1.2 1.2zM2 4.2C1.34 4.2.8 3.65.8 3c0-.65.55-1.2 1.2-1.2.65 0 1.2.55 1.2 1.2 0 .65-.55 1.2-1.2 1.2z"></path></svg></div>'

    merged_icon = '<div style="white-space: nowrap; overflow: hidden;" >{link} <svg style="fill: #6f42c1;" width="12" height="16" aria-hidden="true"><path d="M10 7c-.73 0-1.38.41-1.73 1.02V8C7.22 7.98 6 7.64 5.14 6.98c-.75-.58-1.5-1.61-1.89-2.44A1.993 1.993 0 0 0 2 .99C.89.99 0 1.89 0 3a2 2 0 0 0 1 1.72v6.56c-.59.35-1 .99-1 1.72 0 1.11.89 2 2 2a1.993 1.993 0 0 0 1-3.72V7.67c.67.7 1.44 1.27 2.3 1.69.86.42 2.03.63 2.97.64v-.02c.36.61 1 1.02 1.73 1.02 1.11 0 2-.89 2-2 0-1.11-.89-2-2-2zm-6.8 6c0 .66-.55 1.2-1.2 1.2-.65 0-1.2-.55-1.2-1.2 0-.65.55-1.2 1.2-1.2.65 0 1.2.55 1.2 1.2zM2 4.2C1.34 4.2.8 3.65.8 3c0-.65.55-1.2 1.2-1.2.65 0 1.2.55 1.2 1.2 0 .65-.55 1.2-1.2 1.2zm8 6c-.66 0-1.2-.55-1.2-1.2 0-.65.55-1.2 1.2-1.2.65 0 1.2.55 1.2 1.2 0 .65-.55 1.2-1.2 1.2z"></path></svg></div>'
    if getattr(model, 'merged_at'):
        html = merged_icon
    elif getattr(model, 'closed_at'):
        html = closed_icon
    else:
        html = '{link}'
    value = getattr(model, name)
    link = '<a target=blank href="{0}">{1}</a>'.format(model.html_url, value)
    return Markup(html.format(link=link))


def author_link_formatter(view, context, model, name):
    if model.author is None:
        return ''
    return Markup('<div style="white-space: nowrap; overflow: hidden;"><img src="{0}" style="height:16px; border-radius: 50%;"> <a target=blank href="{1}" >{2}</a></div>'.format(model.author.avatar_url, model.author.url, model.author.login))


def review_decisions_formatter(view, context, model, name):
    output = ''
    authors = []
    is_details = 'details' in context.name
    comments = getattr(model, 'review_decisions')
    last_commit_short_hash = model.last_commit_short_hash

    for comment in comments:
        if comment.author.login in authors:
            continue

        if comment.review_decision == ReviewDecision.CONCEPT_ACK:
            label = 'label-primary'
        elif comment.review_decision == ReviewDecision.TESTED_ACK:
            label = 'label-success'
        elif comment.review_decision == ReviewDecision.UNTESTED_ACK:
            label = 'label-warning'
        elif comment.review_decision == ReviewDecision.NACK:
            label = 'label-danger'
        else:
            continue

        is_stale = last_commit_short_hash and last_commit_short_hash not in comment.body
        if comment.review_decision == ReviewDecision.TESTED_ACK and is_stale:
            style = 'background-color: #2d672d;'
        elif comment.review_decision == ReviewDecision.UNTESTED_ACK and is_stale:
            style = 'background-color: #b06d0f'
        else:
            style = ''

        # Show comments in detail view only
        if is_details:
            outer_style = ''
            comment_markup = '<div style="color: #000000;"> {body}</div>'.format(body=comment.body)

            # Don't add <hr/> after the last comment
            if comments.index(comment) < len(comments) - 1:
                comment_markup += '<hr/>'

        else:
            outer_style = 'white-space: nowrap; overflow: hidden;'
            comment_markup = ''

        full_text = Markup.escape(comment.body)
        output += '<a target=blank href={comment_url} style="color: #FFFFFF; text-decoration: none;">' \
                  '<div style="{outer_style}">' \
                  '<img src="{avatar_url}" style="height:16px; border-radius: 50%;">' \
                  ' <span title="{full_text}" class="label {label}" style="{style}">{author_login}</span>' \
                  '{comment_markup}' \
                  '</div>' \
                  '</a>'.format(full_text=full_text,
                                label=label,
                                avatar_url=comment.author.avatar_url,
                                author_login=comment.author.login,
                                comment_url=comment.url,
                                comment_markup=comment_markup,
                                style=style,
                                outer_style=outer_style)
        authors.append(comment.author.login)

    if len(authors) >= 4 and not is_details:
        output += '<div class="text-center">' \
                  '<small><em>Total: {reviews_count}</em></small>' \
                  '</div>'.format(reviews_count=len(authors))
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
        label_url = context.parent['modify_query'](flt6_label_in_list=label.name)
        label_color = '#' + label.color
        rgb = webcolors.hex_to_rgb(label_color)
        if rgb.blue > 200:
            rgb = [int(c*0.6) for c in rgb]
            label_color = webcolors.rgb_to_hex(rgb)
        output += '<a href={label_url} style="color: #FFFFFF; text-decoration: none;">' \
                  '<div style="white-space: nowrap; overflow: hidden;">' \
                  ' <span class="label" style="background-color: {label_color};" >{label_name}</span>' \
                  '</div>' \
                  '</a>'.format(label_name=label.name,
                                label_url=label_url,
                                label_color=label_color)
    return Markup(output)
