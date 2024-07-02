import tkinter as tk
from tkinter import filedialog
import os.path
import datetime
import shutil

from JsonComponent import *
from Project import *


CONFIG_EXTENSION = ".json"

DEFAULT_AUTOSAVE_PROJECT_PATH = "./"
DEFAULT_CONFIG_AUTO_SAVE_NAME = "autosaved_project"

APPLICATION_CONFIG_PATH = "config.json"

BACKUP_KEY = "backups"
BACKUP_DIR = "BACKUPS"

class ProjectManager:
    current_project = None
    current_project_path = ""
    config = None

    do_auto_save = True

    @staticmethod
    def init_project():
        ProjectManager.current_project = Project()
        ProjectManager.current_project_path = ""

    @staticmethod
    def save_project_dialog():
        #root = tk.Tk()
        #root.withdraw()
        file_path = filedialog.asksaveasfilename()
        if file_path:
            ProjectManager.save_project(file_path)

    @staticmethod
    def load_project_dialog(curve_plot, bars_plot):
        #root = tk.Tk()
        #root.withdraw()
        file_path = filedialog.askopenfilename()
        if file_path:
            ProjectManager.load_project(file_path, curve_plot, bars_plot)

    @staticmethod
    def save_project(path):
        if not ProjectManager.current_project:
            print("No project to save")
            return
        ProjectManager.current_project.name = path.split("/")[-1].split('.')[0]
        file_path = os.path.dirname(path).replace("\\", "/")
        ProjectManager.current_project_path = ProjectManager.current_project.save(file_path, pack_files=True)
        #ProjectManager.make_backup()
        ProjectManager.save_config()

    @staticmethod
    def load_project(path, curve_plot, bars_plot):
        ProjectManager.current_project = Project.load(path, curve_plot, bars_plot)
        ProjectManager.current_project_path = path
        ProjectManager.save_config()

    @staticmethod
    def make_backup():
        if not ProjectManager.current_project:
            return
        project = ProjectManager.current_project
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = project.name.replace(" ", "_") if project.name else "Unnamed_Project"
        backup_dir = os.path.join(BACKUP_DIR, f"{project_name}_{timestamp}")
        os.makedirs(backup_dir, exist_ok=True)

        project.relocate(backup_dir)
        backup_file_path = os.path.join(backup_dir, f"{project_name}{CONFIG_EXTENSION}")
        project.save(backup_file_path, pack_files=True)

        config = ProjectManager._load_or_create_config()
        backup_entry = {"timestamp": timestamp, "backup_path": backup_file_path}
        config.properties.setdefault(BACKUP_KEY, []).append(backup_entry)
        config.save(APPLICATION_CONFIG_PATH)
        print(f"Created backup for project '{project.name}' at '{backup_file_path}'")


    @staticmethod
    def _copy_files_and_update_paths(data, backup_dir):
        for key, value in data.items():
            if isinstance(value, dict):
                ProjectManager._copy_files_and_update_paths(value, backup_dir)
            elif isinstance(value, str) and 'path' in key:
                new_path = os.path.join(backup_dir, os.path.basename(value))
                print("Copying file", value, "to new path", new_path)
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
    def load_config(curve_plot, bars_plot):
        if os.path.isfile(APPLICATION_CONFIG_PATH):
            ProjectManager.config = JsonComponent.load(APPLICATION_CONFIG_PATH)
            ProjectManager.current_project_path = ProjectManager.config.properties.get("last_project_path", "")
            if ProjectManager.current_project_path:
                ProjectManager.load_project(ProjectManager.current_project_path, curve_plot, bars_plot)
                return True
        return False

    @staticmethod
    def auto_save():
        if not ProjectManager.do_auto_save:
            print("Auto save disabled...")
            return
        ProjectManager.save_project(DEFAULT_AUTOSAVE_PROJECT_PATH)

    @staticmethod
    def auto_load(curve_plot, bars_plot):
        if not ProjectManager.load_config(curve_plot, bars_plot):
            if os.path.isfile(DEFAULT_AUTOSAVE_PROJECT_PATH):
                ProjectManager.load_project(DEFAULT_AUTOSAVE_PROJECT_PATH, curve_plot, bars_plot)
                #print("Sucessfully auto loaded project!")

    def enable_auto_save():
        ProjectManager.do_auto_save = True
    def disable_auto_save():
        ProjectManager.do_auto_save = False

    
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
        ProjectManager.auto_save()

    def set_curve_x_offset(curve_name, x_offset):
        if not ProjectManager.current_project:
            ProjectManager.init_project()
        project = ProjectManager.current_project
        project.curve_x_offset[curve_name] = x_offset
        ProjectManager.auto_save()
    
    def set_curve_ranges(curve_name, ranges):
        if not ProjectManager.current_project:
            ProjectManager.init_project()
        project = ProjectManager.current_project
        print("set curve ranges to", ranges)
        project.curve_ranges[curve_name] = ranges
        ProjectManager.auto_save()

    def set_curve_themes(curve_name, theme):
        if not ProjectManager.current_project:
            ProjectManager.init_project()
        project = ProjectManager.current_project
        project.curve_themes[curve_name] = theme
        ProjectManager.auto_save()

    @staticmethod
    def get_curve_ranges(curve_name):
        if not ProjectManager.current_project:
            ProjectManager.init_project()

        project = ProjectManager.current_project
        paths = []
        for p in project.curve_ranges[curve_name]:
            paths.append(p)
        print("get curve ranges:", project.curve_ranges)
        return project.curve_ranges[curve_name]

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
    def get_curve_xoffset(curve_name):
        if not ProjectManager.current_project:
            ProjectManager.init_project()

        project = ProjectManager.current_project
        return float(project.curve_x_offset[curve_name])
    
    @staticmethod
    def append_spikes(spikes_name, spikes_path, theme):
        if not ProjectManager.current_project:
            ProjectManager.init_project()
        
        project = ProjectManager.current_project
        project.spikes_paths[spikes_name] = spikes_path
        project.spikes_themes[spikes_name] = theme
        ProjectManager.auto_save()

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
