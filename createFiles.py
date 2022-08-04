import os, pathlib
from random import randint, choice
import shutil
from tqdm import tqdm

tmpFolder = "Example_folder"

if pathlib.Path(tmpFolder).exists():
    shutil.rmtree(tmpFolder)

os.mkdir(tmpFolder)

with open(f"{tmpFolder}/.info", "x") as f:
    f.write("Some info")

os.mkdir(f"{tmpFolder}/.backup")
os.mkdir(f"{tmpFolder}/tmp")

for i in tqdm(range(5000)):
    name = randint(0, 99999999999)
    filetype = choice(["jpg","png","gif","mp4","jpeg"])
    with open(f"{tmpFolder}/{name}.{filetype}", "x") as file:
        file.write(f"Info about this file.\nName: {name}\nFiletype: {filetype}\n")