import ckan.logic as logic
import ckan.tests.helpers as helpers
import ckan.tests.factories as factories

from ckanext.datasetversions.tests.helpers import (
    assert_equals,
    assert_raises,
    assert_true,
    TestBase,
)


class TestPackageShowBase(TestBase):
    def setup(self):
        super(TestPackageShowBase, self).setup()

        self.user = factories.User()
        self.organization = factories.Organization(
            user=self.user)
        self.logged_out_context = {'ignore_auth': False,
                                   'auth_user_obj': None}


class TestPackageShowThreeVersions(TestPackageShowBase):
    def setup(self):
        super(TestPackageShowThreeVersions, self).setup()

        self.v2 = helpers.call_action('package_create',
                                      context={'user': self.user['id']},
                                      name='189-ma001-2',
                                      version='2',
                                      owner_org=self.organization['id'])

        self.v1 = helpers.call_action('package_create',
                                      context={'user': self.user['id']},
                                      name='189-ma001-1',
                                      version='1',
                                      owner_org=self.organization['id'])

        self.v10 = helpers.call_action('package_create',
                                       context={'user': self.user['id']},
                                       name='189-ma001-10',
                                       version='10',
                                       owner_org=self.organization['id'])

        helpers.call_action('dataset_version_create',
                            context={'user': self.user['id']},
                            id=self.v10['id'],
                            base_name='189-ma001',
                            owner_org=self.organization['id'])

        helpers.call_action('dataset_version_create',
                            context={'user': self.user['id']},
                            id=self.v1['id'],
                            base_name='189-ma001',
                            owner_org=self.organization['id'])

        helpers.call_action('dataset_version_create',
                            context={'user': self.user['id']},
                            id=self.v2['id'],
                            base_name='189-ma001',
                            owner_org=self.organization['id'])

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

    def test_all_versions_displayed_when_showing_parent(self):
        dataset = helpers.call_action('package_show',
                                      id=self.parent['id'])

        self.assert_version_names(dataset, [
            self.v10['name'],
            self.v2['name'],
            self.v1['name']])

    def test_all_versions_displayed_when_showing_child(self):
        dataset = helpers.call_action('package_show',
                                      id=self.v2['id'])

        self.assert_version_names(dataset, [
            self.v10['name'],
            self.v2['name'],
            self.v1['name'],
        ])

    def test_tracking_summary_returned_for_parent(self):
        dataset = helpers.call_action('package_show',
                                      id=self.parent['id'],
                                      include_tracking=True)

        assert_true('tracking_summary' in dataset)

    def test_relationships_not_included_for_parent(self):
        dataset = helpers.call_action('package_show',
                                      id=self.parent['id'])

        assert_true('relationships_as_subject' not in dataset)
        assert_true('relationships_as_object' not in dataset)

    def test_relationships_not_included_for_child(self):
        dataset = helpers.call_action('package_show',
                                      id=self.v1['id'])

        assert_true('relationships_as_subject' not in dataset)
        assert_true('relationships_as_object' not in dataset)

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

        updated_dict = helpers.call_action('package_update',
                                           context={'user': self.user['id']},
                                           **dataset_dict)

        [rel_10] = helpers.call_action(
            'package_relationships_list',
            id=self.v10['id'],
            rel='child_of')

        assert_equals(rel_10['subject'], '189-ma001-10')
        assert_equals(rel_10['type'], 'child_of')
        assert_equals(rel_10['object'], '189-ma001')

        assert_true('_versions' in updated_dict)

        # Versions would appear twice here if they accumulated, or they would
        # if the validators didn't complain
        self.assert_version_names(updated_dict, [
            self.v10['name'],
            self.v2['name'],
            self.v1['name'],
        ])

    def test_versions_do_not_include_deleted_items(self):
        helpers.call_action('package_delete',
                            id=self.v2['name'])

        dataset = helpers.call_action('package_show',
                                      id=self.parent['id'])

        assert_true(self.v2['name'] not in
                    self.get_version_names(dataset))

    def test_versions_do_not_include_private_items(self):
        v12 = helpers.call_action('package_create',
                                  context={'user': self.user['id']},
                                  name='189-ma001-12',
                                  private=True,
                                  owner_org=self.organization['id'],
                                  version=12)
        helpers.call_action('dataset_version_create',
                            id=v12['id'],
                            base_name='189-ma001')

        dataset = helpers.call_action('package_show',
                                      id=self.parent['id'])

        assert_true(v12['name'] not in self.get_version_names(dataset))

    def test_versions_empty_if_all_deleted(self):
        helpers.call_action('package_delete',
                            id=self.v1['name'])
        helpers.call_action('package_delete',
                            id=self.v2['name'])
        helpers.call_action('package_delete',
                            id=self.v10['name'])

        dataset = helpers.call_action('package_show',
                                      id=self.parent['id'])

        assert_equals(dataset['_versions'], [])

    def test_latest_url_is_parent(self):
        dataset = helpers.call_action('package_show',
                                      id=self.parent['id'])

        self.assert_version_urls(dataset, [
            self.parent['name'],
            self.v2['name'],
            self.v1['name']])

    def test_can_see_latest_version_when_logged_out(self):
        dataset = helpers.call_action('package_show',
                                      self.logged_out_context,
                                      id=self.parent['id'])

        assert_equals(dataset['name'], self.v10['name'])


