import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckanext.datasetversions.logic.action.get


class DatasetversionsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IConfigurer)

    # IActions
    def get_actions(self):
        return {
            'package_show':
            ckanext.datasetversions.logic.action.get.package_show
        }

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'datasetversions')
