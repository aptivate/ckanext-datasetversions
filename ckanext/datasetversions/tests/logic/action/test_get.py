import nose.tools

import ckan.tests.helpers as helpers

import ckan.plugins as plugins

assert_equals = nose.tools.assert_equals
assert_true = nose.tools.assert_true
assert_regexp_matches = nose.tools.assert_regexp_matches


class GetTestBase(helpers.FunctionalTestBase):
    @classmethod
    def setup_class(cls):
        super(GetTestBase, cls).setup_class()
        plugins.load('datasetversions')

    @classmethod
    def teardown_class(cls):
        plugins.unload('datasetversions')
        super(GetTestBase, cls).teardown_class()


class TestPackageShow(GetTestBase):
    def setup(self):
        super(TestPackageShow, self).setup()

        self.parent = helpers.call_action('package_create',
                                          name='ma001-1')

        self.v2 = helpers.call_action('package_create',
                                      name='ma001-1-2',
                                      extras=[{'key': 'versionNumber',
                                               'value': '2'}])

        self.v1 = helpers.call_action('package_create',
                                      name='ma001-1-1',
                                      extras=[{'key': 'versionNumber',
                                               'value': '1'}])

        self.v10 = helpers.call_action('package_create',
                                      name='ma001-1-10',
                                      extras=[{'key': 'versionNumber',
                                               'value': '10'}])

        helpers.call_action('package_relationship_create',
                            subject=self.v10['id'],
                            type='child_of',
                            object=self.parent['id'])

        helpers.call_action('package_relationship_create',
                            subject=self.v1['id'],
                            type='child_of',
                            object=self.parent['id'])

        helpers.call_action('package_relationship_create',
                            subject=self.v2['id'],
                            type='child_of',
                            object=self.parent['id'])

    def test_latest_version_displayed_when_showing_parent(self):
        dataset = helpers.call_action('package_show',
                                      id=self.parent['id'])

        assert_equals(dataset['name'], self.v10['name'])

    def test_child_version_displayed_when_showing_child(self):
        dataset = helpers.call_action('package_show',
                                      id=self.v2['id'])

        assert_equals(dataset['name'], self.v2['name'])

    def test_other_versions_displayed_when_showing_parent(self):
        dataset = helpers.call_action('package_show',
                                      id=self.parent['id'])

        assert_equals(dataset['versions'], [self.v10['name'],
                                            self.v2['name'],
                                            self.v1['name']])

    def test_other_versions_displayed_when_showing_child(self):
        dataset = helpers.call_action('package_show',
                                      id=self.v2['id'])

        assert_equals(dataset['versions'], [self.v10['name'],
                                            self.v2['name'],
                                            self.v1['name']])

    def test_tracking_summary_returned_for_parent(self):
        dataset = helpers.call_action('package_show',
                                      id=self.parent['id'],
                                      include_tracking=True)

        assert_true('tracking_summary' in dataset)
