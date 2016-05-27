import ckan.tests.helpers as helpers

from ckanext.datasetversions.tests.helpers import (
    assert_equals,
    assert_true,
    TestBase,
)


class TestPackageShow(TestBase):
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
