from theme import *
from JsonComponent import *

PROJECT_VERSION = "1.0.0"

DEFAULT_PROJECT_NAME = "default_project"
DEFAULT_PROJECT_PATH = ""


from PlotCurve import PlotCurve  # Ensure PlotCurve is imported
from CanvasSpikes import CanvasSpikes


class Project:
    def __init__(self):
        self.name = DEFAULT_PROJECT_NAME
        self.version = PROJECT_VERSION
        self.curves = []  # List to store PlotCurve instances
        
        self.spikes = []

        self.curve_to_spikes_links = {}

        self.backup_identifier = ""

    def to_json_component(self):
        properties = {
            "version": self.version,
            "curves": [curve.to_json_component().to_dict() for curve in self.curves],
            "spikes": [spike.to_json_component().to_dict() for spike in self.spikes],
            "curve_to_spikes_links": self.curve_to_spikes_links,
            "backup_identifier": self.backup_identifier
        }
        return JsonComponent(self.name, properties)

    @classmethod
    def from_json_component(cls, component, curve_plot, bars_plot):
        project = cls()
        project.name = component.name
        project.version = component.properties.get("version", PROJECT_VERSION)
        #Could change computing based off the version
        project.curves = [PlotCurve.from_json_component(JsonComponent.from_dict(c), curve_plot) for c in component.properties.get("curves", [])]
        project.spikes = [CanvasSpikes.from_json_component(JsonComponent.from_dict(c), bars_plot) for c in component.properties.get("spikes", [])]
        project.curve_to_spikes_links = component.properties.get("curve_to_spikes_links", {})
        project.backup_identifier = component.properties.get("backup_identifier", "")
        return project