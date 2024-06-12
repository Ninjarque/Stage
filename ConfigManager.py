import tkinter as tk
from tkinter import filedialog
import os.path
import datetime
import shutil

from JsonComponent import *
from Project import *


DEFAULT_CONFIG_PATH = "config.json"

DEFAULT_CONFIG_AUTO_SAVE_NAME = "last_project"

BACKUP_KEY = "backups"
BACKUP_DIR = "backups"

class ConfigManager:    
    @staticmethod
    def save_config(config):
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        file_path = filedialog.asksaveasfilename()
        if file_path:
            config.save(file_path)
    
    @staticmethod
    def load_config():
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        file_path = filedialog.askopenfilename()
        if file_path:
            return JsonComponent.load(file_path)
        return None
    
    @staticmethod
    def save_project(project):
        if not project:
            print("No project to save")
            return
        last_project = project.to_json_component()
        ConfigManager.save_config(last_project)
        ConfigManager.try_auto_save(project)
        ConfigManager.make_backup(project)
    
    @staticmethod
    def load_project():
        loaded = ConfigManager.load_config()
        if not loaded:
            print("No config loaded")
            return None
        project = Project.from_json_component(loaded)
        ConfigManager.try_auto_save(project)
        return project
    
    @staticmethod
    def make_backup(project):
        if not project:
            return False
        
        config = JsonComponent.load(DEFAULT_CONFIG_PATH) if os.path.isfile(DEFAULT_CONFIG_PATH) else JsonComponent("config")
        if BACKUP_KEY not in config.properties:
            config.properties[BACKUP_KEY] = []
        
        backup = project.to_json_component().to_dict()
        timestamp = datetime.datetime.now().isoformat()
        backup_dir = os.path.join(BACKUP_DIR, timestamp)
        os.makedirs(backup_dir, exist_ok=True)
        
        def copy_files_and_update_paths(data):
            for key, value in data.items():
                if isinstance(value, dict):
                    copy_files_and_update_paths(value)
                elif isinstance(value, str) and 'path' in key:
                    new_path = os.path.join(backup_dir, os.path.basename(value))
                    shutil.copy(value, new_path)
                    data[key] = new_path

        copy_files_and_update_paths(backup)

        backup_entry = {
            "timestamp": timestamp,
            "project": backup
        }
        config.properties[BACKUP_KEY].append(backup_entry)
        
        config.save(DEFAULT_CONFIG_PATH)
        print(f"Created backup at '{timestamp}'")
        return True

    @staticmethod
    def try_auto_save(project):
        if not project:
            return False
        
        config = JsonComponent("config")
        last_project = project.to_json_component()
        config.properties[DEFAULT_CONFIG_AUTO_SAVE_NAME] = last_project.to_dict()
        
        config.save(DEFAULT_CONFIG_PATH)
        print(f"Autosaved file to path '{DEFAULT_CONFIG_PATH}'!")
        return True
        
    @staticmethod
    def try_auto_load():
        if os.path.isfile(DEFAULT_CONFIG_PATH):
            config = JsonComponent.load(DEFAULT_CONFIG_PATH)
            if config:
                backups = config.properties.get(BACKUP_KEY, [])
                if backups:
                    latest_backup = max(backups, key=lambda x: x["timestamp"])
                    last_project = JsonComponent.from_dict(latest_backup["project"])
                    return True, Project.from_json_component(last_project)
                else:
                    print("No backup found in current file, proceeding with simpler loading...")
                    last_project_data = config.properties.get(DEFAULT_CONFIG_AUTO_SAVE_NAME)
                    if last_project_data:
                        last_project = JsonComponent.from_dict(last_project_data)
                        return True, Project.from_json_component(last_project)
            print(f"Couldn't open last auto save file property '{DEFAULT_CONFIG_AUTO_SAVE_NAME}' properly!")

        print(f"No auto save found for file '{DEFAULT_CONFIG_PATH}'...")
        return False, None