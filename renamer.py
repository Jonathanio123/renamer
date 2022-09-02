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
    folder = shard[0]
    shard = shard[1:]
    if len(shard) >= 1:
        for files in shard:
            try:
                os.rename(f"{folder}/{files[0]}", f"{folder}/{files[1]}")
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
            .run(cmd=ffmpegPath, quiet=True)
        )

    except Exception as error:
        print(error)
        print(f"Error converting {filename}.webm to .mp4 format.")
        if multi:
            return filename+".webm"
        else:
            dirOverview.append(fileEntry(filename+".webm"))

    else:
        os.remove(inputFile)
        if multi:
            return filename+".mp4"
        else:
            dirOverview.append(fileEntry(filename+".mp4"))


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
            dirOverview.append(fileEntry(filename+".webp"))
    else:
        os.remove(inputFile)
        if multi:
            return filename+".jpeg"
        else:
            dirOverview.append(fileEntry(filename+".jpeg"))


class fileEntry:
    def __init__(self, oldFileName: str, newFileName: str = ""):
        self.oldFileName = oldFileName
        self.newFileName = newFileName
        _, self.fileExtension = os.path.splitext(oldFileName)

    def setNewName(self, filename: str) -> None:
        """Name without filename extension."""
        self.newFileName = f"{filename}{self.fileExtension}"


class fileList:
    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        self.fileNames = list()

    def append(self, file: fileEntry) -> None:
        self.fileNames.append(file)

    def length(self) -> int:
        return len(self.fileNames)

    def splitShards(self, amountOfShards: int = None) -> list:
        fileCounter = 0
        shards = list()
        shards.append([self.path])
        if amountOfShards:
            shardSize = amountOfShards
        else:
            shardSize = ceil(self.length() / cpuCores)  # Files per shard
        shardSize += 1  # First element is the folder path
        i = 0
        j = 0
        for file in self:
            i = i + 1
            shards[j].append([file.oldFileName, file.newFileName])
            fileCounter = fileCounter + 1
            if i == shardSize:
                i = 0
                j = j + 1
                shards.append([self.path])

        return shards

    def genNewName(self) -> None:
        length = self.length()
        if length < 1:
            raise Exception("No files found.")

        newGeneratedNames = []
        allUnique = False
        while not allUnique:
            for i in range(length):
                newGeneratedNames.append(uuid.uuid4().hex)
            if length != len(set(newGeneratedNames)):
                print(f"Duplicate names in list! Generating new names.")
            else:
                allUnique = True

        for (newName, file) in zip(newGeneratedNames, self):
            file.setNewName(newName)

    def __iter__(self):
        if self.length() < 1:
            StopIteration
        self.iter = 0
        return self

    def __next__(self) -> fileEntry:
        if self.length() == self.iter:
            raise StopIteration
        nextItem = self.fileNames[self.iter]
        self.iter += 1
        return nextItem

    def __getitem__(self, i: int) -> fileEntry:
        return self.fileNames[i]

    def __len__(self) -> int:
        return len(self.fileNames)


