import factory
from faker import Faker
from pytest_factoryboy import register

import ckan.tests.factories as factories

faker = Faker()


class DatasetFactory(factories.Dataset):
    access = "yes"
    category = factory.LazyFunction(lambda: factories.Group()["id"])
    date_created_data_asset = factory.Faker("date")
    extract = factory.Faker("sentence")
    license_id = "notspecified"
    personal_information = "yes"
    organization_visibility = "all"
    update_frequency = "unknown"
    workflow_status = "test"
    protective_marking = "official"
    enable_dtv = False


register(DatasetFactory, "dataset")


@register
class ResourceFactory(factories.Resource):
    package_id = factory.LazyAttribute(lambda _: DatasetFactory()["id"])
    format = "CSV"


class GroupFactory(factories.Group):
    pass


register(GroupFactory, "group")


class OrganizationFactory(factories.Organization):
    pass


register(OrganizationFactory, "organization")


class SysadminFactory(factories.Sysadmin):
    pass


register(SysadminFactory, "sysadmin")
