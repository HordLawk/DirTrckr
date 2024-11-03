from typing import TypedDict
import json
from sys import argv
import os
from time import time

class FolderFilterOptions(TypedDict):
    class SubfoldersOptions(TypedDict):
        recursive: bool
        overrides: dict[str, 'FolderFilterOptions']

    folders: SubfoldersOptions
    files: bool

current_time = time()
if not os.path.isfile('dist/checkpoints.json'):
    os.makedirs('dist', exist_ok=True)
    with open('dist/checkpoints.json', 'w', encoding="utf-8") as file: json.dump([current_time], file)
    print('Created first checkpoint! Run this script again to check for differences.')
    exit()

checkpoints: list[float]
try:
    with open('dist/checkpoints.json', encoding="utf-8") as file: checkpoints = json.load(file)

except json.JSONDecodeError:
    print('Could not parse previous checkpoints. Fix or delete the dist/checkpoints.json file and rerun the script.')
    exit()

try:
    checkpoint_time = checkpoints[int(argv[2]) if (len(argv) > 2) else -1]

except (ValueError, IndexError):
    print('The second argument must be either empty or a valid checkpoint Id')
    exit()

folder_filter: dict[str, FolderFilterOptions]
try:
    with open(argv[1], encoding="utf-8") as file: folder_filter = json.load(file)

except (IndexError, FileNotFoundError, json.JSONDecodeError):
    print('The first argument must be a path to an existing file containing valid JSON content')
    exit()

def handle_folder(path: str, options: FolderFilterOptions = {'folders': {'recursive': True}, 'files': True}) -> None:
    folder_items = os.listdir(path)
    if ('files' in options) and options['files']:
        for item_name in folder_items:
            item_path = os.path.join(path, item_name)
            if os.path.getctime(item_path) > checkpoint_time: print(f'[NEW] {item_path}')
            elif os.path.getmtime(item_path) > checkpoint_time: print(f'[MOD] {item_path}')
    
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
if input(f'Create new checkpoint with Id `{len(checkpoints)}` (Y/N)? ') in ('Y', 'y'):
    with open('dist/checkpoints.json', 'w', encoding="utf-8") as file: json.dump([*checkpoints, current_time], file)