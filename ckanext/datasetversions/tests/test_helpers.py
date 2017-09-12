import unittest

from ckanext.datasetversions.plugin import DatasetversionsPlugin


class TestHelpers(unittest.TestCase):
    def setUp(self):
        super(TestHelpers, self).setUp()
        self.plugin = DatasetversionsPlugin()

    def _get_helper(self, name):
        return self.plugin.get_helpers()[name]

    def test_list_versions(self):
        package = {'_versions': [('v3', 'parent'), ('v2', 'v2'), ('v1', 'v1')]}

        versions = self._get_helper('datasetversions_list')(package)

        self.assertEquals(versions, [('v3', 'parent'), ('v2', 'v2'), ('v1', 'v1')])

    def test_is_old_version_false_for_latest(self):
        package = {'name': 'v3', '_versions':
                   [('v3', 'parent'), ('v2', 'v2'), ('v1', 'v1')]}

        self.assertFalse(self._get_helper('datasetversions_is_old')(package))

    def test_is_old_version_true_for_old(self):
        package = {'name': 'v2', '_versions':
                   [('v3', 'parent'), ('v2', 'v2'), ('v1', 'v1')]}

        self.assertTrue(self._get_helper('datasetversions_is_old')(package))

    def test_is_old_version_false_for_non_existent(self):
        package = {'name': 'v3', '_versions': []}

        self.assertFalse(self._get_helper('datasetversions_is_old')(package))

    def test_is_old_version_false_for_no_versions(self):
        package = {'name': 'v3'}

        self.assertFalse(self._get_helper('datasetversions_is_old')(package))

    def test_get_context_threads_desired_values(self):
        default_keys = ['model', 'session', 'user', 'ignore_auth', 'use_cache']
        minimal_context = {'model': 'foo', 'session': 'bar'}
        get_context = self._get_helper('datasetversions_get_context')

        result = get_context(minimal_context)
        self.assertEqual(sorted(result.keys()), sorted(default_keys))

        should_val = dict(minimal_context.items(), **{'validate': True})
        result = get_context(should_val)
        self.assertTrue(result['validate'])

        shouldnt_val = dict(minimal_context.items(), **{'validate': False})
        result = get_context(shouldnt_val)
        self.assertFalse(result['validate'])

        result = get_context(shouldnt_val)
        self.assertIsNone(result['user'])
