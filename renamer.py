from datetime import datetime
from email import parser
from math import ceil
from multiprocessing import Pool
from pathlib import Path
import shutil
from helpers import inputYN, mainParser
import os
import sys
import uuid
try:
    from PIL import Image
    from tqdm import tqdm
    import ffmpeg
except:
    pass



def renamerWorker(shard):
    err = None
    if len(shard) >= 1:
        for files in shard:
            try:
                os.rename(f"{files[2]}/{files[0]}", f"{files[2]}/{files[1]}")
            except Exception as e:
                if not err:
                    err = []
                err.append([files[0], files[1], e])
    print(f'Process: {os.getpid()} | Finished.')
    return err


def webmConverter(args):
    """ inputFile, outputFile, ffmpegPath, filename = args"""
    inputFile, outputFile, ffmpegPath, filename, multi = args

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
        if multi:
            return filename+".webm"
        else:
            oldNames.append(filename+".webm")

    else:
        os.remove(inputFile)
        if multi:
            return filename+".mp4"
        else:
            oldNames.append(filename+".mp4")


def webpConverter(args):
    """ inputFile, outputFile, filename, multi = args"""
    inputFile, outputFile, filename, multi = args

    try:
        img = Image.open(inputFile).convert("RGB")
        img.save(outputFile, "jpeg")
    except Exception as error:
        print(error)
        try:
            os.remove(outputFile)
        except:
            pass
        if multi:
            return filename+".webp"
        else:
            oldNames.append(filename+".webp")
    else:
        os.remove(inputFile)
        if multi:
            return filename+".jpeg"
        else:
            oldNames.append(filename+".jpeg")




if __name__ == '__main__':

    backupFolder = ".name_backups"
    renamingFolder = "Example_folder"
    multiprocessingEnabled = False
    convertWebm = False
    convertWebp = False
    ffmpegInstalled = False
    ffmpegPath = "ffmpeg"
    cpuCores = os.cpu_count()



    # There should be no need to runs this as root.
    if os.name == 'posix':
        systemLinux = True
        if os.geteuid() == 0:
            print("Don't run this script as root.")
            sys.exit(1)
    else:
        systemLinux = False


    parser = mainParser()

    args = parser.parse_args()
    

    # User has to provide the folder with files to rename
    if args.Path:
        renamingFolder = args.Path.strip("\\")

    if args.backup:
        backupFolder = args.backup.strip("\\")


    if args.cpus:
        cpuCores = int(args.cpus)


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
        convertWebp = inputYN("Convert all .webp to .jpeg before renaming?", defaultYes=False)

    

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
        convertWebm = inputYN("Convert all .webm to .mp4 before renaming?", defaultYes=False)
    



    # Creates a a backup folder where it will create file with old filenames and new ones
    if not Path(backupFolder).exists():
        os.makedirs(backupFolder)


    if systemLinux:
        strippedRenamingFolder = os.path.basename(renamingFolder)
    else:
        strippedRenamingFolder = os.path.basename(renamingFolder).split("\\")[-1]


    backPath = f"{backupFolder}/{strippedRenamingFolder.strip(' / ')}#&#{datetime.now().strftime('%d.%m.%y_%H%M')}#1.txt"
    if Path(backPath).exists():
        backPath = backPath[:-6] + f"#{int(backPath[-5]) +1}" + backPath[-4:]
    Path(backPath).touch(exist_ok=True)


    oldNames = list()
    if multiprocessingEnabled:
        pool = Pool(cpuCores)
        processes = []


    timeBefore = datetime.now()
    with os.scandir(renamingFolder) as dir:
        for entry in dir:
            filename, ext = os.path.splitext(entry.name)
            if entry.is_file() and entry.name[0] != ".":

                if ext == ".webp" and convertWebp:
                    inputFile = f"{renamingFolder}/{filename}.webp"
                    outputFile = f"{renamingFolder}/{filename}.jpeg"

                    if multiprocessingEnabled:
                        p = pool.apply_async(webpConverter, args=([inputFile, outputFile, filename, True],))
                        processes.append(p)
                    else:
                        webpConverter([inputFile, outputFile, filename, False])
                
                elif ext == ".webm" and convertWebm:
                    inputFile = f"{renamingFolder}/{filename}.webm"
                    outputFile = f"{renamingFolder}/{filename}.mp4"

                    if multiprocessingEnabled:
                        p = pool.apply_async(webmConverter, args=([inputFile, outputFile, ffmpegPath, filename, True],))
                        processes.append(p)

                    else:
                        webmConverter([inputFile, outputFile, ffmpegPath, filename, False])

                else:
                    oldNames.append(entry.name)

    if multiprocessingEnabled:
        pool.close()
        pool.join()
        
        for p in processes:
            value = p.get()
            if value:
                oldNames.append(value)
    
    if convertWebm or convertWebp:
        print(f"Files converted in {(datetime.now() - timeBefore).total_seconds()} seconds.")


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
            newNames.append(str(uuid.uuid4().hex) + "." + oldNames[i].split(".")[-1])
        if fileLen != len(newNames):
            print(f"Not same amount of new names generated as there are old names. This should not happen!\n\
                Len files: {fileLen} != new filenames: {len(newNames)}")
            sys.exit(3)
        elif fileLen > len(set(newNames)):
            print(f"Duplicate names in list! Generating new names.")
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
        fileCounter = 0
        filesPerWorkerList = list()
        filesPerWorkerList.append([])
        filesPerWorker = ceil(fileLen / cpuCores)
        i = 0
        j = 0
        for line in range(fileLen):
            i = i + 1
            filesPerWorkerList[j].append([oldNames[line],newNames[line], renamingFolder])
            fileCounter = fileCounter + 1
            if i == filesPerWorker:
                i = 0
                j = j + 1 
                filesPerWorkerList.append([])
        

        print(f"Renaming {fileCounter} files...")
        timeBefore = datetime.now()
        with Pool(cpuCores) as pool:
            r = pool.map(renamerWorker, filesPerWorkerList)
        
        err = False
        for ret in r:
            if ret:
                for job in ret:
                    if job:
                        err = True
                        print("---------")
                        print(f"File '{job[0]}' could not be renamed to '{job[1]}' !")
                        print(job[2])
                        print("---------")

        if err:
            print("Some files could not be renamed!")


                
        
        print(f"{fileLen} files renamed in {(datetime.now() - timeBefore).total_seconds()} seconds.")
            


    sys.exit()