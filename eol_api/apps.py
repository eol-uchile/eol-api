# Installed packages (via pip)
from django.apps import AppConfig

# Installed packages (via pip)
from openedx.core.djangoapps.plugins.constants import (
    PluginSettings,
    PluginURLs,
    ProjectType,
    SettingsType,
)


class EOLAPIConfig(AppConfig):
    name = 'eol_api'
    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: 'eol_api',
                PluginURLs.REGEX: r'^',
                PluginURLs.RELATIVE_PATH: 'urls',
            },
        },
        PluginSettings.CONFIG: {
            ProjectType.CMS: {
                SettingsType.COMMON: {
                    PluginSettings.RELATIVE_PATH: "settings.common"}},
            ProjectType.LMS: {
                SettingsType.COMMON: {
                    PluginSettings.RELATIVE_PATH: "settings.common"}},
        },
    }
