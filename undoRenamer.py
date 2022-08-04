from genericpath import exists
from pathlib import Path
from datetime import datetime
from posixpath import split
import sys
import os
try:
    from PIL import Image
    from tqdm import tqdm
except:
    pass


backupFolder = ".name_backups"
renamingFolder = "Example_folder"

# Simple y/n input function
def inputYN(prompt, abort=False, defaultYes=True):
    if defaultYes:
        default = "[Y/n]:"
    else:
        default = "[y/N]:"

    userInput = input(f"{prompt} {default} ").lower()

    if userInput == "n" or (not defaultYes and userInput == ""):
        if abort:
            print("Aborting")
            sys.exit(1)
        return False

    if userInput == "y" or (defaultYes and userInput == ""):
        return True

if not Path(backupFolder).exists():
    print(f"{backupFolder} folder not found!\nAborting")
    sys.exit(1)

newestBackup = None

with os.scandir(backupFolder) as dir:
    for entry in dir:
        if renamingFolder not in entry.name or entry.name[0] == ".":
            continue
        elif newestBackup is None:
            newestBackup = entry.name
            continue

        newestDate = datetime.strptime(str(newestBackup).split("-")[1].split("#")[0],'%d.%m.%y_%H%M')
        currentDate = datetime.strptime(str(entry.name).split("-")[1].split("#")[0],'%d.%m.%y_%H%M')

        if currentDate > newestDate:
            newestBackup = entry.name

        elif currentDate == newestDate:
            if int(str(entry.name).split("#")[1].split(".")[0]) > int(newestBackup.split("#")[1].split(".")[0]):
                newestBackup = entry.name
    
if newestBackup is None:
    print(f"No backup files found for {renamingFolder} directory.\nAborting")
    sys.exit(1)

backupFile = list()
with open(f"{backupFolder}/{newestBackup}", "r") as file:
    for line in file:
        strippedLine = line.strip().split("    ")
        backupFile.append([strippedLine[0], strippedLine[1]])


missingFiles = list()
i = 0
first = True
for filename in backupFile:
    if not Path(f"{renamingFolder}/{filename[1]}").exists():
            basename = filename[1].split('.')[0]
            if Path(f"{renamingFolder}/{basename}.jpeg").exists():
                if first:
                    inputYN("Too keep filenames and extenstions consistant all former .webp will be converted back to .jpeg.\nNo changes have been made. Do you want to continue?", True, False)
                    first = False
                print(f"{basename}.jpeg was converted from webp. Converting back to .webp")
                try:
                    img = Image.open(renamingFolder+"/"+basename+".jpeg").convert("RGB")
                    img.save(renamingFolder+"/"+basename+".webp", "webp")
                except Exception as error:
                    print(error)
                    try:
                        os.remove(renamingFolder+"/"+basename+".webp")
                    except:
                        pass
                    print("Error converting jpeg back to webp. No changes have been made.\nAborting")
                    sys.exit(2)
                else:
                    os.remove(renamingFolder+"/"+basename+".jpeg")
            else:
                missingFiles.append(filename[1])
    i = i + 1

if len(missingFiles) > 0:
    print("Files not found: ")
    for filename in missingFiles:
        print(filename)
    inputYN(f"{len(missingFiles)} files not found! Do you still want to continue?", True, False)
else:
    inputYN(f"{len(backupFile)} files to be renamed. Do you want to continue?", True, False)



if "tqdm" in sys.modules:
    for i in tqdm(range(len(backupFile)), ncols=100):
        os.rename(renamingFolder+"/"+backupFile[i][1], renamingFolder+"/"+backupFile[i][0])
else:
    for filenames in backupFile:
        os.rename(renamingFolder+"/"+filenames[1], renamingFolder+"/"+filenames[0])

print(f"Hiding old backup file '.{newestBackup}'")
os.rename(f"{backupFolder}/{newestBackup}",f"{backupFolder}/.{newestBackup}")

