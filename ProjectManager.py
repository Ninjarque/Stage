import tkinter as tk
from tkinter import filedialog
import os.path
import datetime
import shutil

from JsonComponent import *
from Project import *


CONFIG_EXTENSION = ".json"

DEFAULT_AUTOSAVE_PROJECT_PATH = "auto_saved_project.json"
DEFAULT_CONFIG_AUTO_SAVE_NAME = "autosaved_project"

APPLICATION_CONFIG_PATH = "config.json"

BACKUP_KEY = "backups"
BACKUP_DIR = "BACKUPS"

class ProjectManager:
    current_project = None
    current_project_path = ""
    config = None

    @staticmethod
    def init_project():
        ProjectManager.current_project = Project()
        ProjectManager.current_project_path = ""

    @staticmethod
    def save_project_dialog():
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename()
        if file_path:
            ProjectManager.save_project(file_path)

    @staticmethod
    def load_project_dialog():
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename()
        if file_path:
            ProjectManager.load_project(file_path)

    @staticmethod
    def save_project(path):
        if not ProjectManager.current_project:
            print("No project to save")
            return
        ProjectManager.current_project_path = path
        json_component = ProjectManager.current_project.to_json_component()
        json_component.save(path)
        ProjectManager.make_backup()

    @staticmethod
    def load_project(path):
        ProjectManager.current_project_path = path
        json_component = JsonComponent.load(path)
        ProjectManager.current_project = Project.from_json_component(json_component)

    @staticmethod
    def make_backup():
        if not ProjectManager.current_project:
            return
        project = ProjectManager.current_project
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = project.name.replace(" ", "_") if project.name else "Unnamed_Project"
        backup_dir = os.path.join(BACKUP_DIR, f"{project_name}_{timestamp}")
        os.makedirs(backup_dir, exist_ok=True)

        backup = project.to_json_component().to_dict()
        ProjectManager._copy_files_and_update_paths(backup, backup_dir)
        
        config = ProjectManager._load_or_create_config()
        backup_entry = {"timestamp": timestamp, "backup": backup}
        config.properties.setdefault(BACKUP_KEY, []).append(backup_entry)
        config.save(ProjectManager.current_project_path)
        print(f"Created backup for project '{project.name}' at '{timestamp}'")

    @staticmethod
    def _copy_files_and_update_paths(data, backup_dir):
        for key, value in data.items():
            if isinstance(value, dict):
                ProjectManager._copy_files_and_update_paths(value, backup_dir)
            elif isinstance(value, str) and 'path' in key:
                new_path = os.path.join(backup_dir, os.path.basename(value))
                shutil.copy(value, new_path)
                data[key] = new_path

    @staticmethod
    def _load_or_create_config():
        if os.path.isfile(ProjectManager.current_project_path):
            return JsonComponent.load(ProjectManager.current_project_path)
        else:
            return JsonComponent("project")

    @staticmethod
    def save_config():
        if not ProjectManager.config:
            ProjectManager.config = JsonComponent("config")
        ProjectManager.config.properties["last_project_path"] = ProjectManager.current_project_path
        ProjectManager.config.save(APPLICATION_CONFIG_PATH)

    @staticmethod
    def load_config():
        if os.path.isfile(APPLICATION_CONFIG_PATH):
            ProjectManager.config = JsonComponent.load(APPLICATION_CONFIG_PATH)
            ProjectManager.current_project_path = ProjectManager.config.properties.get("last_project_path", "")
            if ProjectManager.current_project_path:
                ProjectManager.load_project(ProjectManager.current_project_path)

    @staticmethod
    def auto_save():
        ProjectManager.save_project(DEFAULT_AUTOSAVE_PROJECT_PATH)
        ProjectManager.save_config()

    @staticmethod
    def auto_load():
        ProjectManager.load_config()
        if os.path.isfile(DEFAULT_AUTOSAVE_PROJECT_PATH):
            ProjectManager.load_project(DEFAULT_AUTOSAVE_PROJECT_PATH)
            print("Sucessfully auto loaded project!")

    
    '''
    UTILITY FUNCTIONS TO BETTER ACCESS THE CURRENT INSTANCE OF PROJECT:
    '''

    
    @staticmethod
    def append_curve(curve_name, curve_path, theme):
        if not ProjectManager.current_project:
            ProjectManager.init_project()
        
        project = ProjectManager.current_project
        project.curve_paths[curve_name] = curve_path
        project.curve_themes[curve_name] = theme

    @staticmethod
    def get_curve_paths():
        if not ProjectManager.current_project:
            ProjectManager.init_project()

        project = ProjectManager.current_project
        paths = []
        for k, p  in project.curve_paths.items():
            paths.append(p)
        return paths
    @staticmethod
    def get_curve_themes():
        if not ProjectManager.current_project:
            ProjectManager.init_project()

        project = ProjectManager.current_project
        paths = []
        for k, p in project.curve_themes.items():
            paths.append(p)
        return paths
    
    @staticmethod
    def append_spikes(spikes_name, spikes_path, theme):
        if not ProjectManager.current_project:
            ProjectManager.init_project()
        
        project = ProjectManager.current_project
        project.spikes_paths[spikes_name] = spikes_path
        project.spikes_themes[spikes_name] = theme

    @staticmethod
    def get_spikes_paths():
        if not ProjectManager.current_project:
            ProjectManager.init_project()

        project = ProjectManager.current_project
        paths = []
        for k, p in project.spikes_paths.items():
            paths.append(p)
        return paths
    @staticmethod
    def get_spikes_themes():
        if not ProjectManager.current_project:
            ProjectManager.init_project()

        project = ProjectManager.current_project
        paths = []
        for k, p in project.spikes_themes.items():
            paths.append(p)
        return paths