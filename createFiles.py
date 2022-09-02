import os, pathlib
from random import choice
from datetime import datetime
import shutil
from multiprocessing import Pool
from binascii import hexlify
from helpers import inputYN
import uuid


def creator(amount):
    for _ in range(amount):
        name = hexlify(uuid.uuid4().hex)
        filetype = choice(["jpg","png","gif","mp4","jpeg"])
        with open(f"{tmpFolder}/{name}.{filetype}", "x") as file:
            file.write(f"Info about this file.\nName: {name}\nFiletype: {filetype}\n")
    print(f'Process: {os.getpid()} | Finished.')

def singleCreator(folder: str,amount: int, seedGen):
    for _ in range(amount):
        seed = seedGen.getrandbits(128)
        name = uuid.UUID(int=seed, version=4).hex
        filetype = ["jpg","png","gif","mp4","jpeg"]
        filetype = filetype[seedGen.randint(0,4)]
        with open(f"{folder}/{name}.{filetype}", "x") as file:
            file.write(f"Info about this file.\nName: {name}\nFiletype: {filetype}\n")

tmpFolder = "Example_folder"
filesToCreate = 10_000

if __name__ == '__main__':
    inputYN(f"This will completely destroy the folder '{tmpFolder}' and its contents. Then fill it with {filesToCreate} random files.", True, False)
    
    
    filesPerWorker = filesToCreate // os.cpu_count()
    filesPerWorkerList = [filesPerWorker] * os.cpu_count() + [filesToCreate - filesPerWorker * os.cpu_count()]


    if pathlib.Path(tmpFolder).exists():
        print(f"Deleting '{tmpFolder}' folder.")
        shutil.rmtree(tmpFolder)

    os.mkdir(tmpFolder)

    with open(f"{tmpFolder}/.info", "x") as f:
        f.write("Some info")

    os.mkdir(f"{tmpFolder}/.backup")
    os.mkdir(f"{tmpFolder}/tmp")

    print("Creating files...")
    timeBefore = datetime.now()
    with Pool() as pool:
        r = pool.map(creator, filesPerWorkerList)
    
    print(f"{filesToCreate} files created in {(datetime.now() - timeBefore).total_seconds()} seconds.")

# Old single threaded version
#    for i in tqdm(range(filesToCreate)):
#        name = randint(0, 99999999999)
#        filetype = choice(["jpg","png","gif","mp4","jpeg"])
#        with open(f"{tmpFolder}/{name}.{filetype}", "x") as file:
#            file.write(f"Info about this file.\nName: {name}\nFiletype: {filetype}\n")