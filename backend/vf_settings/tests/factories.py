from projectroles.app_settings import AppSettingAPI

app_settings = AppSettingAPI()


PROJECT_SETTINGS_A = {
    "user_defined_tags": "",
    "disable_pedigree_sex_check": False,
    "exclude_from_inhouse_db": False,
    "ts_tv_valid_range": "1-2",
    "test_param": "test project set A",
}

USER_SETTINGS_A = {
    "umd_predictor_api_token": "",
    "ga4gh_beacon_network_widget_enabled": False,
    "latest_version_seen_changelog": "",
    "test_param": "test user set A",
}

PROJECT_USER_SETTINGS_A = {
    "test_param": "test project user set A",
}

SITE_SETTINGS_A = {
    "test_param": "test site set A",
}

PROJECT_DEFINITIONS = {
    "disable_pedigree_sex_check": {
        "app_name": "variants",
        "internal_name": "disable_pedigree_sex_check__project",
    },
    "exclude_from_inhouse_db": {
        "app_name": "variants",
        "internal_name": "exclude_from_inhouse_db__project",
    },
    "ts_tv_valid_range": {
        "app_name": "variants",
        "internal_name": "ts_tv_valid_range__project",
    },
    "user_defined_tags": {
        "app_name": "variants",
        "internal_name": "user_defined_tags__project",
    },
    "test_param": {
        "app_name": "variants",
        "internal_name": "test_param__project",
    },
}

SITE_DEFINITIONS = {
    "test_param": {
        "app_name": "variants",
        "internal_name": "test_param__site",
    },
}

USER_DEFINITIONS = {
    "ga4gh_beacon_network_widget_enabled": {
        "app_name": "variants",
        "internal_name": "ga4gh_beacon_network_widget_enabled__user",
    },
    "latest_version_seen_changelog": {
        "app_name": "variants",
        "internal_name": "latest_version_seen_changelog__user",
    },
    "test_param": {
        "app_name": "variants",
        "internal_name": "test_param__user",
    },
    "umd_predictor_api_token": {
        "app_name": "variants",
        "internal_name": "umd_predictor_api_token__user",
    },
}


PROJECT_USER_DEFINITIONS = {
    "test_param": {
        "app_name": "variants",
        "internal_name": "test_param__project_user",
    },
}


def get_project_defaults(project):
    return {
        "user_defined_tags": app_settings.get_default(
            "variants", "user_defined_tags__project", project=project
        ),
        "disable_pedigree_sex_check": app_settings.get_default(
            "variants", "disable_pedigree_sex_check__project", project=project
        ),
        "exclude_from_inhouse_db": app_settings.get_default(
            "variants", "exclude_from_inhouse_db__project", project=project
        ),
        "ts_tv_valid_range": app_settings.get_default(
            "variants", "ts_tv_valid_range__project", project=project
        ),
        "test_param": app_settings.get_default("variants", "test_param__project", project=project),
    }


def get_user_defaults(user):
    return {
        "umd_predictor_api_token": app_settings.get_default(
            "variants", "umd_predictor_api_token__user", user=user
        ),
        "ga4gh_beacon_network_widget_enabled": app_settings.get_default(
            "variants", "ga4gh_beacon_network_widget_enabled__user", user=user
        ),
        "latest_version_seen_changelog": app_settings.get_default(
            "variants", "latest_version_seen_changelog__user", user=user
        ),
        "test_param": app_settings.get_default("variants", "test_param__user", user=user),
    }


def get_site_defaults():
    return {"test_param": app_settings.get_default("variants", "test_param__site")}


def get_project_user_defaults(project, user):
    return {
        "test_param": app_settings.get_default(
            "variants", "test_param__project_user", project=project, user=user
        )
    }


def get_all_defaults_no_project(user):
    return {
        **get_user_defaults(user),
        **get_site_defaults(),
        **get_project_defaults(None),
        **get_project_user_defaults(None, user),
    }


def get_all_defaults(project, user):
    return {
        **get_user_defaults(user),
        **get_site_defaults(),
        **get_project_defaults(project),
        **get_project_user_defaults(project, user),
    }
