import ckan.tests.helpers as helpers
import ckan.tests.factories as factories

from ckanext.datasetversions.tests.helpers import (
    assert_equals,
    TestBase,
)


class TestCreate(TestBase):
    def setup(self):
        super(TestBase, self).setup()

        self.user = factories.User()
        self.organization = factories.Organization(user=self.user)

        self.v2 = helpers.call_action('package_create',
                                      name='189-ma001-2',
                                      version=2)

        self.v1 = helpers.call_action('package_create',
                                      name='189-ma001-1',
                                      version=1)

        self.v10 = helpers.call_action('package_create',
                                       name='189-ma001-10',
                                       version=10)

    def test_new_versions_associated_with_existing(self):
        helpers.call_action('dataset_version_create',
                            id=self.v1['id'],
                            base_name='189-ma001')

        helpers.call_action('dataset_version_create',
                            id=self.v2['id'],
                            base_name='189-ma001')

        helpers.call_action('dataset_version_create',
                            id=self.v10['id'],
                            base_name='189-ma001')

        [rel_1] = helpers.call_action(
            'package_relationships_list',
            id=self.v1['id'],
            rel='child_of')

        [rel_2] = helpers.call_action(
            'package_relationships_list',
            id=self.v2['id'],
            rel='child_of')

        [rel_10] = helpers.call_action(
            'package_relationships_list',
            id=self.v10['id'],
            rel='child_of')

        assert_equals(rel_1['subject'], '189-ma001-1')
        assert_equals(rel_1['type'], 'child_of')
        assert_equals(rel_1['object'], '189-ma001')

        assert_equals(rel_2['subject'], '189-ma001-2')
        assert_equals(rel_2['type'], 'child_of')
        assert_equals(rel_2['object'], '189-ma001')

        assert_equals(rel_10['subject'], '189-ma001-10')
        assert_equals(rel_10['type'], 'child_of')
        assert_equals(rel_10['object'], '189-ma001')

    def test_organization_set(self):
        helpers.call_action('dataset_version_create',
                            context={'user': self.user['name']},
                            id=self.v1['id'],
                            base_name='189-ma001',
                            owner_org=self.organization['id'])

        parent_dataset = helpers.call_action(
            'ckan_package_show',
            context={'user': self.user['name']},
            id='189-ma001')

        assert_equals(parent_dataset['owner_org'],
                      self.organization['id'])

    def test_parent_dataset_is_private_with_owner_org(self):
        helpers.call_action('dataset_version_create',
                            context={'user': self.user['name']},
                            id=self.v1['id'],
                            base_name='189-ma001',
                            owner_org=self.organization['id'])

        parent_dataset = helpers.call_action(
            'ckan_package_show',
            context={'user': self.user['name']},
            id='189-ma001')

        assert_equals(parent_dataset['private'], True)

    def test_parent_dataset_is_public_for_no_owner_org(self):
        helpers.call_action('dataset_version_create',
                            context={'user': self.user['name']},
                            id=self.v1['id'],
                            base_name='189-ma001')

        parent_dataset = helpers.call_action(
            'ckan_package_show',
            context={'user': self.user['name']},
            id='189-ma001')

        assert_equals(parent_dataset['private'], False)
