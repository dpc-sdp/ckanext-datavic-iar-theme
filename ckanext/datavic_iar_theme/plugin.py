import logging
import ckan.plugins as p
import ckan.plugins.toolkit as tk
import ckanext.datavic_iar_theme.helpers as helpers

from ckanext.search_autocomplete.interfaces import ISearchAutocomplete

log = logging.getLogger(__name__)

@tk.blanket.config_declarations
class DatavicIARThemePlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IMiddleware, inherit=True)
    p.implements(ISearchAutocomplete)

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
