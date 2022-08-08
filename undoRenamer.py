from pathlib import Path
from datetime import datetime
import shutil
from helpers import inputYN
import sys
import os
try:
    from PIL import Image
    from tqdm import tqdm
    import ffmpeg
except:
    pass


backupFolder = ".name_backups"
renamingFolder = "Example_folder"
ffmpegPath = "ffmpeg"
if shutil.which("ffmpeg"):
        ffmpegInstalled = True
elif Path("ffmpeg/bin/ffmpeg.exe").exists():
        ffmpegPath = "ffmpeg/bin/ffmpeg.exe"


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

        newestDate = datetime.strptime(str(newestBackup).split("#&#")[1].split("#")[0],'%d.%m.%y_%H%M')
        currentDate = datetime.strptime(str(entry.name).split("#&#")[1].split("#")[0],'%d.%m.%y_%H%M')

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
                    inputYN("Too keep filenames and extenstions consistant all former .webp and .mp4 will be converted back to .jpeg and .webm.\nNo changes have been made. Do you want to continue?", True, False)
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
                    print(f"Error converting {filename}.jpeg to .webp format.")
                    print("No changes have been made.\nAborting")
                    sys.exit(2)
                else:
                    os.remove(renamingFolder+"/"+basename+".jpeg")
            
            if Path(f"{renamingFolder}/{basename}.mp4").exists():
                if first:
                    inputYN("Too keep filenames and extenstions consistant all former .webp and .mp4 will be converted back to .jpeg and .webm.\nNo changes have been made. Do you want to continue?", True, False)
                    first = False
                print(f"{basename}.mp4 was converted from webm. Converting back to .webm")
                try:
                    (
                        ffmpeg
                        .input(f"{renamingFolder}/{basename}.mp4")
                        .output(f"{renamingFolder}/{basename}.webm")
                        .run(cmd=ffmpegPath,quiet=True)
                    )
                except Exception as error:
                    print(error)
                    print(f"Error converting {filename}.mp4 to .webm format.")
                    print("No changes have been made.\nAborting")
                    sys.exit(2)
                else:
                    os.remove(renamingFolder+"/"+basename+".mp4")


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
        try:
            os.rename(renamingFolder+"/"+backupFile[i][1], renamingFolder+"/"+backupFile[i][0])
        except Exception as e:
            print(e)
else:
    for filenames in backupFile:
        try:
            os.rename(renamingFolder+"/"+filenames[1], renamingFolder+"/"+filenames[0])
        except Exception as e:
            print(e)
print(f"Hiding old backup file '.{newestBackup}'")
os.rename(f"{backupFolder}/{newestBackup}",f"{backupFolder}/.{newestBackup}")

