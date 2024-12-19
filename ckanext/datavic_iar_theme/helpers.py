from __future__ import annotations

import json
import logging
from typing import Optional, Any
from bs4 import BeautifulSoup

from sqlalchemy.sql import func

import ckan.authz as authz
import ckan.model as model
import ckan.plugins.toolkit as tk
import ckan.lib.helpers as h

from ckanext.harvest.model import HarvestSource
import ckanext.activity.model.activity as model_activity
from ckanext.toolbelt.decorators import Collector
from ckanext.scheming.helpers import scheming_get_dataset_schema

import ckanext.datavic_iar_theme.config as conf
import ckanext.datavicmain.const as const


log = logging.getLogger(__name__)
helper, get_helpers = Collector("vic_iar").split()


@helper
def organization_list() -> list[dict[str, Any]]:
    return tk.get_action("organization_list")(
        {}, {"all_fields": True, "include_dataset_count": False}
    )


@helper
def get_parent_orgs(output: Optional[str] = None) -> list[dict[str, str]] | list[str]:
    """Get a list of parent organisations options. Exclude restricted ones"""
    organisations: list[model.Group] = model.Group.get_top_level_groups("organization")

    parent_orgs = [{"value": "", "text": "Please select..."}]

    for org in organisations:
        if org.extras.get(const.ORG_VISIBILITY_FIELD) == const.ORG_RESTRICTED:
            continue

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
        resource.format.upper().split(".")[-1] for resource in query if resource.format
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

    resource_groups: list[list[dict[str, Any]]] = (
        tk.h.group_resources_by_temporal_range(package.get("resources", []))
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


@helper
def is_delwp_vector_data(resources: list[dict[str, Any]]) -> bool:
    for res in resources:
        if res["format"].lower() in [
            "dwg",
            "dxf",
            "gdb",
            "shp",
            "mif",
            "tab",
            "extended tab",
            "mapinfo",
        ]:
            return True

    return False


@helper
def is_delwp_raster_data(resources: list[dict[str, Any]]) -> bool:
    for res in resources:
        if res["format"].lower() in [
            "ecw",
            "geotiff",
            "jpeg",
            "jp2",
            "jpeg 2000",
            "tiff",
            "lass",
            "xyz",
        ]:
            return True

    return False


@helper
def is_delwp_dataset(package: dict[str, Any]) -> bool:
    """Check if the dataset is harvested with delwp harvester"""
    for extra in package.get("extras", []):
        if extra["key"] != "harvest_source_type":
            continue

        if extra["value"] == "delwp":
            return True

    return False


@helper
def is_delwp_dataset_restricted(package: dict[str, Any]) -> bool:
    """Check if the delwp dataset is restricted"""
    for extra in package.get("extras", []):
        if extra["key"] != "delwp_restricted":
            continue

        return tk.asbool(extra["value"])

    return False


@helper
def get_route_after_login_config():
    return tk.config.get("ckan.auth.route_after_login")


@helper
def get_came_from_url(came_from: str | None) -> str:

    return came_from or tk.url_for(
        tk.config.get("ckan.auth.route_after_login") or "dataset.search"
    )


@helper
def datastore_loaded_resources(pkg_dict: dict[str, Any]) -> list[str]:
    """Return a list of the dataset resources that are loaded to the datastore"""
    if not pkg_dict["resources"]:
        return []
    return [
        resource["id"]
        for resource in pkg_dict["resources"]
        if resource["datastore_active"]
    ]


@helper
def get_header_structure(userobj: model.User | None) -> list[dict[str, Any]]:
    is_logged_in: bool = bool(userobj)
    is_sysadmin: bool = bool(userobj) and userobj.sysadmin

    try:
        can_create_packages = (
            bool(userobj)
            and tk.check_access("package_create", {"user": userobj.name}, {})
            and True
        )
    except tk.NotAuthorized:
        can_create_packages = False

    return [
        {
            "title": tk._("My account"),
            "url": "#",
            "hide": not is_logged_in,
            "child": [
                {
                    "title": tk._("Dashboard"),
                    "url": tk.h.url_for("dashboard.datasets"),
                    "hide": not is_logged_in or not can_create_packages,
                },
                {
                    "title": tk._("Profile"),
                    "url": (
                        tk.h.url_for("user.read", id=userobj.name)
                        if is_logged_in
                        else "#"
                    ),
                    "hide": not is_logged_in,
                },
                {
                    "title": tk._("Sysadmin settings"),
                    "url": tk.h.url_for("admin.index"),
                    "hide": not is_sysadmin,
                },
                {
                    "title": tk._("Homepage content"),
                    "url": tk.h.url_for("datavic_home.manage"),
                    "hide": not is_sysadmin,
                },
                {
                    "title": tk._("Pages"),
                    "url": tk.h.url_for("pages.pages_index"),
                    "hide": not is_sysadmin,
                },
                {
                    "title": tk._("Blog"),
                    "url": tk.h.url_for("pages.blog_index"),
                    "hide": not is_sysadmin,
                },
                {
                    "title": tk._("Bulk manager"),
                    "url": tk.h.url_for("bulk.manager"),
                    "hide": not is_sysadmin,
                }
            ],
        },
        {
            "title": tk._("Support"),
            "url": "#",
            "hide": not is_logged_in,
            "child": [
                {
                    "title": tk._("User guides"),
                    "url": f"/{conf.get_pages_base_url()}/user-guides",
                    "hide": _get_page_item("user-guides") is None,
                },
                {
                    "title": tk._("Contact us"),
                    "url": f"/{conf.get_pages_base_url()}/contact-us",
                    "hide": _get_page_item("contact-us") is None,
                },
                {
                    "title": tk._("About us"),
                    "url": f"/{conf.get_pages_base_url()}/about-us",
                    "hide": _get_page_item("about-us") is None,
                },
                {
                    "title": tk._("News and announcements"),
                    "url": tk.h.url_for("pages.blog_index"),
                },
            ],
        },
        {
            "title": tk._("Data sharing"),
            "url": "#",
            "hide": not is_logged_in,
            "child": [
                {
                    "title": tk._("Data sharing resources"),
                    "url": f"/{conf.get_pages_base_url()}/data-sharing-resources",
                    "hide": _get_page_item("data-sharing-resources") is None,
                }
            ],
        },
        {
            "title": tk._("Datasets"),
            "url": "#",
            "hide": not is_logged_in,
            "child": [
                {"title": tk._("Search"), "url": h.url_for("dataset.search")},
                {
                    "title": tk._("Browse by organisation"),
                    "url": tk.h.url_for("organization.index"),
                },
                {
                    "title": tk._("Browse by category"),
                    "url": tk.h.url_for("group.index"),
                },
            ],
        },
        {
            "title": tk._("DaAS"),
            "subtitle": tk._("""Digital and Analytics Service (DaAS)"""),
            "url": "#",
            "hide": not is_logged_in,
            "child": [
                {
                    "title": page["title"],
                    "url": _build_page_url(page),
                }
                for page in _get_daas_pages()
            ],
        },
    ]


def _get_page_item(name: str) -> dict[str, Any] | None:
    """Return a ckanext-pages page item based on the page name"""
    try:
        tk.check_access('ckanext_pages_show', {}, {"page": name})
    except tk.NotAuthorized:
        return None

    result = tk.get_action("ckanext_pages_show")({}, {"page": name})

    if not result:
        return None

    if result["page_type"] != "page":
        return None

    return result


def _build_page_url(page: dict[str, Any]) -> str:
    """Build a page URL for ckanext-pages entity based on the page type and name"""
    page_type = "blog" if page["page_type"] == "blog" else conf.get_pages_base_url()

    return f"/{page_type}/{page['name']}"


def _get_daas_pages():
    """Return a list of DaAS pages. Exclude pages that are not DaAS related,
    but were created with ckanext-pages"""
    exclude = ("user-guides", "contact-us", "data-sharing-resources")
    result = tk.get_action("ckanext_pages_list")({}, {"order": True, "private": False})

    return [
        page
        for page in result
        if (page["page_type"] == "page" and page["name"] not in exclude)
    ]


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


@helper
def harvester_list() -> list[dict[str, Any]]:
    """Return a list of all available harvesters on the portal"""

    query = (
        model.Session.query(HarvestSource)
        .filter(HarvestSource.active.is_(True))
        .order_by(HarvestSource.created.desc()) # type: ignore
    )

    return [{"value": "", "label": "All"}] + [
        {"value": harvester.id, "label": harvester.title} for harvester in query
    ]


@helper
def datastore_dictionary(resource_id: str, resource_view_id: str):
    """
    Return the data dictionary info for a resource
    """
    try:
        resource_view = tk.get_action("resource_view_show")(
            {},
            {"id": resource_view_id}
        )
        headers = [
            f for f in tk.get_action("datastore_search")(
                {},
                {
                    "resource_id": resource_id,
                    "limit": 0,
                    "include_total": False
                }
            )["fields"]
            if not f["id"].startswith("_")
        ]

        if "show_fields" in resource_view:
            headers = [c for c in headers if c["id"] in resource_view["show_fields"]]

        return headers

    except (tk.ObjectNotFound, tk.NotAuthorized):
        return []


@helper
def get_package_title(package_id: str) -> str:
    user = tk.g.user
    context = {"user": user}
    try:
        pkg = tk.get_action("package_show")(context, {"id": package_id})
    except (tk.ObjectNotFound, tk.NotAuthorized):
        tk.abort(403)
    return pkg.get("title", "")


@helper
def extra_html_restrictions(text):
    filtered_text = BeautifulSoup(text,"html.parser")

    # Lets remove all script tags from the HTML markup
    for script in filtered_text.find_all('script'):
        script.extract()

    return str(filtered_text)


@helper
def resource_attributes(attrs):
    try:
        attrs = json.loads(attrs)
    except ValueError:
        return None

    return attrs


@helper
def check_last_activity(activity):
    # Taken originally fron action.py for acitivies
    prev_activity = (
        model.Session.query(model_activity.Activity.id)
        .filter_by(object_id=activity["object_id"])
        .filter(model_activity.Activity.timestamp < activity["timestamp"])
        .order_by(
            # type_ignore_reason: incomplete SQLAlchemy types
            model_activity.Activity.timestamp.desc()  # type: ignore
        )
        .first()
    )

    return prev_activity if prev_activity else None
