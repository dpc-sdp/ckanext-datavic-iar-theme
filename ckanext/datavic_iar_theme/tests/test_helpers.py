import pytest
from faker import Faker

from ckan.tests.helpers import call_action

import ckanext.datavic_iar_theme.helpers as h


fake = Faker()


@pytest.fixture
def resource_data():
    def func(**kwargs):
        data_dict = {
            "id": fake.uuid4(),
            "url": fake.url(),
            "name": fake.slug(fake.sentence(nb_words=5)),
            "format": "csv",
        }
        data_dict.update(kwargs)
        return data_dict

    return func


class TestVisibilityList:
    def test_visibility_list_is_a_list(self):
        assert isinstance(h.visibility_list(), list)

    def test_visibility_list_has_three_items(self):
        assert len(h.visibility_list()) == 3

    def test_visibility_list_items_have_value_and_label_keys(self):
        for item in h.visibility_list():
            assert "value" in item
            assert "label" in item

    def test_visibility_list_items_have_string_values(self):
        for item in h.visibility_list():
            assert isinstance(item["value"], str)
            assert isinstance(item["label"], str)

    def test_visibility_list_items_have_valid_values(self):
        valid_values = ["all", "private", "public"]
        for item in h.visibility_list():
            assert item["value"] in valid_values


class TestResourceFormats:
    @pytest.mark.usefixtures("clean_db")
    def test_format_list(self, dataset_factory, resource_data):
        dataset_factory(
            resources=[
                resource_data(),
                resource_data(),
                resource_data(format="xml"),
            ]
        )

        format_list: list[str] = h.format_list()
        assert format_list == ["CSV", "XML"]

    @pytest.mark.usefixtures("clean_db")
    def test_format_list_no_resources(self):
        assert not h.format_list()

    @pytest.mark.usefixtures("clean_db")
    def test_format_list_only_contains_active_resources(self, resource_factory):
        resource_factory()
        resource = resource_factory(format="xls")
        call_action("resource_delete", id=resource["id"])

        res_formats: list[str] = h.format_list()

        assert "CSV" in res_formats
        assert "XLS" not in res_formats

    @pytest.mark.usefixtures("clean_db")
    def test_format_list_is_ordered_alphabetically(self, resource_factory):
        for _format in ("qwe", "asd", "zxc"):
            resource_factory(format=_format)

        res_formats: list[str] = h.format_list()
        sorted_formats: list[str] = sorted(res_formats, key=lambda x: x.lower())
        assert res_formats == sorted_formats


class TestOrganizationAndGroupLists:
    def test_organization_list_no_orgs(self):
        assert not h.organization_list()

    @pytest.mark.usefixtures("clean_db")
    def test_organization_list_with_org(self, organization):
        org_list = h.organization_list()

        assert org_list
        assert isinstance(org_list, list)
        assert isinstance(org_list[0], dict)
        assert len(org_list) == 1

    def test_organization_list_no_groups(self):
        assert not h.search_form_group_list()

    @pytest.mark.usefixtures("clean_db")
    def test_organization_list_no_groups_org(self, organization):
        assert not h.search_form_group_list()

    @pytest.mark.usefixtures("clean_db")
    def test_organization_list_with_group(self, group):
        group_list = h.search_form_group_list()

        assert group_list
        assert isinstance(group_list, list)
        assert isinstance(group_list[0], dict)
        assert len(group_list) == 1
