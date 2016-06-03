def list(package):
    return package['_versions']


def is_old(package):
    versions = package.get('_versions', [])

    try:
        return versions.index(package['name']) != 0
    except ValueError:
        return False
