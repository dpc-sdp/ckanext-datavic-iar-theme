from __future__ import annotations

import logging
from typing import Optional, Any

from sqlalchemy.sql import func

import ckan.model as model
import ckan.plugins.toolkit as tk
import ckan.lib.helpers as h

from ckanext.toolbelt.decorators import Collector

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
    return [resource["id"] for resource in pkg_dict["resources"] if resource["datastore_active"]]


@helper
def show_blog_button():
    return conf.show_blog_button()


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
                    "title": tk._("Pages"),
                    "url": tk.h.url_for("pages.pages_index"),
                    "hide": not is_logged_in,
                },
                {
                    "title": tk._("Blog"),
                    "url": tk.h.url_for("pages.blog_index"),
                    "hide": not is_logged_in,
                },
            ],
        },
        {
            "title": tk._("Support"),
            "url": "#",
            "hide": not is_logged_in,
            "child": [
                {"title": tk._("User guides"), "url": tk.h.url_for("home.index")},
                {
                    "title": tk._("Contact us"),
                    "url": tk.h.vic_iar_get_parent_site_url() + "/contact-us",
                },
                {"title": tk._("About us"), "url": tk.h.url_for("home.about")},
                {
                    "title": tk._("News and announcements"),
                    "url": tk.h.url_for("home.about"),
                },
            ],
        },
        {
            "title": tk._("Data sharing"),
            "url": "#",
            "hide": not is_logged_in,
            "child": [
                {
                    "title": tk._("Data sharing framework"),
                    "url": tk.h.url_for("home.index"),
                },
                {"title": tk._("Data ethics"), "url": tk.h.url_for("home.index")},
            ],
        },
        {
            "title": tk._("Datasets"),
            "url": "#",
            "hide": True,
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
            "title": tk._("Digital and Analytics Service (DaAS)"),
            "subtitle": tk._("DaAS"),
            "url": "#",
            "hide": not is_logged_in,
            "child": [
                {
                    "title": page["title"],
                    "url": _build_page_url(page),
                }
                for page in tk.get_action("ckanext_pages_list")(
                    {}, {"order": True, "private": False}
                )
            ],
        },
    ]


def _build_page_url(page: dict[str, Any]) -> str:
    page_type = "blog" if page["page_type"] == "blog" else conf.get_pages_base_url()

    return f"/{page_type}/{page['name']}"
