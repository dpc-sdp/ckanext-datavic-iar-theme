import ckan.plugins as p
import ckan.plugins.toolkit as tk
import ckanext.datavic_iar_theme.helpers as helpers


@tk.blanket.config_declarations
class DatavicIARThemePlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.ITemplateHelpers)

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
