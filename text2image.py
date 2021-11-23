# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 16:28:02 2020

@author: Wolf Culemann
"""

#%%

from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import glob
import argparse

import nltk
from nltk import tokenize

nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")


ap = argparse.ArgumentParser()
ap.add_argument(
    "-t",
    "--text-folder",
    type=str,
    default="./text/",
    help="folder with the txt file(s)",
)

ap.add_argument(
    "-o",
    "--output-subfolder",
    type=str,
    default="./text/images/",
    help="name of the output folder (subfolder of text folder)",
)

ap.add_argument(
    "-r",
    "--resolution",
    nargs="+",
    type=int,
    default=(1920, 1080),
    help="output resolution for images",
)

ap.add_argument(
    "-mw",
    "--max-width",
    type=int,
    default=75,
    help="max. number of characters per line",
)

ap.add_argument(
    "-f",
    "--font",
    type=str,
    default="times",
    help="font name (if it cant be found, put ttf-file into the same folder",
)

ap.add_argument("-fs", "--font-size", type=int, default=20, help="font size")

ap.add_argument(
    "-ls",
    "--line-space",
    type=float,
    default=2,
    help="space between lines, but includes next line!!!",
)

ap.add_argument(
    "-fc",
    "--font-color",
    nargs="+",
    type=int,
    default=(20, 20, 20),
    help="font color as rgb tuple",
)

ap.add_argument(
    "-bc",
    "--bg-color",
    type=int,
    nargs="+",
    default=(200, 200, 200),
    help="background color as rgb tuple",
)

ap.add_argument(
    "-cp",
    "--comma-pagebreak",
    type=bool,
    default=False,
    help="whether to allow breaks at comma",
)

ap.add_argument(
    "-bb",
    "--brutal-break",
    type=bool,
    default=False,
    help="whether to allow breaks in the middle of the sentence",
)

ap.add_argument(
    "-dt",
    "--dist-top",
    type=int,
    default=2,
    help="distance from the top of the page in numbers of line (heights)",
)


##### measured params

# if text is not centered enough:
# larger values --> text shifts to the left
# smaller values --> text shifts to the right
ap.add_argument(
    "-fhm",
    "--font-height-measured",
    type=int,
    default=22,
    help="measured height of the font type in pix (for respective size)",
)
ap.add_argument(
    "-fwm",
    "--font-width-measured",
    type=int,
    default=10,
    help="measured width of the font type in pix (for respective size)",
)

ap.add_argument(
    "-at",
    "--above-title",
    type=int,
    default=200,
    help="space (in pix) above title/headline",
)


def write_title_page_img(current_page, text_name, page_number, **kwargs):

    global PAGE, OUTPUT_NAME, ARGS

    font_width = (ARGS["font_size"] / ARGS["font_size"]) * ARGS["font_width_measured"]

    PAGE = 0

    img = Image.new("RGB", tuple(ARGS["resolution"]), color=tuple(ARGS["bg_color"]))
    fnt = ImageFont.truetype(
        font=os.path.join(DIR_PATH, ARGS["font"]),
        size=ARGS["font_size"],
        encoding="utf-8",
    )
    d = ImageDraw.Draw(img)
    i = 0

    while current_page != []:
        # draw all the lines onto the current img
        text = current_page.pop(0)
        text = text.strip()

        # import pdb;pdb.set_trace()
        # calc x-axis pos for centering
        diff = (ARGS["max_width"] - len(text)) * font_width

        d.text(
            (
                kwargs["starting_point"][0] + (diff / 2),
                kwargs["starting_point"][1]
                + i * ARGS["line_space"] * ARGS["font_size"]
                + ARGS["above_title"],
            ),
            text,
            font=fnt,
            fill=tuple(ARGS["font_color"]),
        )  # .strip(" ")
        i += 1
    img.save(os.path.join(ARGS["output_subfolder"], eval(OUTPUT_NAME)))
    PAGE += 1
    return "200"


def write_current_page_img(current_page, text_name, page_number, **kwargs):

    global PAGE, OUTPUT_NAME, DIR_PATH, ARGS

    img = Image.new("RGB", ARGS["resolution"], color=tuple(ARGS["bg_color"]))
    fnt = ImageFont.truetype(
        font=os.path.join(DIR_PATH, ARGS["font"]),
        size=ARGS["font_size"],
        encoding="utf-8",
    )
    d = ImageDraw.Draw(img)
    i = 0
    added = 0
    while current_page != []:
        # draw all the lines onto the current img
        text = current_page.pop(0)
        l_space = ARGS["line_space"] * ARGS["font_size"]
        if text.startswith("***"):
            text = text.replace("***", "")  # replace three stars
            # l_space = line_space + add_line_space_break
            added += 0  # add_line_space_break
        # text = text.replace("  "," ") #replace double blanks
        d.text(
            (
                kwargs["starting_point"][0],
                kwargs["starting_point"][1] + i * l_space + added,
            ),
            text,
            font=fnt,
            fill=tuple(ARGS["font_color"]),
        )  # .strip(" ")
        i += 1
    # import pdb;pdb.set_trace()
    img.save(os.path.join(ARGS["output_subfolder"], eval(OUTPUT_NAME)))
    PAGE += 1
    return "200"


def build_images(lines, size, width, pictures=[], **kwargs):

    global ARGS

    if len(lines) <= size:
        pictures.append(lines)
        return pictures
    else:
        lines_to_consider = lines[0:size]
        rest_lines = lines[size:]
        sentences = tokenize.sent_tokenize(unwrap(lines_to_consider), language="german")
        if not sentences[-1].endswith("."):
            # import pdb;pdb.set_trace()
            if (
                (len(sentences[-1]) > 1.5 * width)
                and (", " in sentences[-1])
                and ARGS["comma_pagebreak"]
            ):
                splitty = sentences[-1].rsplit(", ", 1)
                if len(splitty) > 1:
                    last_part = splitty[1]
                    rest_lines.insert(0, last_part)
                    sentences[-1] = splitty[0] + ","
                # If last part is less than a line width also push forward,
                # here you can decide if you want to skip more
                elif len(splitty[0]) < width:
                    rest_lines.insert(0, splitty[0])
                    sentences.pop(-1)
            else:
                rest_lines.insert(0, sentences[-1])
                sentences.pop(-1)
        pictures.append(wrap(unwrap(sentences), width))
        rest_lines = wrap(unwrap(rest_lines), width)
        return build_images(rest_lines, size, width, pictures)


def wrap(raw_text, maxwidth, linebreak="***"):
    breaked = raw_text.split(linebreak)
    wrapped_lines = []
    for par in breaked:
        wrapped_lines.extend(textwrap.wrap(par, width=maxwidth))

    wrapped_lines = [
        l.replace("    ", "***    ") for l in wrapped_lines
    ]  # reinsert the placeholder for later split
    return wrapped_lines


def unwrap(wrapped_text):
    return " ".join(wrapped_text)


def main(args):

    text_path = args["text_folder"]  # "./name_der_rose/"
    # output_subfolder = os.path.join(text_path,args["output_subfolder"])
    if not os.path.exists(args["output_subfolder"]):
        os.makedirs(args["output_subfolder"])

    # args["output_subfolder"] = output_subfolder

    text_list = glob.glob(f"{text_path}*.txt")

    img_res = args["resolution"]

    # PARAMS
    max_width = args["max_width"]
    font_size = args["font_size"]
    line_space = args["line_space"] * font_size  # includes next line (in pix)
    dist_top = args["dist_top"]

    f_size = args["font_height_measured"]
    f_width = args["font_width_measured"]
    font_width = (font_size / f_size) * f_width

    # approx. max lines
    max_lines = int((img_res[1] - 2 * dist_top * line_space) / line_space)
    print("INFO: Calculated max. numbers of lines:   ", max_lines)

    # centering the text approx.
    start_x = (img_res[0] - (font_width * max_width)) / 2
    starting_point = (start_x, 2 * line_space)  # 120)

    # centering the text approx.
    start_x = (img_res[0] - (font_width * max_width)) / 2
    starting_point = (start_x, 2 * line_space)  # 120)

    for text in text_list:

        text_name = os.path.splitext(os.path.basename(text))[0]

        print(f"INFO: reading {text}")
        with open(text, "r", encoding="utf-8") as f:
            content = f.read()

        print("INFO: stripping double spaces and line breaks")
        while True:
            content = content.replace("  ", " ")  # replace double spaces
            content = content.replace("\n", " ")  # strip line breaks

            proceed = "  " in content

            if not proceed:
                proceed = "\n" in content

            if not proceed:
                break

        # add four spaces behind §§§ for indentation
        content = content.replace("§§§", "§§§***    ")

        heads_pages = content.split("###")
        page_counter = 0
        for section in heads_pages:
            if "$" in section:
                # is header
                pics = build_images(section.split("$"), max_lines, max_width, **args)

                while pics != []:
                    page_counter += 1
                    print(f"INFO: Writing page number {page_counter} for {text}")
                    write_title_page_img(
                        pics.pop(0),
                        text_name,
                        page_counter,
                        starting_point=starting_point,
                        **args,
                    )
            else:

                paras = section.split("§§§")
                paragraphs = []
                for p in paras:
                    paragraphs.append(textwrap.wrap(p, width=max_width))

                # remove empty list
                paragraphs = [l for l in paragraphs if l != []]

                lines = [l for l_par in paragraphs for l in l_par]

                pics = build_images(lines, max_lines, max_width, **args)

                while pics != []:
                    page_counter += 1
                    print(f"INFO: Writing page number {page_counter} for {text}")
                    write_current_page_img(
                        pics.pop(0),
                        text_name,
                        page_counter,
                        starting_point=starting_point,
                        **args,
                    )


if __name__ == "__main__":

    args = vars(ap.parse_args())
    ARGS = args.copy()
    DIR_PATH = os.path.dirname(os.path.realpath(__file__))

    # global variable for page counting
    PAGE = 0

    # how to name the output images, beware of the string structure (string representation of an f-string)
    OUTPUT_NAME = 'f"{text_name}_{str(PAGE).zfill(3)}.png"'

    main(args)

    print("INFO: Done.")
