from ckan.plugins import toolkit

import ckan.logic as logic
from ckan.logic.action.get import package_show as base_package_show


def package_show(context, data_dict):
    this_dataset = base_package_show(context, data_dict)
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

    _set_versions_in_extras(version_to_display,
                            all_active_versions)

    return version_to_display


def _set_versions_in_extras(dataset, versions):
    extras = dataset['extras']
    new_extras = []

    for e in extras:
        if e['key'] != 'versions':
            new_extras.append(e)

    new_extras.append(
        {'key': 'versions', 'value': [v['name'] for v in versions]})

    dataset['extras'] = new_extras


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
        version = base_package_show(context, data_dict)
        if version['state'] == 'active' and not version['private']:
            versions.append(version)

    versions.sort(key=_get_version, reverse=True)

    return versions


def _get_version(version):
    extras_dict = {e['key']: e['value'] for e in version['extras']}
    try:
        version_number = int(extras_dict['versionNumber'])
    except ValueError:
        version_number = 0

    return version_number