class TestLoggedOutPackageShow(TestPackageShowBase):
    def setup(self):
        super(TestLoggedOutPackageShow, self).setup()

    def test_private_versioned_dataset_not_available_as_latest(self):
        v12 = helpers.call_action('package_create',
                                  context={'user': self.user['id']},
                                  name='189-ma001-12',
                                  private=True,
                                  owner_org=self.organization['id'],
                                  version=12)
        helpers.call_action('dataset_version_create',
                            id=v12['id'],
                            base_name='189-ma001')

        dataset = helpers.call_action('package_show',
                                      context=self.logged_out_context,
                                      id='189-ma001')
        assert_true(v12['name'] not in self.get_version_names(dataset))

    def test_not_authorized_for_private_unversioned_dataset(self):
        dataset = helpers.call_action('package_create',
                                      context={'user': self.user['id']},
                                      name='dataset-without-versions',
                                      private=True,
                                      owner_org=self.organization['id'])

        assert_raises(logic.NotAuthorized,
                      helpers.call_action,
                      'package_show',
                      self.logged_out_context,
                      id=dataset['id'])

    def test_not_authorized_for_private_versioned_dataset(self):
        v12 = helpers.call_action('package_create',
                                  context={'user': self.user['id']},
                                  name='189-ma001-12',
                                  private=True,
                                  owner_org=self.organization['id'],
                                  version=12)
        helpers.call_action('dataset_version_create',
                            id=v12['id'],
                            base_name='189-ma001')

        assert_raises(logic.NotAuthorized,
                      helpers.call_action,
                      'package_show',
                      self.logged_out_context,
                      id='189-ma001-12')

    def test_authorized_for_public_versioned_dataset_when_other_private(self):
        v1 = helpers.call_action('package_create',
                                 context={'user': self.user['id']},
                                 name='189-ma001-1',
                                 private=False,
                                 owner_org=self.organization['id'],
                                 version=1)

        v2 = helpers.call_action('package_create',
                                 context={'user': self.user['id']},
                                 name='189-ma001-2',
                                 private=True,
                                 owner_org=self.organization['id'],
                                 version=2)

        helpers.call_action('dataset_version_create',
                            id=v1['id'],
                            base_name='189-ma001')

        helpers.call_action('dataset_version_create',
                            id=v2['id'],
                            base_name='189-ma001')

        dataset = helpers.call_action('package_show',
                                      context=self.logged_out_context,
                                      id='189-ma001-1')

        assert_true(v1['name'] in self.get_version_names(dataset))


class TestPackageSearch(TestBase):
    def setup(self):
        super(TestPackageSearch, self).setup()

        self.user = factories.User()
        self.organization = factories.Organization(user=self.user)

        self.v1 = helpers.call_action('package_create',
                                      name='189-ma001-1',
                                      version='1')

        helpers.call_action('dataset_version_create',
                            id=self.v1['id'],
                            base_name='189-ma001',
                            context={'user': self.user['name']},
                            owner_org=self.organization['id'])

        self.parent = helpers.call_action('ckan_package_show',
                                          id='189-ma001')

    def test_search_results_do_not_include_parent_version_if_private(self):
        results = helpers.call_action('package_search',
                                      q='*:*',
                                      start='0',
                                      rows='20',
                                      sort='metadata_modified desc')

        names = [r['name'] for r in results['results']]

        assert_true('189-ma001' not in names)


class TestVersionNumber(TestBase):
    def test_non_numeric_version_number_treated_as_zero(self):
        v1 = helpers.call_action('package_create',
                                 name='189-ma001-1',
                                 version='1')

        v2 = helpers.call_action('package_create',
                                 name='189-ma001-2',
                                 version='v2')

        helpers.call_action('dataset_version_create',
                            id=v2['id'],
                            base_name='189-ma001')

        helpers.call_action('dataset_version_create',
                            id=v1['id'],
                            base_name='189-ma001')

        dataset = helpers.call_action('package_show',
                                      id='189-ma001')

        self.assert_version_names(dataset, [v1['name'], v2['name']])
