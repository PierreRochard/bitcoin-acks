from flask_admin.contrib.sqla import ModelView


class PullRequestsModelView(ModelView):
    def __init__(self, model, session, *args, **kwargs):
        super(PullRequestsModelView, self).__init__(model, session, *args,
                                                    **kwargs)
        self.static_folder = 'static'
        self.endpoint = 'admin'
        self.name = 'Pull Requests'

    can_delete = False
    can_create = False
    can_edit = False
    can_view_details = True
    # column_searchable_list = [
    #     'screen_name',
    #     'name',
    #     'description',
    #     'location'
    # ]
    # column_list = [
    #     'is_interesting',
    #     'tags',
    #     'profile_image_url',
    #     'screen_name',
    #     'following',
    #     'friends_followers_ratio',
    #     'name',
    #     'description',
    #     'location',
    #     'created_at',
    #     'followers_count',
    #     'friends_count',
    #     'statuses_count',
    #     'favourites_count',
    #     'lang',
    # ]
    # column_filters = [c for c in column_list if not c.endswith('_ratio')]
    # column_editable_list = [
    #     'is_interesting',
    #     'tags'
    # ]
    #
    # column_formatters = dict(
    #     screen_name=screen_name_formatter,
    #     profile_image_url=image_formatter
    # )
    # column_default_sort = ('followers_count', True)
