from theme import Theme
from JsonComponent import *

PROJECT_VERSION = "1.0.0"

DEFAULT_PROJECT_NAME = "last_project"
DEFAULT_PROJECT_PATH = ""


class Project:
    def __init__(self):
        self.name = DEFAULT_PROJECT_NAME
        self.version = PROJECT_VERSION
        self.file_path = DEFAULT_PROJECT_PATH
        self.curve_paths = {}
        self.curve_view_ranges = (0, -1)
        self.curve_ranges = {}
        self.curve_themes = {}

        self.spikes_paths = {}
        self.spikes_themes = {}

        self.curve_to_spikes_links = {}

        self.backup_identifier = ""

    def to_json_component(self):
        properties = {
            "version": self.version,
            "curve_paths": self.curve_paths,
            "curve_view_ranges": {0: self.curve_view_ranges[0], 1: self.curve_view_ranges[1]},
            "curve_ranges": self.curve_ranges,
            "curve_themes": {k: v.to_dict() for k, v in self.curve_themes.items()},
            "spikes_paths": self.spikes_paths,
            "spikes_themes": {k: v.to_dict() for k, v in self.spikes_themes.items()},
            "curve_to_spikes_links": self.curve_to_spikes_links,
            "backup_identifier": self.backup_identifier
        }
        return JsonComponent(self.name, properties)

    @classmethod
    def from_json_component(cls, component):
        project = cls()
        project.name = component.name
        project.version = component.properties.get("version", PROJECT_VERSION)
        #Could change computing based off the version
        project.curve_paths = component.properties.get("curve_paths", {})
        view_ranges = component.properties.get("curve_view_ranges", {0: 0, 1: -1})
        project.curve_view_ranges = (view_ranges[0], view_ranges[1])
        project.curve_ranges = component.properties.get("curve_ranges", {})
        project.curve_themes = {k: Theme.from_dict(v) for k, v in component.properties.get("curve_themes", {}).items()}
        project.spikes_paths = component.properties.get("spikes_paths", {})
        project.spikes_themes = {k: Theme.from_dict(v) for k, v in component.properties.get("spikes_themes", {}).items()}
        project.curve_to_spikes_links = component.properties.get("curve_to_spikes_links", {})
        project.backup_identifier = component.properties.get("backup_identifier", "")
        return project