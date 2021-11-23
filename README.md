# text2image
Converting plain text to images, mainly for eyetracking studies

# Basic Usage

Make sure, the requirements are installed in the env (install with "pip install -r requirements.txt")

1. Place a .txt file into the "text" folder (or create a new folder, that you specify in the arguments).
2. Make sure the text contains "###" for splitting headers and "$$" for sections within the title-page (see example saarland.txt)
3. Run with -h argument to see the list of arguments (python text2image.py -h)
4. Run script with specified arguments, e.g. "python text2image.py -f arial -bc 0 0 0 -fc 200 200 200" for creating white text with arial font on black background
