from __future__ import annotations

import ckan.plugins.toolkit as tk
from ckan.common import session

from ckanext.oidc_pkce.signals import user_sync

@user_sync.connect
def on_user_sync(user_id: str):
    session["ckanext:datavic_iar_theme:oidc_migrated_account"] = True
