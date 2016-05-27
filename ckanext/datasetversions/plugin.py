import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckanext.datasetversions.logic.action.create
import ckanext.datasetversions.logic.action.get


class DatasetversionsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IConfigurer)

    # IActions
    def get_actions(self):
        return {
            'base_package_show':
            ckanext.datasetversions.logic.action.get.base_package_show,
            'package_show':
            ckanext.datasetversions.logic.action.get.package_show,
            'dataset_version_create':
            ckanext.datasetversions.logic.action.create.dataset_version_create,
        }

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'datasetversions')
