from theme import Theme
from JsonComponent import *

PROJECT_VERSION = "1.0.0"

DEFAULT_PROJECT_NAME = "default_project"
DEFAULT_PROJECT_PATH = ""


class Project:
    def __init__(self):
        self.name = DEFAULT_PROJECT_NAME
        self.version = PROJECT_VERSION
        self.curve_paths = {}
        self.curve_x_offset = 0
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
            "curve_x_offset": {0: self.curve_x_offset},
            "curve_view_ranges": {0: self.curve_view_ranges[0], 1: self.curve_view_ranges[1]},
            "curve_ranges": self.curve_ranges,
            "curve_themes": {k: v for k, v in self.curve_themes.items()},
            "spikes_paths": self.spikes_paths,
            "spikes_themes": {k: v for k, v in self.spikes_themes.items()},
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
        curve_x_offset = component.properties.get("curve_x_offset", {"0": "0"})
        project.curve_x_offset = int(curve_x_offset["0"])
        view_ranges = component.properties.get("curve_view_ranges", {"0": "0", "1": "-1"})
        project.curve_view_ranges = (int(view_ranges["0"]), int(view_ranges["1"]))
        project.curve_ranges = component.properties.get("curve_ranges", {})
        project.curve_themes = {k: v for k, v in component.properties.get("curve_themes", "graph1").items()}
        project.spikes_paths = component.properties.get("spikes_paths", {})
        project.spikes_themes = {k: v for k, v in component.properties.get("spikes_themes", "bars1").items()}
        project.curve_to_spikes_links = component.properties.get("curve_to_spikes_links", {})
        project.backup_identifier = component.properties.get("backup_identifier", "")
        return project