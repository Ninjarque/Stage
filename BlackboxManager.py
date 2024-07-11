import subprocess
import os

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

    def run(full_mode=True):
        try:
            with cd("/media/ninjarque/3e2d74d8-db3c-43ea-87b9-9d1dda0a6c0d/charles-adele/Documents/Exemple_1"):
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
        except Exception as e:
            print("Couldn't run the commands, try verifying that the required files are in the correct path and that you are using Mac or Linux!")
            print("Error:", e)
        pass