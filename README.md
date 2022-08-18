Simple python script to randomize the filenames of all the files inside a folder.
 
 How to use:
  The main file is renamer.py. To specify the folder with files you want renamed, pass its name/path to the script as an argument. 
  For example, if you want to specify a folder in the same directory as renamer.py then run 'renamer.py <folder name> '.
  The createFiles.py is just for testing. For more on usage see help wtih 'renamer.py -h'
 
 Notes:
  - Random names are made with uuid4().hex, the file extension is kept.
  - It will ignore all dotfiles and folders, therefore, it will not recursively rename files inside folders.
  - It will ask to convert .webp to .jpegs and .webm to .mp4, it will change the extension BEFORE randomizing the filenames.
  - In the same directory as renamer.py, it will create a .name_backups. Inside it will create a txt file with the old filenames and the new ones. Which you can use to restore the old filenames manually or with the undoRenamer.py
  
  Optional dependencies:
  - [tqdm](https://github.com/tqdm/tqdm) - To show progress of renaming files.
  - [Pillow](https://github.com/python-pillow/Pillow) - To convert .webp to .jpeg
  - [ffmpeg-python](https://github.com/kkroening/ffmpeg-python) and [FFmpeg](https://ffmpeg.org/) - To convert .webm to .mp4. 


  Warning:
  - This is just a hobby project for myself and there are likely more than a few bugs. Remember to make backups.
  
