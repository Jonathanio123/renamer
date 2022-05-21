#!/usr/bin/python3
from datetime import datetime
from pathlib import Path
import os
import sys
import uuid
from tqdm import tqdm

if os.name == 'posix':
    if os.geteuid() == 0:
        print("Don't run this script as root.")
        sys.exit(1)


backupFolder = ".name_backups"
renamingFolder = "Example_folder"

if len(sys.argv) > 1:
    renamingFolder = str(sys.argv[1])


if not Path(renamingFolder).exists():
    print(f"Folder '{renamingFolder}' does not exist. Pass folder name as an argument.\nExample: ./renamer.py 'folder with files to be renamed'")
    sys.exit(2)

userInput = input(f"Rename all files in directory '{renamingFolder}'? [y/N]: ").lower()
if userInput != "y":
    print("Aborting")
    sys.exit(1)

if not Path(backupFolder).exists():
    os.mkdir(backupFolder)
    
backPath = f"{backupFolder}/{renamingFolder.strip(' / ')}-{datetime.now().strftime('%d.%m.%y_%H%M')}#1.txt"
if Path(backPath).exists():
    backPath = backPath[:-6] + f"#{int(backPath[-5]) +1}" + backPath[-4:]
Path(backPath).touch(exist_ok=True)


oldNames = list()
with os.scandir(renamingFolder) as dir:
    for entry in dir:
        if entry.is_file() and entry.name[0] != ".":
            oldNames.append(entry.name)


fileLen = len(oldNames)
if fileLen:
    print(f"Files to be renamed: {fileLen}")
else:
    print(f"No files found in the folder '{renamingFolder}'.")
    sys.exit(2)

allUnique = False
while not allUnique:
    newNames = list()
    for i in range(fileLen):
        newNames.append(str(uuid.uuid4()) + "." + oldNames[i].split(".")[-1])
    if fileLen != len(newNames):
        print(f"Not same amount of new names generated as there are old names. This should not happen!\n\
            Len files: {fileLen} != new filenames: {len(newNames)}")
        sys.exit(3)
    elif fileLen > len(set(newNames)):
        print("Duplicate in list! Generating new names.")
    else:
        allUnique = True



with open(backPath, "w") as fileBackup:
    for i in range(fileLen):
        fileBackup.write(oldNames[i] + "    " + newNames[i] + "\n")

for i in tqdm(range(fileLen), ncols=100):
    os.rename(f"{renamingFolder}/{oldNames[i]}", f"{renamingFolder}/{newNames[i]}")

print("Finished renaming files.")
sys.exit()