from __future__ import annotations

import ckan.plugins.toolkit as tk


CONFIG_PARENT_SITE_URL = "ckan.parent_site_url"
DEFAULT_PARENT_SITE_URL = "https://www.data.vic.gov.au/"

CONFIG_HOTJAR_ENABLED = "ckan.tracking.hotjar_enabled"
CONFIG_HOTJAR_HJID = "ckan.tracking.hotjar.hjid"
CONFIG_HOTJAR_HJSV = "ckan.tracking.hotjar.hjsv"


def get_parent_site_url() -> str:
    return tk.config.get(CONFIG_PARENT_SITE_URL, DEFAULT_PARENT_SITE_URL)


def hotjar_tracking_enabled() -> bool:
    return tk.asbool(tk.config.get(CONFIG_HOTJAR_ENABLED))


def get_hotjar_hsid() -> str | None:
    return tk.config.get(CONFIG_HOTJAR_HJID)


def get_hotjar_hjsv() -> str | None:
    return tk.config.get(CONFIG_HOTJAR_HJSV)

