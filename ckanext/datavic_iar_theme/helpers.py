from __future__ import annotations

import json
import logging
from typing import Optional, Any

from sqlalchemy.sql import func

import ckan.authz as authz
import ckan.model as model
import ckan.plugins.toolkit as tk
import ckan.lib.helpers as h

from ckanext.toolbelt.decorators import Collector
from ckanext.scheming.helpers import scheming_get_dataset_schema

import ckanext.datavic_iar_theme.config as conf


log = logging.getLogger(__name__)
helper, get_helpers = Collector("vic_iar").split()


@helper
def organization_list() -> list[dict[str, Any]]:
    return tk.get_action("organization_list")(
        {}, {"all_fields": True, "include_dataset_count": False}
    )


@helper
def get_parent_orgs(output: Optional[str] = None) -> list[dict[str, str]] | list[str]:
    organisations: list[model.Group] = model.Group.get_top_level_groups("organization")

    if output == "list":
        parent_orgs = [org.name for org in organisations]
    else:
        parent_orgs = [{"value": "", "text": "Please select..."}]
        for org in organisations:
            parent_orgs.append({"value": org.name, "text": org.display_name})

    return parent_orgs


@helper
def search_form_group_list() -> list[dict[str, Any]]:
    return tk.get_action("group_list")(
        {}, {"all_fields": True, "include_dataset_count": False}
    )


@helper
def format_list() -> list[str]:
    """Return a list of all available resources on portal"""

    query = (
        model.Session.query(model.Resource.format)
        .filter(model.Resource.state == model.State.ACTIVE)
        .group_by(model.Resource.format)
        .order_by(func.lower(model.Resource.format))
    )

    formats = [
        resource.format.upper().split('.')[-1] for resource in query if resource.format
    ]
    unique_formats = set(formats)

    return sorted(list(unique_formats))


@helper
def get_parent_site_url():
    return conf.get_parent_site_url().rstrip("/")


@helper
def hotjar_tracking_enabled():
    return conf.hotjar_tracking_enabled()


@helper
def get_hotjar_hsid():
    return conf.get_hotjar_hsid()


@helper
def get_hotjar_hjsv():
    return conf.get_hotjar_hjsv()


@helper
def linked_user(user: str, maxlength: int = 0, avatar: int = 20):
    """Custom linked_user helper"""
    user_obj: model.User | None = model.User.get(user)

    if not user_obj:
        return user

    name: str = (
        user_obj.name if model.User.VALID_NAME.match(user_obj.name) else user_obj.id
    )
    display_name = user_obj.display_name

    if maxlength and len(user_obj.display_name) > maxlength:
        display_name = display_name[:maxlength] + "..."

    # DataVic custom changes to show different links depending on user access
    url: str = (
        h.url_for("user.read", id=name)
        if h.check_access("package_create")
        else h.url_for("activity.user_activity", id=name)
    )  # type: ignore

    return h.literal(
        "{icon} {link}".format(
            icon=h.gravatar(email_hash=user_obj.email_hash, size=avatar),
            link=h.link_to(display_name, url),
        )
    )


@helper
def visibility_list() -> list[dict[str, str]]:
    return [
        {"value": "all", "label": "Open to the public and VPS only"},
        {"value": "private", "label": "Open to VPS only"},
        {"value": "public", "label": "Open to the public"},
    ]


@helper
def featured_resource_preview(package: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Return a featured resource preview
        - It takes only CSV resources with an existing preview
        - Only resources uploaded to datastore
        - Only not historical resources
    """

    featured_preview = None

    resource_groups: list[list[dict[str, Any]]] = tk.h.group_resources_by_temporal_range(
        package.get("resources", [])
    )

    resources = resource_groups[0] if resource_groups else []

    for resource in resources:
        if resource.get("format", "").lower() != "csv":
            continue

        if not resource.get("datastore_active"):
            continue

        try:
            resource_views = tk.get_action("resource_view_list")(
                {}, {"id": resource["id"]}
            )
        except tk.ObjectNotFound:
            pass
        else:
            if resource_views:
                featured_preview = {"preview": resource_views[0], "resource": resource}

    return featured_preview


def _get_last_resource_if_historical(package: dict[str, Any]) -> dict[str, Any] | None:
    """If the dataset contains historical resources, return the most recent one"""
    historical_resources = tk.h.historical_resources_list(package.get("resources", []))

    if len(historical_resources) <= 1:
        return

    if historical_resources[1].get("period_start"):
        return historical_resources[0]

    return


@helper
def get_route_after_login_config():
    return tk.config.get("ckan.auth.route_after_login")


@helper
def get_came_from_url(came_from: str | None) -> str:
    if came_from is None:
        return tk.url_for(
            tk.config.get("ckan.auth.route_after_login") or "dataset.search"
        )
    return came_from


@helper
def role_in_org(organization_id, user_name):
    return authz.users_role_for_group_or_org(organization_id, user_name)


@helper
def prepare_general_fields(data: dict[str, Any]) -> str:
    schema: dict[str, Any] | None = scheming_get_dataset_schema(
        data.get("type", "dataset")
    )

    if not schema:
        return json.dumps({})

    new_data = {
        field : _get_value_for_field(data.get(field, "")) for field in [
            field["field_name"] for field in schema[
                "dataset_fields"
                ]
            ]
    }
    if new_data.get('tag_string'):
        new_data['tag_string'] = ','.join([i.strip() for i in new_data['tag_string'].split(',')])

    return json.dumps(new_data)


@helper
def get_metadata_groups(data):
    if data and not data.get('tag_string'):
        data['tag_string'] = ', '.join(
            h.dict_list_reduce(data.get('tags', {}), 'name')
        )

    schema: dict[str, Any] | None = scheming_get_dataset_schema(
        data.get("type", "dataset")
    )

    if not schema:
        return [], []

    groups = []
    fields = schema["dataset_fields"]

    for field in schema["dataset_fields"]:
        if field.get("display_group") and field["display_group"] not in groups:
            groups.append(field["display_group"])
    return groups, fields


def _get_value_for_field(value):
    # Boolean in forms shown with Capitalize
    if (type(value) is bool):
        value = str(value).capitalize()
    return value
