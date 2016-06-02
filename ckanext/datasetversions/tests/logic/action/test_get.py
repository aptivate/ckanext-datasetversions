import ckan.tests.helpers as helpers
import ckan.tests.factories as factories

from ckanext.datasetversions.tests.helpers import (
    assert_equals,
    assert_true,
    TestBase,
)


class TestPackageShow(TestBase):
    def setup(self):
        super(TestPackageShow, self).setup()

        self.v2 = helpers.call_action('package_create',
                                      name='189-ma001-2',
                                      extras=[{'key': 'versionNumber',
                                               'value': '2'}])

        self.v1 = helpers.call_action('package_create',
                                      name='189-ma001-1',
                                      extras=[{'key': 'versionNumber',
                                               'value': '1'}])

        self.v10 = helpers.call_action('package_create',
                                       name='189-ma001-10',
                                       extras=[{'key': 'versionNumber',
                                                'value': '10'}])

        helpers.call_action('dataset_version_create',
                            id=self.v10['id'],
                            base_name='189-ma001')

        helpers.call_action('dataset_version_create',
                            id=self.v1['id'],
                            base_name='189-ma001')

        helpers.call_action('dataset_version_create',
                            id=self.v2['id'],
                            base_name='189-ma001')

        self.parent = helpers.call_action('ckan_package_show',
                                          id='189-ma001')

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

        extras_dict = {e['key']: e['value'] for e in dataset['extras']}

        assert_equals(extras_dict['versions'], [self.v10['name'],
                                                self.v2['name'],
                                                self.v1['name']])

    def test_other_versions_displayed_when_showing_child(self):
        dataset = helpers.call_action('package_show',
                                      id=self.v2['id'])

        extras_dict = {e['key']: e['value'] for e in dataset['extras']}

        assert_equals(extras_dict['versions'], [self.v10['name'],
                                                self.v2['name'],
                                                self.v1['name']])

    def test_tracking_summary_returned_for_parent(self):
        dataset = helpers.call_action('package_show',
                                      id=self.parent['id'],
                                      include_tracking=True)

        assert_true('tracking_summary' in dataset)

    def test_versions_dont_accumulate(self):
        [rel_10] = helpers.call_action(
            'package_relationships_list',
            id=self.v10['id'],
            rel='child_of')

        assert_equals(rel_10['subject'], '189-ma001-10')
        assert_equals(rel_10['type'], 'child_of')
        assert_equals(rel_10['object'], '189-ma001')

        dataset_dict = helpers.call_action('package_show',
                                           id='189-ma001')

        # TODO: Looks like a bug?
        del dataset_dict['relationships_as_subject']
        del dataset_dict['relationships_as_object']

        updated_dict = helpers.call_action('package_update',
                                           **dataset_dict)

        # Tests the above bug
        [rel_10] = helpers.call_action(
            'package_relationships_list',
            id=self.v10['id'],
            rel='child_of')

        assert_equals(rel_10['subject'], '189-ma001-10')
        assert_equals(rel_10['type'], 'child_of')
        assert_equals(rel_10['object'], '189-ma001')

        extras_dict = {e['key']: e['value'] for e in updated_dict['extras']}

        assert_true('versions' in extras_dict)

        # Versions would appear twice here if they accumulated, or they would
        # if the validators didn't complain
        assert_equals(extras_dict['versions'], [
            self.v10['name'],
            self.v2['name'],
            self.v1['name'],
        ])

    def test_versions_do_not_include_deleted_items(self):
        helpers.call_action('package_delete',
                            id=self.v2['name'])

        dataset = helpers.call_action('package_show',
                                      id=self.parent['id'])

        extras_dict = {e['key']: e['value'] for e in dataset['extras']}

        assert_true(self.v2['name'] not in extras_dict['versions'])

    def test_versions_do_not_include_private_items(self):
        user = factories.User()
        organization = factories.Organization(user=user)

        v12 = helpers.call_action('package_create',
                                  context={'user': user['id']},
                                  name='189-ma001-12',
                                  private=True,
                                  owner_org=organization['id'],
                                  extras=[{'key': 'versionNumber',
                                           'value': '12'}])
        helpers.call_action('dataset_version_create',
                            id=v12['id'],
                            base_name='189-ma001')

        dataset = helpers.call_action('package_show',
                                      id=self.parent['id'])

        extras_dict = {e['key']: e['value'] for e in dataset['extras']}

        assert_true(v12['name'] not in extras_dict['versions'])

    def test_versions_empty_if_all_deleted(self):
        helpers.call_action('package_delete',
                            id=self.v1['name'])
        helpers.call_action('package_delete',
                            id=self.v2['name'])
        helpers.call_action('package_delete',
                            id=self.v10['name'])

        dataset = helpers.call_action('package_show',
                                      id=self.parent['id'])

        extras_dict = {e['key']: e['value'] for e in dataset['extras']}

        assert_equals(extras_dict['versions'], [])


class TestVersionNumber(TestBase):
    def test_non_numeric_version_number_treated_as_zero(self):
        v1 = helpers.call_action('package_create',
                                 name='189-ma001-1',
                                 extras=[{'key': 'versionNumber',
                                          'value': '1'}])

        v2 = helpers.call_action('package_create',
                                 name='189-ma001-2',
                                 extras=[{'key': 'versionNumber',
                                          'value': 'v2'}])

        helpers.call_action('dataset_version_create',
                            id=v2['id'],
                            base_name='189-ma001')

        helpers.call_action('dataset_version_create',
                            id=v1['id'],
                            base_name='189-ma001')

        dataset = helpers.call_action('package_show',
                                      id='189-ma001')

        extras_dict = {e['key']: e['value'] for e in dataset['extras']}

        assert_equals(extras_dict['versions'], [v1['name'], v2['name']])
