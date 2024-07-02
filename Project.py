import os
import shutil
import tempfile
import glob
from theme import *
from JsonComponent import *

from PlotCurve import PlotCurve
from CanvasSpikes import CanvasSpikes

from FileManager import FileManager

from SpikeCluster import *
import saver

PROJECT_VERSION = "1.0.0"
DEFAULT_PROJECT_NAME = "default_project"


class Project:
    tmpdir = tempfile.TemporaryDirectory()
    def __init__(self):
        self.name = DEFAULT_PROJECT_NAME
        self.version = PROJECT_VERSION
        self.packed = False

        self.curves = []
        self.spikes = []

        self.curve_to_spikes_links = {}
        self.target_curve = ""
        self.current_curve = ""

        self.backup_identifier = ""

    def to_json_component(self):
        properties = {
            "version": self.version,
            "packed": self.packed,
            "curves": [curve.to_json_component().to_dict() for curve in self.curves],
            "spikes": [spike.to_json_component().to_dict() for spike in self.spikes],
            "curve_to_spikes_links": self.curve_to_spikes_links,
            "target_curve": self.target_curve,
            "current_curve": self.current_curve,
            "backup_identifier": self.backup_identifier
        }
        return JsonComponent(self.name, properties)

    @classmethod
    def from_json_component(cls, component, curve_plot, bars_plot):
        project = cls()
        project.name = component.name
        project.version = component.properties.get("version", PROJECT_VERSION)
        project.packed = component.properties.get("packed", False)
        #Could change computing based off the version
        project.curves = [PlotCurve.from_json_component(JsonComponent.from_dict(c), curve_plot) for c in component.properties.get("curves", [])]
        project.spikes = [CanvasSpikes.from_json_component(JsonComponent.from_dict(c), bars_plot) for c in component.properties.get("spikes", [])]
        #print([[x.x for x in spike.spikes_data] for spike in project.spikes])
        project.curve_to_spikes_links = component.properties.get("curve_to_spikes_links", {})

        project.target_curve = component.properties.get("target_curve", "")
        project.current_curve = component.properties.get("current_curve", "")

        project.backup_identifier = component.properties.get("backup_identifier", "")
        return project


    def relocate(self, new_dir):
        for curve in self.curves:
            curve_file = curve.get_file_path()
            if curve_file:
                new_path = os.path.join(new_dir, os.path.basename(curve_file))
                a = os.path.abspath(curve_file)
                b = os.path.abspath(new_path)
                if a == b:
                    continue
                shutil.copy(curve_file, new_path)
                curve.update_file_path(os.path.relpath(new_path, new_dir))

        for spike in self.spikes:
            spike_file = spike.get_file_path()
            if spike_file:
                new_path = os.path.join(new_dir, os.path.basename(spike_file))
                a = os.path.abspath(spike_file)
                b = os.path.abspath(new_path)
                if a == b:
                    continue
                shutil.copy(spike_file, new_path)
                spike.update_file_path(os.path.relpath(new_path, new_dir))

        self.backup_identifier = os.path.relpath(new_dir, os.path.dirname(self.name))

    def pack(self, file_path, file_name, relocate_files):
        FileManager.pack(self, file_path, file_name, relocate_files)

    @staticmethod
    def unpack(file_path):
        return FileManager.unpack(file_path)

    def read(self, file_path, target_file_name):
        return FileManager.read(file_path, target_file_name)

    def write(self, file_path, target_file_name, data):
        FileManager.write(file_path, target_file_name, data)

    def save(self, file_path, pack_files):
        if pack_files:
            bi = 0
            for curve in self.curves:
                if os.path.exists(curve.file_path):
                    ext = curve.file_path.split(".")[-1]
                    future_path = ("./curve{}.{}").format(bi, ext)
                    if os.path.exists(future_path):
                        bi += 1
                        continue
                    shutil.copyfile(curve.file_path, future_path)
                    curve.update_file_path(future_path)
                    print("Copied", curve.file_path, "to the archive")
                else:
                    compiled = SpikeCluster.merge(curve.spikes_clusters)
                    saver.write_XY(("./curve{}.xy").format(bi), compiled.spikesX, compiled.spikesY)
                    curve.update_file_path(("./curve{}.xy").format(bi))
                    print("Couldn't find the", curve.file_path, "file, so compiled the curveto the archive")
                bi += 1
            bi = 0
            for bars in self.spikes:
                #we can't just copy over the file here because the spikes are a changing part in the files
                saver.write_ASG(("./spike{}.asg").format(bi), bars.spikes_data)
                bars.update_file_path(("./spike{}.asg").format(bi))
                bi += 1
        self.pack(file_path, self.name, pack_files)
        return os.path.join(file_path, self.name + FileManager.DEFAULT_PROJECT_EXTENSION)

    @staticmethod
    def load(file_path, curve_plot, bars_plot):
        unpacked_file = Project.unpack(file_path)
        js_files = []
        for file in os.listdir(unpacked_file):
            if file.endswith(".json"):
                js_files.append(os.path.join(unpacked_file, file))
        if not js_files:
            return None
        project_path = js_files[0]
        p = JsonComponent.load(project_path)
        return Project.from_json_component(p, curve_plot, bars_plot)

    def get_file(self, target_file_name):
        return FileManager.read(self.name, target_file_name)

    @classmethod
    def cleanup(cls):
        FileManager.cleanup()

    @classmethod
    def refresh(cls):
        FileManager.refresh()