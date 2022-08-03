Simple python script to randomize the filenames of all the files inside a folder.
 
 How to use:
 The main file is renamer.py. To specify the folder with files you want renamed, pass its name/path to the script as an argument. 
 For example, if you want to to specify a folder in the same directory as renamer.py then run 'renamer.py <folder name> '.
 
 Notes:
  - It will ignore all dotfiles and folders, therefore, it will not recursivly rename files inside folders.
  - It will ask to convert .webp to .jpegs, it will change the extenstion BEFORE randomizing the filenames.
  - In the same directory as renamer.py, it will create a .name_backups. Inside it wil create a txt file with the old filenames and the new ones.
  
  Optional dependencys:
  - [tqdm](https://github.com/tqdm/tqdm) - Too show progress of renaming files.
  - [Pillow](https://github.com/python-pillow/Pillow) - Too convert webp to .jpeg
  
