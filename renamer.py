from datetime import datetime
from pathlib import Path
from helpers import inputYN
import os
import sys
import uuid
try:
    from PIL import Image
    from tqdm import tqdm
except:
    pass

# There should be no need to runs this as root.
if os.name == 'posix':
    if os.geteuid() == 0:
        print("Don't run this script as root.")
        sys.exit(1)


backupFolder = ".name_backups"
renamingFolder = "Example_folder"


# User has to provide the folder with files to rename
if len(sys.argv) > 1:
    renamingFolder = str(sys.argv[1])


if not Path(renamingFolder).exists():
    print(f"Folder '{renamingFolder}' does not exist. Pass folder name as an argument.\nExample: ./renamer.py 'folder with files to be renamed'")
    sys.exit(2)


inputYN(f"Rename all files in directory '{renamingFolder}'?", True, False)
if "PIL" in sys.modules:
    convertWebp = inputYN("Convert all .webp to .jpeg before renaming?")
else:
    print("PIL library not installed, unable to convert .webp to .jpeg.")
    convertWebp = False


# Creates a a backup folder where it will create file with old filenames and new ones
if not Path(backupFolder).exists():
    os.mkdir(backupFolder)
    
backPath = f"{backupFolder}/{renamingFolder.strip(' / ')}-{datetime.now().strftime('%d.%m.%y_%H%M')}#1.txt"
if Path(backPath).exists():
    backPath = backPath[:-6] + f"#{int(backPath[-5]) +1}" + backPath[-4:]
Path(backPath).touch(exist_ok=True)


oldNames = list()
with os.scandir(renamingFolder) as dir:
    for entry in dir:
        filename, ext = os.path.splitext(entry.name)
        if entry.is_file() and entry.name[0] != ".":
            if ext == ".webp" and convertWebp:
                try:
                    img = Image.open(renamingFolder+"/"+entry.name).convert("RGB")
                    img.save(renamingFolder+"/"+filename+".jpeg", "jpeg")
                except Exception as error:
                    print(error)
                    try:
                        os.remove(renamingFolder+"/"+filename+".jpeg")
                    except:
                        pass
                else:
                    os.remove(renamingFolder+"/"+entry.name)
                    oldNames.append(filename+".jpeg")
            else:
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


# Writes the backup file with old and new filenames
with open(backPath, "w") as fileBackup:
    for i in range(fileLen):
        fileBackup.write(oldNames[i] + "    " + newNames[i] + "\n")

# For loop that renames files
if "tqdm" in sys.modules:
    for i in tqdm(range(fileLen), ncols=100):
        os.rename(f"{renamingFolder}/{oldNames[i]}", f"{renamingFolder}/{newNames[i]}")
else:
    print("Tqdm library not installed, not showing progress bar.")
    for i in range(fileLen):
        os.rename(f"{renamingFolder}/{oldNames[i]}", f"{renamingFolder}/{newNames[i]}")

print("Finished renaming files.")
sys.exit()