import ckan.logic as logic
from ckan.logic.action.get import package_show as ckan_package_show
from ckan.plugins import toolkit


def dataset_version_create(context, data_dict):
    id = data_dict.get('id')
    parent_name = data_dict.get('base_name')

    parent = _get_or_create_parent_dataset(
        context,
        {'name': parent_name,
         'owner_org': data_dict.get('owner_org')})

    toolkit.get_action('package_relationship_create')(
        _get_context(context), {
            'subject': id,
            'object': parent['id'],
            'type': 'child_of',
        }
    )


def _get_or_create_parent_dataset(context, data_dict):
    try:
        dataset = ckan_package_show(
            _get_context(context), {'id': data_dict['name']})
    except (logic.NotFound):
        dataset = toolkit.get_action('package_create')(
            _get_context(context), data_dict)

    return dataset


def _get_context(context):
    return {
        'model': context['model'],
        'session': context['session'],
        'user': context['user'],
        'ignore_auth': context.get('ignore_auth', False)
    }
