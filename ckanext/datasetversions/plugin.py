import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckanext.datasetversions.logic.action.create
import ckanext.datasetversions.logic.action.get
import ckanext.datasetversions.helpers as helpers


class DatasetversionsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController)
    plugins.implements(plugins.ITemplateHelpers)

    # IActions
    def get_actions(self):
        return {
            'ckan_package_show':
            ckanext.datasetversions.logic.action.get.ckan_package_show,
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

    # IPackageController
    def read(self, entity):
        pass

    def create(self, entity):
        pass

    def edit(self, entity):
        pass

    def authz_add_role(self, object_role):
        pass

    def authz_remove_role(self, object_role):
        pass

    def delete(self, entity):
        pass

    def after_create(self, context, pkg_dict):
        '''
            Extensions will receive the validated data dict after the package
            has been created (Note that the create method will return a package
            domain object, which may not include all fields). Also the newly
            created package id will be added to the dict.
        '''
        pass

    def after_update(self, context, pkg_dict):
        '''
            Extensions will receive the validated data dict after the package
            has been updated (Note that the edit method will return a package
            domain object, which may not include all fields).
        '''
        pass

    def after_delete(self, context, pkg_dict):
        '''
            Extensions will receive the data dict (tipically containing
            just the package id) after the package has been deleted.
        '''
        pass

    def after_show(self, context, pkg_dict):
        '''
            Extensions will receive the validated data dict after the package
            is ready for display (Note that the read method will return a
            package domain object, which may not include all fields).
        '''
        pass

    def before_search(self, search_params):
        '''
            Extensions will receive a dictionary with the query parameters,
            and should return a modified (or not) version of it.

            search_params will include an `extras` dictionary with all values
            from fields starting with `ext_`, so extensions can receive user
            input from specific fields.

        '''
        return search_params

    def after_search(self, search_results, search_params):
        '''
            Extensions will receive the search results, as well as the search
            parameters, and should return a modified (or not) object with the
            same structure:

                {'count': '', 'results': '', 'facets': ''}

            Note that count and facets may need to be adjusted if the extension
            changed the results for some reason.

            search_params will include an `extras` dictionary with all values
            from fields starting with `ext_`, so extensions can receive user
            input from specific fields.

        '''

        return search_results

    def before_index(self, package_dict):
        # We recalculate this on the fly so don't index it
        package_dict.pop('_versions', False)

        return package_dict

    def before_view(self, pkg_dict):
        '''
             Extensions will recieve this before the dataset gets
             displayed. The dictionary passed will be the one that gets
             sent to the template.
        '''
        return pkg_dict

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'datasetversions_list': helpers.list,
            'datasetversions_is_old': helpers.is_old,
        }
