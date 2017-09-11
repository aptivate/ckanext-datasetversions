def list(package):
    return package['_versions']


def is_old(package):
    versions = package.get('_versions', [])

    names = [v[0] for v in versions]

    try:
        return names.index(package['name']) != 0
    except ValueError:
        return False


def _get_context(context):
    """An internal context generator. Accepts a CKAN context.

    CKAN's internals put various things into the context which
    makes reusing it for multiple API calls inadvisable. This
    function adds more fine grain control on the context from
    our plugin logic side.
    """
    new_context = {
        'model': context['model'],
        'session': context['session'],
        'user': context.get('user'),
        'ignore_auth': context.get('ignore_auth', False),
        'use_cache': context.get('use_cache', False),
    }

    if 'validate' in context:
        new_context['validate'] = context['validate']

    return new_context
