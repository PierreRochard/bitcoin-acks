from flask_admin.contrib.sqla import ModelView

from bitcoin_acks.webapp.mixins import NullOrderMixinView


class BountiesModelView(ModelView, NullOrderMixinView):
    def __init__(self, model, session, *args, **kwargs):
        super(BountiesModelView, self).__init__(model, session, *args,
                                                    **kwargs)
        self.static_folder = 'static'
        self.endpoint = 'bounties'
        self.name = 'Bounties'

    can_delete = False
    can_create = True
    can_edit = False
    can_view_details = True

    named_filter_urls = True

    details_modal = True
