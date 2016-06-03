from ckan.plugins import toolkit

import ckan.logic as logic
from ckan.logic.action.get import package_show as ckan_package_show


@toolkit.side_effect_free
def package_show(context, data_dict):
    this_dataset = ckan_package_show(context, data_dict)
    version_to_display = this_dataset

    parent_names = _get_parent_dataset_names(context, this_dataset['id'])

    if len(parent_names) > 0:
        base_id = parent_names[0]
        display_latest_version = False
    else:
        base_id = this_dataset['id']
        display_latest_version = True

    all_version_names = _get_child_dataset_names(context, base_id)
    all_active_versions = _get_ordered_active_dataset_versions(
        context,
        data_dict,
        all_version_names)

    # Show the most recent, public active one
    if display_latest_version and len(all_active_versions) > 0:
        version_to_display = all_active_versions[0]

    version_to_display['_versions'] = [v['name'] for v in all_active_versions]

    return version_to_display


def _get_child_dataset_names(context, parent_id):
    children = []

    try:
        children = toolkit.get_action('package_relationships_list')(
            context,
            data_dict={'id': parent_id,
                       'rel': 'parent_of'})
    except logic.NotFound:
        pass

    return _get_names_from_relationships(children)


def _get_parent_dataset_names(context, child_id):
    parents = []

    try:
        parents = toolkit.get_action('package_relationships_list')(
            context,
            data_dict={'id': child_id,
                       'rel': 'child_of'})
    except logic.NotFound:
        pass

    return _get_names_from_relationships(parents)


def _get_names_from_relationships(relationships):
    return [r['object'] for r in relationships]


def _get_ordered_active_dataset_versions(context, data_dict, child_names):
    versions = []

    for name in child_names:
        data_dict['id'] = name
        version = ckan_package_show(context, data_dict)
        if version['state'] == 'active' and not version['private']:
            versions.append(version)

    versions.sort(key=_get_version, reverse=True)

    return versions


def _get_version(dataset):
    try:
        version_number = int(dataset['version'])
    except ValueError:
        version_number = 0

    return version_number
