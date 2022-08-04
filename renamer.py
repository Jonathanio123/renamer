from datetime import datetime
from email import parser
from math import ceil
from multiprocessing import Pool
import multiprocessing
from pathlib import Path
import shutil
from helpers import inputYN
import os
import sys
import uuid
import argparse
try:
    from PIL import Image
    from tqdm import tqdm
    import ffmpeg
except:
    pass


def renamer(shard):
    for files in shard:
        os.rename(f"{renamingFolder}/{files[0]}", f"{renamingFolder}/{files[1]}")
    print(f'Process: {os.getpid()} | Finished.')


def webmConverter(args):
    """ inputFile, outputFile, ffmpegPath, filename, entry.name = args"""
    inputFile, outputFile, ffmpegPath, filename = args
    try:
        (
            ffmpeg
            .input(inputFile)
            .output(outputFile)
            .run(cmd=ffmpegPath,quiet=True)
        )
    except Exception as error:
        print(error)
        print(f"Error converting {filename}.webm to .mp4 format.")
        oldNames.append(entry.name)
    else:
        os.remove(inputFile)
        oldNames.append(filename+".mp4")




if __name__ == '__main__':

    backupFolder = ".name_backups"
    renamingFolder = "Example_folder"
    multiprocessingEnabled = False
    convertWebm = False
    convertWebp = False
    ffmpegInstalled = False
    ffmpegPath = "ffmpeg"



    # There should be no need to runs this as root.
    if os.name == 'posix':
        if os.geteuid() == 0:
            print("Don't run this script as root.")
            sys.exit(1)


    parser = argparse.ArgumentParser(description="Python script to rename all files (except: dotfiles and folders) inside a folder with random names.\
                                                    It will create a backup folder '.name_backups' where a file with old names and new names are saved")

    parser.add_argument('Path',
                       metavar='<path>',
                       type=str,
                       help='Path to folder with files you want renamed.')

    parser.add_argument('--backup',
                       metavar="<path>",
                       type=str,
                       help='Path to backup folder. Default path is .name_backups/')

    parser.add_argument("-m", "--multithreading", 
                        required=False,
                        action='store_true',
                        help="WARNING MIGHT BE BUGGY! Enable multiprocessing. Is a little bit faster but might contain bugs.")

    parser.add_argument("-cp", "--convertP", 
                        required=False,
                        action='store_true',
                        help="Will convert .webp to .jpeg without asking the user.")
    
    parser.add_argument("-cv", "--convertV", 
                        required=False,
                        action='store_true',
                        help="Will convert .webm to .mp4 without asking the user.")
    
    parser.add_argument("-s", "--script", 
                        required=False,
                        action='store_true',
                        help="Will skip all user input, useful when ran by other scripts. Can be combined with -c")

    args = parser.parse_args()
    

    # User has to provide the folder with files to rename
    if args.Path:
        renamingFolder = args.Path.strip("\\")

    if args.backup:
        backupFolder = args.backup.strip("\\")


    if not Path(renamingFolder).is_dir():
        print(f"Folder '{renamingFolder}' does not exist. Pass folder name as an argument.\nExample: ./renamer.py <folder name>")
        sys.exit(2)


    if args.multithreading:
        multiprocessingEnabled = True
    


    if not args.script:
        inputYN(f"Rename all files in directory '{renamingFolder}'?", True, False)
    

    if not "PIL" in sys.modules:
        print("PIL library not installed, unable to convert .webp to .jpeg.")
        convertWebp = False
    elif args.convertP:
        print("Converting all .webp to .jpeg before renaming.")
        convertWebp = True
    elif not args.script:
        convertWebp = inputYN("Convert all .webp to .jpeg before renaming?")

    

    if shutil.which("ffmpeg"):
        ffmpegInstalled = True
    elif Path("ffmpeg/bin/ffmpeg.exe").exists():
            ffmpegPath = "ffmpeg/bin/ffmpeg.exe"
            ffmpegInstalled = True

    if not "ffmpeg" in sys.modules or not ffmpegInstalled:
        print("ffmpeg library not installed, unable to convert .webm to .mp4.")
        convertWebm = False
    elif args.convertV:
        print("Converting all .webm to .mp4 before renaming.")
        convertWebm = True
    elif not args.script:
        convertWebm = inputYN("Convert all .webm to .mp4 before renaming?")
    



    # Creates a a backup folder where it will create file with old filenames and new ones
    if not Path(backupFolder).exists():
        os.mkdir(backupFolder)
        
    backPath = f"{backupFolder}/{renamingFolder.strip(' / ')}-{datetime.now().strftime('%d.%m.%y_%H%M')}#1.txt"
    if Path(backPath).exists():
        backPath = backPath[:-6] + f"#{int(backPath[-5]) +1}" + backPath[-4:]
    Path(backPath).touch(exist_ok=True)


    oldNames = list()
    if multiprocessingEnabled:
        multiprocessing.set_start_method('spawn')

    with os.scandir(renamingFolder) as dir:
        for entry in dir:
            filename, ext = os.path.splitext(entry.name)
            if entry.is_file() and entry.name[0] != ".":

                if ext == ".webp" and convertWebp:
                    inputFile = f"{renamingFolder}/{filename}.webp"
                    outputFile = f"{renamingFolder}/{filename}.jpeg"

                    try:
                        img = Image.open(inputFile).convert("RGB")
                        img.save(outputFile, "jpeg")
                    except Exception as error:
                        print(error)
                        try:
                            os.remove(outputFile)
                        except:
                            pass
                        oldNames.append(entry.name)

                    else:
                        os.remove(inputFile)
                        oldNames.append(filename+".jpeg")
                
                if ext == ".webm" and convertWebm:
                    inputFile = f"{renamingFolder}/{filename}.webm"
                    outputFile = f"{renamingFolder}/{filename}.mp4"

                    if multiprocessingEnabled:
                        print("Multithreading not supported for webm converstion.")
                        webmConverter([inputFile, outputFile, ffmpegPath, filename])
                        continue
                    else:
                        webmConverter([inputFile, outputFile, ffmpegPath, filename])

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

    if not multiprocessingEnabled:
        # For loop that renames files
        if "tqdm" in sys.modules:
            for i in tqdm(range(fileLen), ncols=100):
                os.rename(f"{renamingFolder}/{oldNames[i]}", f"{renamingFolder}/{newNames[i]}")
            print("Finished renaming files.")
            
        else:
            print("Tqdm library not installed, not showing progress bar.")
            print("Renaming files...")
            timeBefore = datetime.now()
            for i in range(fileLen):
                os.rename(f"{renamingFolder}/{oldNames[i]}", f"{renamingFolder}/{newNames[i]}")
            print(f"{fileLen} files renamed in {(datetime.now() - timeBefore).total_seconds()} seconds.")
    else:
        filesPerWorkerList = list()
        filesPerWorkerList.append([])
        filesPerWorker = ceil(fileLen / os.cpu_count())
        i = 0
        j = 0
        for line in range(fileLen):
            i = i + 1
            filesPerWorkerList[j].append([oldNames[line],newNames[line]])
            if i == filesPerWorker:
                i = 0
                j = j + 1 
                filesPerWorkerList.append([])

        print("Renaming files...")
        timeBefore = datetime.now()
        with Pool() as pool:
            r = pool.map(renamer, filesPerWorkerList)
        
        print(f"{fileLen} files renamed in {(datetime.now() - timeBefore).total_seconds()} seconds.")
            


    sys.exit()