if __name__ == '__main__':

    backupFolder = ".name_backups"
    renamingFolder = "Example_folder"
    multiprocessingEnabled = False
    convertWebm = False
    convertWebp = False
    ffmpegInstalled = False
    ffmpegPath = "ffmpeg"
    cpuCores = os.cpu_count()

    # There should be no need to run this as root.
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
        renamingFolder = os.path.abspath(args.Path)

    if args.backup:
        backupFolder = os.path.abspath(args.backup)

    if args.cpus:
        cpuCores = int(args.cpus)

    if not Path(renamingFolder).is_dir():
        print(
            f"Folder '{renamingFolder}' does not exist. Pass folder name as an argument.\nExample: ./renamer.py <folder name>")
        sys.exit(2)

    if args.multithreading:
        multiprocessingEnabled = True

    if not args.script:
        inputYN(
            f"Rename all files in directory '{renamingFolder}'?", True, False)

    if not "PIL" in sys.modules:
        print("PIL library not installed, unable to convert .webp to .jpeg.")
        convertWebp = False
    elif args.convertP:
        print("Converting all .webp to .jpeg before renaming.")
        convertWebp = True
    elif not args.script:
        convertWebp = inputYN(
            "Convert all .webp to .jpeg before renaming?", defaultYes=False)

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
        convertWebm = inputYN(
            "Convert all .webm to .mp4 before renaming?", defaultYes=False)

    # Creates a a backup folder where it will create file with old filenames and new ones
    if not Path(backupFolder).exists():
        os.makedirs(backupFolder)

    if systemLinux:
        strippedRenamingFolder = os.path.basename(renamingFolder)
    else:
        strippedRenamingFolder = os.path.basename(renamingFolder)

    backPath = f"{backupFolder}/{strippedRenamingFolder}#&#{datetime.now().strftime('%d.%m.%y_%H%M')}#1.txt"
    if Path(backPath).exists():
        backPath = backPath[:-6] + f"#{int(backPath[-5]) +1}" + backPath[-4:]
    Path(backPath).touch(exist_ok=True)

    dirOverview = fileList(renamingFolder)

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
                        p = pool.apply_async(webpConverter, args=(
                            [inputFile, outputFile, filename, True],))
                        processes.append(p)
                    else:
                        webpConverter([inputFile, outputFile, filename, False])

                elif ext == ".webm" and convertWebm:
                    inputFile = f"{renamingFolder}/{filename}.webm"
                    outputFile = f"{renamingFolder}/{filename}.mp4"

                    if multiprocessingEnabled:
                        p = pool.apply_async(webmConverter, args=(
                            [inputFile, outputFile, ffmpegPath, filename, True],))
                        processes.append(p)

                    else:
                        webmConverter(
                            [inputFile, outputFile, ffmpegPath, filename, False])

                else:
                    dirOverview.append(fileEntry(entry.name))

    if multiprocessingEnabled:
        pool.close()
        pool.join()

        for p in processes:
            value = p.get()
            if value:
                dirOverview.append(fileEntry(value))

    if convertWebm or convertWebp:
        print(
            f"Files converted in {(datetime.now() - timeBefore).total_seconds()} seconds.")

    if dirOverview.length():
        print(f"Files to be renamed: {dirOverview.length()}")
    else:
        print(f"No files found in the folder '{renamingFolder}'.")
        sys.exit(2)

    dirOverview.genNewName()

    # Writes the backup file with old and new filenames
    with open(backPath, "w") as fileBackup:
        for file in dirOverview:
            fileBackup.write(file.oldFileName + "    " +
                             file.newFileName + "\n")

    if not multiprocessingEnabled:
        # For loop that renames files
        if "tqdm" in sys.modules:
            for i in tqdm(range(dirOverview.length()), ncols=100):
                os.rename(f"{renamingFolder}/{dirOverview[i].oldFileName}",
                          f"{renamingFolder}/{dirOverview[i].newFileName}")
            print("Finished renaming files.")

        else:
            print("Tqdm library not installed, not showing progress bar.")
            print("Renaming files...")
            timeBefore = datetime.now()
            for i in range(dirOverview.length()):
                os.rename(f"{renamingFolder}/{dirOverview[i].oldFileName}",
                          f"{renamingFolder}/{dirOverview[i].newFileName}")
            print(
                f"{dirOverview.length()} files renamed in {(datetime.now() - timeBefore).total_seconds()} seconds.")
    else:
        filesPerWorkerList = dirOverview.splitShards()

        print(f"Renaming {dirOverview.length()} files...")
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
                        print(
                            f"File '{job[0]}' could not be renamed to '{job[1]}' !")
                        print(job[2])
                        print("---------")

        if err:
            print("Some files could not be renamed!")

        print(f"{dirOverview.length()} files renamed in {(datetime.now() - timeBefore).total_seconds()} seconds.")

    sys.exit()
