import subprocess
import os
import shutil
from tkinter import filedialog

from Project import Project
from ProjectManager import ProjectManager

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


class BlackboxManager:
    def __init__():
        pass

    def run(full_mode=False):
        try:
            path = ProjectManager.blackbox_path
            with cd(path):
                print("######## job_xfit_nu3 ########")
                subprocess.call(["./job_xfit_nu3"])
                if full_mode == True:
                    print("######## job_cal_nu3_full ########")
                    subprocess.call(["./job_cal_nu3_full"])
                else:
                    print("######## job_cal_nu3  ########")
                    subprocess.call(["./job_cal_nu3"])
                print("######## job_sim_nu3 ########")
                subprocess.call(["./job_sim_nu3"])
                print("Ran every black box command!")

                to_copy_file = ProjectManager.current_project_path
                if to_copy_file != "":
                    to_copy_file, _ = os.path.split(to_copy_file)
                if to_copy_file == "":
                    to_copy_file = filedialog.asksaveasfilename(initialdir=ProjectManager.blackbox_path, title="Select the blackbox output project name")
                if not to_copy_file == "":
                    _, name = os.path.split(to_copy_file)
                    to_copy_path = os.path.dirname(to_copy_file).replace("\\", "/")
                    
                    simul_path = os.path.join(to_copy_path, "simul.xy")
                    spectr_path = os.path.join(to_copy_path, "spectr.t")
                    shutil.copy(os.path.join(path, "simul.xy"), simul_path)
                    shutil.copy(os.path.join(path, "spectr.t"), spectr_path)
                    proj = Project.make_project(simul_path, spectr_path)
                    proj.name = name.split(".")[0]
                    proj.save(to_copy_path, True)
                else:
                    print("Skipping movement of files and project making...")
        except Exception as e:
            print("Couldn't run the commands, try verifying that the required files are in the correct path and that you are using Mac or Linux!")
            print("Error:", e)
        pass