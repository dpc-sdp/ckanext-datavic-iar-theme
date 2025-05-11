from __future__ import annotations

import logging
from typing import Any

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan import types
import ckanext.datavic_iar_theme.helpers as helpers

from ckanext.search_autocomplete.interfaces import ISearchAutocomplete

log = logging.getLogger(__name__)

@tk.blanket.config_declarations
class DatavicIARThemePlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IMiddleware, inherit=True)
    p.implements(ISearchAutocomplete)
    p.implements(p.ISignal)

    def make_middleware(self, app, config):
        app.before_request(lambda: log.info("Session cookie: %s", tk.request.headers.get("cookie")))
        return app

    # IConfigurer
    def update_config(self, config_):
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("webassets", "datavic_iar_theme")

        tk.add_ckan_admin_tab(
            tk.config,
            "check_link.report",
            "Link availability",
            config_var="ckan.admin_tabs",
            icon="chain-broken",
        )

        # Reset group/organization cache on server restart
        helpers.group_list.reset(is_organization=False)
        helpers.group_list.reset(is_organization=True)

    # ITemplateHelpers
    def get_helpers(self):
        return helpers.get_helpers()

    # ISearchAutocomplete
    def get_categories(self):
        return {
            'organization': tk._('Organisations'),
            'res_format': tk._('Formats'),
            'groups': tk._('Categories'),
        }

    # ISignal
    def get_signal_subscriptions(self) -> types.SignalMapping:
        return {
            tk.signals.action_succeeded: [
                {
                    "receiver": clear_group_list_cache,
                    "sender": "group_create",
                },
                {
                    "receiver": clear_group_list_cache,
                    "sender": "group_update",
                },
                {
                    "receiver": clear_group_list_cache,
                    "sender": "group_delete",
                },
                {
                    "receiver": clear_group_list_cache,
                    "sender": "organization_create",
                },
                {
                    "receiver": clear_group_list_cache,
                    "sender": "organization_update",
                },
                {
                    "receiver": clear_group_list_cache,
                    "sender": "organization_delete",
                },
            ]
        }


def clear_group_list_cache(
    action_name: str,
    context: types.Context,
    data_dict: dict[str, Any],
    result: dict[str, Any],
):
    """Invalidates the cached group or organization list after
    create, update, or delete actions."""

    is_organization = (
        action_name.startswith("organization")
        or data_dict.get("type") == "organization"
    )
    helpers.group_list.reset(is_organization=is_organization)
