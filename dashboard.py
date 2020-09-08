from django.utils.translation import ugettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard, AppIndexDashboard


class CustomIndexDashboard(Dashboard):
    columns = 3

    def init_with_context(self, context):
        self.available_children.append(modules.LinkList)
        self.children.append(modules.LinkList(
            _('Support'),
            children=[
                {
                    'title': _('Chargoon'),
                    'url': 'http://www.chargoon.com/',
                    'external': True,
                },
                {
                    'title': _('test'),
                    'url': '',
                    'external': True,
                },
                {
                    'title': _('nip'),
                    'url': 'http://127.0.0.1:8000/admin/nip/shiftassignmentpivoted_by_id/',
                    'external': False,
                },
            ],
            column=0,
            order=0
        ))