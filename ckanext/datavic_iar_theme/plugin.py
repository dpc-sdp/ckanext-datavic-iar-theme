import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.datavic_iar_theme.helpers as helpers


class DatavicIARThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('webassets', 'datavic_iar_theme')

        toolkit.add_ckan_admin_tab(
            toolkit.config,
            'check_link.report',
            'Link availability',
            config_var='ckan.admin_tabs',
            icon="chain-broken",
        )

    # ITemplateHelpers

    def get_helpers(self):
        ''' Return a dict of named helper functions (as defined in the ITemplateHelpers interface).
        These helpers will be available under the 'h' thread-local global object.
        '''
        return {
            'organization_list': helpers.organization_list,
            'get_parent_orgs': helpers.get_parent_orgs,
            'search_form_group_list': helpers.search_form_group_list,
            'format_list': helpers.format_list,
            'get_parent_site_url': helpers.get_parent_site_url,
            'get_gtm_code': helpers.get_gtm_code,
            'datavic_linked_user': helpers.datavic_linked_user,
            'hotjar_tracking_enabled': helpers.hotjar_tracking_enabled,
            'get_hotjar_hsid': helpers.get_hotjar_hsid,
            'get_hotjar_hjsv': helpers.get_hotjar_hjsv,
            'visibility_list': helpers.visibility_list,
            'featured_resource_preview':helpers.featured_resource_preview
        }
