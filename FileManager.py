import os
import shutil
import tempfile
import zipfile
from JsonComponent import JsonComponent

import saver


class FileManager:
    DEFAULT_PROJECT_EXTENSION = ".proj"

    tmpdir = tempfile.TemporaryDirectory()
    
    @staticmethod
    def get_file(path):
        return open(path, 'r')
    
    @staticmethod
    def write_file(path, content):
        with open(path, 'w+') as file:
            file.write(content)

    @staticmethod
    def delete_file(path):
        os.remove(path)

    @staticmethod
    def pack(project, file_path, file_name, relocate_files):
        file_name = file_name + FileManager.DEFAULT_PROJECT_EXTENSION

        exists = False
        if os.path.exists(file_path):
            exists = True
        
        archive_name = os.path.join(file_path, file_name)
        tmp_dir = tempfile.mkdtemp()
        tmp_archive_dir = os.path.join(tmp_dir, 'temp_archive')
        
        if os.path.exists(tmp_archive_dir):
            shutil.rmtree(tmp_archive_dir)
        os.makedirs(tmp_archive_dir, exist_ok=True)

        if relocate_files:
            if not exists:
                for curve in project.curves:
                    shutil.copy(curve.file_path, os.path.join(tmp_archive_dir, os.path.basename(curve.file_path)))
            for bars in project.spikes:
                bars_path = os.path.join(tmp_archive_dir, os.path.basename(bars.file_path).split('.')[0] + '.asg')
                bars.file_path = bars.file_path.split('.')[0] + '.asg'
                saver.write_ASG(bars_path, bars.spikes_data)
                #shutil.copy(bars.file_path, os.path.join(tmp_archive_dir, os.path.basename(bars.file_path)))
            if not exists:
                project.relocate(file_path)
        
        # Save project JSON
        js = project.to_json_component()
        js.save(os.path.join(tmp_archive_dir, project.name + '.json'))

        # Create zip archive
        shutil.make_archive(tmp_archive_dir, 'zip', tmp_archive_dir)
        shutil.move(tmp_archive_dir + '.zip', archive_name)

        shutil.rmtree(tmp_dir)

    @staticmethod
    def unpack(file_path):
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        return temp_dir

    @staticmethod
    def read(file_path, target_file_name):
        unpacked_dir = FileManager.unpack(file_path)
        target_file_path = os.path.join(unpacked_dir, target_file_name)
        data = None
        if os.path.exists(target_file_path):
            with open(target_file_path, 'r') as f:
                data = f.read()
        shutil.rmtree(unpacked_dir)
        return data

    @staticmethod
    def write(file_path, target_file_name, data):
        unpacked_dir = FileManager.unpack(file_path)
        target_file_path = os.path.join(unpacked_dir, target_file_name)
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
        with open(target_file_path, 'w') as f:
            f.write(data)
        
        # Create zip archive
        tmp_archive = os.path.join(tempfile.mkdtemp(), 'temp_archive')
        shutil.make_archive(tmp_archive, 'zip', unpacked_dir)
        shutil.move(tmp_archive + '.zip', file_path)

        shutil.rmtree(unpacked_dir)

    @staticmethod
    def cleanup():
        pass  # Temporary directories are cleaned up individually now

    @staticmethod
    def refresh():
        pass  # Temporary directories are cleaned up individually now