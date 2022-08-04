import sys
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