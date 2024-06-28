import os
import shutil
import tempfile
import glob
from theme import *
from JsonComponent import *

PROJECT_VERSION = "1.0.0"

DEFAULT_PROJECT_NAME = "default_project"
DEFAULT_PROJECT_PATH = ""

DEFAULT_PROJECT_EXTENSION = ".proj"


from PlotCurve import PlotCurve  # Ensure PlotCurve is imported
from CanvasSpikes import CanvasSpikes


class Project:
    tmpdir = tempfile.TemporaryDirectory()
    def __init__(self):
        self.name = DEFAULT_PROJECT_NAME
        self.version = PROJECT_VERSION
        self.packed = False

        self.curves = []  # List to store PlotCurve instances
        
        self.spikes = []

        self.curve_to_spikes_links = {}

        self.backup_identifier = ""

    def to_json_component(self):
        properties = {
            "version": self.version,
            "packed": self.packed,
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
        project.packed = component.properties.get("packed", False)
        #Could change computing based off the version
        project.curves = [PlotCurve.from_json_component(JsonComponent.from_dict(c), curve_plot) for c in component.properties.get("curves", [])]
        project.spikes = [CanvasSpikes.from_json_component(JsonComponent.from_dict(c), bars_plot) for c in component.properties.get("spikes", [])]
        project.curve_to_spikes_links = component.properties.get("curve_to_spikes_links", {})
        project.backup_identifier = component.properties.get("backup_identifier", "")
        return project

    def relocate(self, new_dir):        
        for curve in self.curves:
            curve_file = curve.get_file_path()
            if curve_file:
                new_path = os.path.join(new_dir, os.path.basename(curve_file))
                shutil.copy(curve_file, new_path)
                curve.update_file_path(os.path.relpath(new_path, new_dir))

        for spike in self.spikes:
            spike_file = spike.get_file_path()
            if spike_file:
                new_path = os.path.join(new_dir, os.path.basename(spike_file))
                shutil.copy(spike_file, new_path)
                spike.update_file_path(os.path.relpath(new_path, new_dir))

        # Update internal paths
        self.backup_identifier = os.path.relpath(new_dir, os.path.dirname(self.name))
    
    def pack(self, file_path, file_name, relocate_files):
        file_name = file_name + DEFAULT_PROJECT_EXTENSION
        file = os.path.join(file_path, file_name)
        tmp_archive = os.path.join(self.tmpdir.name, 'temp_archive')
        print("Creating dir", tmp_archive)
        os.makedirs(tmp_archive, exist_ok=True)
        if relocate_files:
            self.relocate(file_path)
        js = self.to_json_component()
        js.save(os.path.join(tmp_archive, self.name + '.json'))

        shutil.make_archive(tmp_archive, 'zip', self.tmpdir.name, 'temp_archive')
        os.rename(tmp_archive + '.zip', os.path.join(self.tmpdir.name, file_name))
    
    @staticmethod
    def unpack(file_path):
        temp_zip = os.path.join(Project.tmpdir.name, 'temp_archive.zip')
        shutil.copy(file_path, temp_zip)
        shutil.unpack_archive(temp_zip, Project.tmpdir.name)
        os.remove(temp_zip)
        return os.path.join(Project.tmpdir.name, 'temp_archive') #os.path.join(Project.tmpdir.name, file_path.split('/')[-1].split('.')[0])

    def read(self, file_path, file_name, target_file_name):
        self.unpack(file_path, file_name)
        target_file_path = os.path.join(self.tmpdir.name, target_file_name)
        if os.path.exists(target_file_path):
            with open(target_file_path, 'r') as f:
                data = f.read()
        else:
            data = None
        self.pack(file_path, file_name)
        return data

    def write(self, file_path, file_name, target_file_name, data):
        self.unpack(file_path, file_name)
        target_file_path = os.path.join(self.tmpdir.name, target_file_name)
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
        with open(target_file_path, 'w') as f:
            f.write(data)
        self.pack(file_path, file_name)

    def save(self, file_path, pack_files):
        self.pack(file_path, self.name, pack_files)
        tmp_path = os.path.join(self.tmpdir.name, self.name + DEFAULT_PROJECT_EXTENSION)
        project_path = os.path.join(file_path, self.name + DEFAULT_PROJECT_EXTENSION)
        print("Saving project by copying from", tmp_path, "to", project_path)
        shutil.copy(tmp_path, project_path)
        return project_path
    
    def load(file_path, curve_plot, bars_plot):
        #Project.cleanup()
        #Project.tmpdir = tempfile.TemporaryDirectory()
        unpacked_file = Project.unpack(file_path)
        js_files = []
        for file in os.listdir(unpacked_file):
            if file.endswith(".json"):
                js_files.append(os.path.join(unpacked_file, file))
                print("Project file (", unpacked_file, ") ", file.lower())
        if not js_files:
            print("Error, no project file for", file_path, "under the unpacked file location", unpacked_file)
            return None

        project_path = js_files[0]

        p = JsonComponent.load(project_path)
        return Project.from_json_component(p, curve_plot, bars_plot)


    def get_file(self, target_file_name):
        self.unpack()
        target_file_path = os.path.join(self.tmpdir.name, target_file_name)
        if os.path.exists(target_file_path):
            return target_file_path
        else:
            return None

    @classmethod
    def cleanup(self):
        self.tmpdir.cleanup()
