def list(package):
    return package['_versions']


def is_old(package):
    versions = package.get('_versions', [])

    names = [v[0] for v in versions]

    try:
        return names.index(package['name']) != 0
    except ValueError:
        return False
