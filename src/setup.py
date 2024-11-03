from typing import TypedDict
import json
import os
from sys import argv

class FolderFilterOptions(TypedDict):
    subfolders: bool | dict[str, 'FolderFilterOptions']
    files: bool

folder_filter: dict[str, FolderFilterOptions]

with open(argv[1]) as file:
    folder_filter = json.load(file)

file_list: dict[str, float] = {}

def handle_folder(path: str, options: FolderFilterOptions = {'subfolders': True, 'files': True}) -> None:
    folder_items = os.listdir(path)
    if options['files']:
        for item_name in folder_items:
            item_path = os.path.join(path, item_name)
            if os.path.isfile(item_path): file_list[item_path] = os.path.getmtime(item_path)
    
    if not options['subfolders']: return
    
    if options['subfolders'] == True:
        for item_name in folder_items:
            item_path = os.path.join(path, item_name)
            if os.path.isdir(item_path): handle_folder(item_path)
        
        return
    
    for (subfolder_name, subfolder_options) in options['subfolders'].items():
        handle_folder(os.path.join(path, subfolder_name), subfolder_options)

for (path, options) in folder_filter.items(): handle_folder(path, options)
os.makedirs('dist', exist_ok=True)  
with open('dist/data.json', 'w') as file: json.dump(file_list, file)