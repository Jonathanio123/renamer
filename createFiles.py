import os, pathlib
from random import randint, choice
import shutil
from tqdm import tqdm
from multiprocessing import Pool


def creator(i, tmpFolder="Example_folder"):
    name = randint(0, 99999999999)
    filetype = choice(["jpg","png","gif","mp4","jpeg"])
    with open(f"{tmpFolder}/{name}.{filetype}", "x") as file:
        file.write(f"Info about this file.\nName: {name}\nFiletype: {filetype}\n")



if __name__ == '__main__':
    tmpFolder = "Example_folder"
    filesToCreate = 200000

    if pathlib.Path(tmpFolder).exists():
        print(f"Deleting '{tmpFolder}' folder.")
        shutil.rmtree(tmpFolder)

    os.mkdir(tmpFolder)

    with open(f"{tmpFolder}/.info", "x") as f:
        f.write("Some info")

    os.mkdir(f"{tmpFolder}/.backup")
    os.mkdir(f"{tmpFolder}/tmp")

    print("Creating workers")
    with Pool() as pool:
        r = pool.map(creator, range(filesToCreate))
    print(f"{filesToCreate} files created in '{tmpFolder}'.")

# Single threaded version
#    for i in tqdm(range(filesToCreate)):
#        name = randint(0, 99999999999)
#        filetype = choice(["jpg","png","gif","mp4","jpeg"])
#        with open(f"{tmpFolder}/{name}.{filetype}", "x") as file:
#            file.write(f"Info about this file.\nName: {name}\nFiletype: {filetype}\n")