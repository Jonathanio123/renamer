import sys
import argparse
import os
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


def mainParser():
    parser = argparse.ArgumentParser(description="Python script to rename all files (except: dotfiles and folders) inside a folder with random names.\
                                                    It will create a backup folder '.name_backups' where a file with old names and new names are saved")

    parser.add_argument('Path',
                       metavar='<path>',
                       type=str,
                       help='Path to folder with files you want renamed.')

    parser.add_argument("-m", "--multithreading", 
                        required=False,
                        action='store_true',
                        help="WARNING MIGHT BE BUGGY! USE AT YOUR OWN RISK! Enable multiprocessing when convering and renaming files.")

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

    parser.add_argument('--backup',
                       metavar="<path>",
                       type=str,
                       help='Path to backup folder. Default path is .name_backups/')

    parser.add_argument('--cpus',
                       metavar=f"[1-{os.cpu_count()}]",
                       type=int,
                       choices=range(1,os.cpu_count()+1),
                       help='Maximum threads to use. Default is to use all cpu cores. Has no effect without the "-m" flag')

    return parser