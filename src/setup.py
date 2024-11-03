from typing import TypedDict
import json
from sys import argv
import os

class FolderFilterOptions(TypedDict):
    class SubfoldersOptions(TypedDict):
        recursive: bool
        overrides: dict[str, 'FolderFilterOptions']

    folders: SubfoldersOptions
    files: bool

folder_filter: dict[str, FolderFilterOptions]
with open(argv[1]) as file: folder_filter = json.load(file)
file_list: dict[str, float] = {}

def handle_folder(path: str, options: FolderFilterOptions = {'folders': {'recursive': True}, 'files': True}) -> None:
    folder_items = os.listdir(path)
    if ('files' in options) and options['files']:
        for item_name in folder_items:
            item_path = os.path.join(path, item_name)
            if os.path.isfile(item_path): file_list[item_path] = os.path.getmtime(item_path)
    
    if not 'folders' in options: return
    if 'overrides' in options['folders']:
        for (subfolder_name, subfolder_options) in options['folders']['overrides'].items():
            folder_items.remove(subfolder_name)
            handle_folder(os.path.join(path, subfolder_name), subfolder_options)
    
    if (not 'recursive' in options['folders']) or (not options['folders']['recursive']): return
    for item_name in folder_items:
        item_path = os.path.join(path, item_name)
        if os.path.isdir(item_path): handle_folder(item_path)

for (path, options) in folder_filter.items(): handle_folder(path, options)
os.makedirs('dist', exist_ok=True)  
with open('dist/data.json', 'w') as file: json.dump(file_list, file)