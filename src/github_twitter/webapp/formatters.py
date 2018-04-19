from markupsafe import Markup


def screen_name_formatter(view, context, model, name):
    return Markup(
        f'<a href="https://twitter.com/{model.screen_name}">{model.screen_name}</a>')


def image_formatter(view, context, model, name):
    url = getattr(model, name)
    return Markup(f'<img src="{url}">')
