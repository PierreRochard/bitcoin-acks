import datetime

import humanize

from markupsafe import Markup

from bitcoin_acks.constants import ReviewDecision


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
        humanized_date = humanize.naturaltime(now - old_date)
        return Markup('<div title="{0}" style="white-space: nowrap; overflow: hidden;">{1}</div>'.format(old_date, humanized_date))
    else:
        return ''


def pr_link_formatter(view, context, model, name):
    value = getattr(model, name)
    return Markup('<a target=blank href="{0}">{1}</a>'.format(model.html_url, value))


def author_link_formatter(view, context, model, name):
    if model.author is None:
        return ''
    return Markup('<div style="white-space: nowrap; overflow: hidden;"><img src="{0}" style="height:16px; border-radius: 50%;"> <a target=blank href="{1}" >{2}</a></div>'.format(model.author.avatar_url, model.author.url, model.author.login))


def ack_formatter(comments, last_commit_short_hash, context_name):
    output = ''
    authors = []
    is_details = 'details' in context_name

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

    if len(authors) >= 3 and not is_details:
        output += '<div class="text-center">' \
                  '<small><em>Total: {reviews_count}</em></small>' \
                  '</div>'.format(reviews_count=len(authors))
    return Markup(output)


def concept_ack_formatter(view, context, model, name):
    return ack_formatter(comments=getattr(model, 'concept_acks'),
                         last_commit_short_hash=model.last_commit_short_hash,
                         context_name=context.name)


def tested_ack_formatter(view, context, model, name):
    return ack_formatter(comments=getattr(model, 'tested_acks'),
                         last_commit_short_hash=model.last_commit_short_hash,
                         context_name=context.name)


def untested_ack_formatter(view, context, model, name):
    return ack_formatter(comments=getattr(model, 'untested_acks'),
                         last_commit_short_hash=model.last_commit_short_hash,
                         context_name=context.name)


def nack_formatter(view, context, model, name):
    return ack_formatter(comments=getattr(model, 'nacks'),
                         last_commit_short_hash=model.last_commit_short_hash,
                         context_name=context.name)


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
