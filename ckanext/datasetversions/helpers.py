def list(package):
    extras_dict = {e['key']: e['value'] for e in package['extras']}

    return extras_dict['_versions']
