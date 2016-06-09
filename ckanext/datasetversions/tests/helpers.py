import nose.tools

import ckan.tests.helpers as helpers
import ckan.plugins as plugins

assert_equals = nose.tools.assert_equals
assert_raises = nose.tools.assert_raises
assert_regexp_matches = nose.tools.assert_regexp_matches
assert_true = nose.tools.assert_true


class TestBase(helpers.FunctionalTestBase):
    @classmethod
    def setup_class(cls):
        super(TestBase, cls).setup_class()
        plugins.load('datasetversions')

    @classmethod
    def teardown_class(cls):
        plugins.unload('datasetversions')
        super(TestBase, cls).teardown_class()

    def assert_version_names(self, dataset, expected_names):
        assert_equals(self.get_version_names(dataset), expected_names)

    def assert_version_urls(self, dataset, expected_urls):
        assert_equals(self.get_version_urls(dataset), expected_urls)

    def get_version_names(self, dataset):
        return [n[0] for n in dataset['_versions']]

    def get_version_urls(self, dataset):
        return [n[1] for n in dataset['_versions']]
