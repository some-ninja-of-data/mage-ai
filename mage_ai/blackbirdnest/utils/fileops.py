

import os
import glob
import shutil



DOWNLOAD_PATH = 'C:\\Users\\A228783DIRPblackbird\\Downloads'
COPY_TO_PATH = 'C:\\Mozenda\\High radius'



def get_downloaded_file(file_name_to_find=None, **kwargs):
    downloads_folder = kwargs.get('downloads_folder',DOWNLOAD_PATH)
    list_of_files = glob.glob(f'{downloads_folder}\\{file_name_to_find}*.xlsx') # * means all if need specific format then *.xlsx
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def copy_file_to_folder(path_to_copy=None, destination_path=None, destination_name=None):
    os.makedirs(destination_path, exist_ok=True)
    full_destination = os.path.join(destination_path,destination_name)
    shutil.copyfile(path_to_copy, full_destination)
    return full_destination