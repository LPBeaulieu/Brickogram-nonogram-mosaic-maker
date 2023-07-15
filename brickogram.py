from alive_progress import alive_bar
import copy
import glob
import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
import re
import sys


#The image file paths within the "Images" subfolder of your working folder
#(excluding the nonogram clue PDF files) are assembled in the "img_files"
#list.
cwd = os.getcwd()
path_img = os.path.join(cwd, "Images", "*.*")
img_files = glob.glob(path_img)
img_files = [file for file in img_files if (file[-4:].lower() != ".pdf" and
"Thumbnail Image" not in file and "Required 1 x 1 Plates" not in file)]

#You can opt to generate the nonobram clud PDF files in A4 format
#by passing in the "A4" argument when running the Python code.
A4 = False
#The "A4_margin" variable adds 25 pixels to the "y" coordinate
#where the puzzle title will be written on the clue pages, when
#generated in A4 format, to account for the greater height of
#an A4 page versus a US letter page.
A4_margin = 0
#The blank variable, initialized to "None" will store the RGB
#value of the blank that will be used in a given
#nonogram puzzle. You can opt to have no blanks by passing
#in the "no_blanks" argument when running the code, and all
#the colors and numbers will be provided on the clue sheets.
#If the "no_blanks" argument is not passed in, then the code
#automatically selects the lightest color in nonogram grid that
#has a proportion equal or above that of "auto_blanks_threshold"
#in the nonogram grid. The default threshold is set to five percent
#and should you want to modify it, you would need to input your
#desired value after the "auto_blanks:" argument. For example,
#should you want a threshold of 20%, you would enter "auto_blanks:20".
#Otherwise, you can select a blank color that would apply
#to all the nonogram puzzles generated for the pixelated
#images found within the "Images" folder by providing
#the blank color hex code or parenthesized RGB value
#after the "blank:" argument. For example, entering
#the following "py brickogram.py blank:(255,255,255)" would
#select white as the blank color for all of the images
#found in the "Images" folder of your working folder.
#Finally, should you want a specific image to use a
#particular blank color, simply include the parenthesized
#RGB value at the end of its file name
#(ex: "image file name (255, 255, 255).png").
blank = None
no_blanks = False
auto_blanks = True
auto_blanks_threshold = 0.05
#The "blank_user" variable stores your selected blank
#color that applies to all the images found in the
#"Images" folder (unless you added a parenthesized
#RGB value at the end of a given image file name).
#The code cycles through all of the images and will
#reset the value of "blank" to "None" if the "blank_user"
#is still equal to "None", so that the blank color
#could be automatically determined by the code
#(unless the parenthesized RGB value was provided
#in the image file name).
blank_user = None
#The pixel side dimensions of a 1x1 plate are stored
#within the "stud_pixels" variable and will allow the
#nonogram clues to be drawn to scale, so that they
#could be lined up with the base plate on which the
#nonogram will be solved.
stud_pixels = 94

#The number of cells per side of the square nonogram
#grid is set to 32 by default (as the standard square
#base plates measure 32 studs per side), but may be
#changed to any number, as long as the total number
#of studs in the mosaic is a multiple of that number.
#That is to say your nonogram grid will fit "x" times
#within the total width and "y" times in the total
#height of your final mosaic, where "x" and "y" are
#both integers. For example, a mosaic with a total
#width 64 studs and a height of 128 studs would require
#a nonogram grid size of 16 x 16 (16 studs) or 32 x 32
#(32 studs), both of which are common base plate
#dimensions. Simply pass in the number of nonogram
#cells after the "nonogram_cells:" argument when
#running the code (for example: ' py brickogram
#"nonogram_cells:16" ' for a 16 x 16 stud nonogram grid).
nonogram_cells = 32
#The perforations margin is set at the pixel equivalent
#of 0.75 inch at 300 ppi resolution and will allow for
#the clue sheets to be perforated and bound using flexible
#plastic binding rings looped through some 2 x 8 Technic plates
#with 7 Holes. These will allow the instructions to be clamped
#onto the base paltes to make sure the clues stay aligned
#with their corresponding row or column.
perforations_margin = 225
#The "non_printable_area_margin" corresponds to the pixel
#equivalent of a 0.25 inch margin at 300 ppi resolution,
#and is used to factor in the non printable area of most
#printers corresponding to a quarter inch.
non_printable_area_margin = 75
#The starting font size of the different fonts used throughout
#the clue documents is determined below and are automatically
#shrunk down to the appropriate size on the page. The relative
#font sizes are also automatically harmonized in order for the
#document to look nice. You can place different True Type Font
#(".ttf") files in the font folders should you like to have
#different fonts in the PDF documents, and their size and spacing
#will adjust themselves automatically. The "Fonts" folder contains
#the "Cover Page Heading Font" subfolder (for the heading of the
#the cover pages, the default font being taken from the
#"Nb Pixel Font Bundle 2", check them out at
#https://nimblebeastscollective.itch.io/nb-pixel-font-bundle).
#The other subfolders are "Cover Page Subtitle Font" (for the subtitle
#on the cover page), "Title Page Heading Font" and "Title Page Text Font"
#(for the heading and body text on the title pages, respectively,
#"Title Font" (for the headings on the actual clue sheets) and "Numbers Font"
#(for the clue numbers).
numbers_font_size = 150
title_font_size = 300
title_page_heading_font_size = 300
title_page_text_font_size = 300
cover_page_heading_font_size = 300
cover_page_subtitle_font_size = 300
cover_page_heading_string = "Nonogram Puzzle"
top_cover_page_subtitle_string = "Top Panel Clues"
side_cover_page_subtitle_string = "Side Panel Clues"
title_page_heading_string = "Nonogram Puzzle"

title_page_blank_string = "In this puzzle, the blank color is:"
title_page_no_blanks_string = "There are no blanks in this puzzle."
title_page_auto_blanks_string = "The blank colors are shown in the top left corners of the clue sheets."
title_page_materials_string = "For this project, you will need the following 1 x 1 plates:"
column_string = "column"
row_string = "row"
top_string = "Top"
side_string = "Side"
side_panel_pdf_name = " Side Panels.pdf"
top_panel_pdf_name = " Top Panels.pdf"
continued_string = "Cont'd..."
continued_string_new_page = "Required 1 x 1 Plates (Cont'd)"

if len(sys.argv) > 1:
    #The "try/except" statement will
    #intercept any "ValueErrors" and
    #ask the users to correctly enter
    #the desired values for the variables
    #directly after the colon separating
    #the variable name from the value.
    try:
        for i in range(1, len(sys.argv)):
            if sys.argv[i].strip().lower()[:2] == "a4":
                A4 = True
            elif sys.argv[i].strip().lower()[:6] == "blank:":
                if sys.argv[i].strip().lower()[6] == "(" and sys.argv[i][6:].strip().lower()[-1] == ")":
                    blank = sys.argv[i].strip()[6:]
                    blank_user = blank
                    blank_list = [int(element.strip()) for element in blank_user[1:-1].split(",")]
                    blank_tuple_user = tuple(blank_list)
                    auto_blanks = False
                else:
                    blank = sys.argv[i][6:].lower().replace("#", "")
                    blank_tuple_user = tuple([int(blank[i:i+2], 16) for i in range(0, len(blank), 2)])
                    blank = str(blank_tuple_user)
                    blank_user = blank
            elif sys.argv[i].strip().lower() == "no_blanks":
                no_blanks = True
                auto_blanks = False
            elif sys.argv[i].strip().lower()[:11] == "auto_blanks":
                if len(sys.argv[i].strip().lower()) > 12 and sys.argv[i].strip()[11] == ":":
                    auto_blanks_threshold = float(int(sys.argv[i].strip()[12:])/100)
            elif sys.argv[i].strip().lower()[:15] == "nonogram_cells:":
                nonogram_cells = int(sys.argv[i].strip()[15:])

    except:
        sys.exit('\nPlease ensure that the additional arguments that you pass in when ' +
        'running the Python code are separated by spaces. Also, any RGB values following ' +
        'the "blank:" argument should be parenthesized, as in the following example: ' +
        '"py brickogram.py a4 blank:(255,255,255)", which would set the blank to white ' +
        'for all the pixelated images found in the "Images" subfolder of your working folder.')

#The code automatically retrieves the ".ttf" font files
#within the folders mentioned above and will instantiate
#ImageFont objects for them, provided that a single TTF
#file was provided in each folder.
path_font = os.path.join(cwd, "Fonts", "Numbers Font", "*.ttf")
numbers_font_files = glob.glob(path_font)

path_font = os.path.join(cwd, "Fonts", "Title Font", "*.ttf")
title_font_files = glob.glob(path_font)

path_font = os.path.join(cwd, "Fonts", "Title Page Heading Font", "*.ttf")
title_page_heading_font_files = glob.glob(path_font)

path_font = os.path.join(cwd, "Fonts", "Title Page Text Font", "*.ttf")
title_page_text_font_files = glob.glob(path_font)

path_font = os.path.join(cwd, "Fonts", "Cover Page Heading Font", "*.ttf")
cover_page_heading_font_files = glob.glob(path_font)

path_font = os.path.join(cwd, "Fonts", "Cover Page Subtitle Font", "*.ttf")
cover_page_subtitle_font_files = glob.glob(path_font)



if (not numbers_font_files or not title_font_files or not title_page_heading_font_files or
not title_page_text_font_files or not cover_page_heading_font_files or not cover_page_subtitle_font_files or
len(numbers_font_files) > 1 or len(title_font_files) > 1 or
len(title_page_heading_font_files) > 1 or len(title_page_text_font_files) > 1 or
len(cover_page_heading_font_files) > 1 or len(cover_page_subtitle_font_files) > 1):
    sys.exit('\n\nPlease include a single "True Type Font (.ttf)" file in the ' +
    '"Numbers Font" subfolder within your working folder, and another one in the ' +
    '"Title Font" subfolder. The same goes for the folders "Title Page Heading Font", ' +
    '"Title Page Text Font", "Cover Page Heading Font" and "Cover Page Subtitle Font".')
else:
    numbers_font = ImageFont.truetype(numbers_font_files[0], numbers_font_size)
    title_font = ImageFont.truetype(title_font_files[0], title_font_size)
    title_page_heading_font = ImageFont.truetype(title_page_heading_font_files[0], title_page_heading_font_size)
    title_page_text_font = ImageFont.truetype(title_page_text_font_files[0], title_page_text_font_size)
    cover_page_heading_font = ImageFont.truetype(cover_page_heading_font_files[0], cover_page_heading_font_size)
    cover_page_subtitle_font = ImageFont.truetype(cover_page_subtitle_font_files[0], cover_page_subtitle_font_size)


#The "for i in range(len(imf_files))" loop will cycle through the
#pixelated images found within the "Images" subfolder of the
#working folder, and append the corresponding title page and
#clue sheets at the end of the "side_panel_pdf_name"
#and "top_panel_pdf_name" PDF documents each initially
#containing a cover page.
print("\nCurrently creating a total of " + str(len(img_files)) + " nonograms:\n")
with alive_bar(len(img_files)) as bar:
    for i in range(len(img_files)):
        try:
            #As the clue sheets headings vary from one image from another,
            #given that they have different file names, the "title_font_size"
            #and "title_font" need to be reinitialized in-between each image.
            #Similarly, as one image could contain a blank RGB tuple at the
            #end of its file name, which would place a "title_page_blank_string"
            #followed by the 1 x 1 plate depicting the blank color used throughout
            #the image instead of a "title_page_auto_blanks_string" on the title page,
            #the "title_page_text_font_size" and "title_page_text_font" both need
            #to be reinitialized as well in-between images.
            title_font_size = 300
            title_font = ImageFont.truetype(title_font_files[0], title_font_size)
            title_page_text_font_size = 300
            title_page_text_font = ImageFont.truetype(title_page_text_font_files[0], title_page_text_font_size)

            #The "blank_user" variable stores your selected blank
            #color that applies to all the images found in the
            #"Images" folder (unless you added a parenthesized
            #RGB value at the end of a given image file name).
            #The code cycles through all of the images and will
            #reset the value of "blank" to "None" if the "blank_user"
            #is still equal to "None", so that the blank color
            #could be automatically determined by the code
            #(unless the parenthesized RGB value was provided
            #in the image file name).
            if blank_user:
                blank = blank_user
                blank_tuple = blank_tuple_user
            else:
                blank = None
            #The code will screen the file name to see whether
            #it ends with a parenthesized RGB value (an opening
            #parenthesis, folowed by one or more digits, a comma,
            #with a space or not before the subsequent digit, and
            #so on). That RGB value would then supersede any other
            #specified blank values for that image.
            image_name = "".join(img_files[i].split(".")[:-1]).replace("\\", "/").split("/")[-1]
            image_name_blank = re.findall(r"([(]\d+,[ ]?\d+,[ ]?\d+[)]\Z)", image_name)
            if image_name_blank:
                blank = image_name_blank[0]
                blank_tuple = tuple([int(element.strip()) for element in blank[1:-1].split(",")])
                image_name = image_name.replace(blank, "")
                auto_blanks = False

            #Each of the different images will be stored
            #in their respective folders in this version of the code.
            if not os.path.isdir(os.path.join(cwd, "Images", image_name)):
                os.makedirs(os.path.join(cwd, "Images", image_name))

            img = Image.open(img_files[i])
            img = img.convert('RGB')
            pix = img.load()

            #The width and height of the pixelated image are stored
            #in the "width" and "height" variables, respectively, and
            #will be used to cycle through the horizontal and vertical
            #pixels to determine the locations of color transitions along
            #both axes. This will enable the code to determine the aggregated
            #pixel size in the pixelated image (how many actual pixels make
            #up an aggregated pixel. For example, a "pixel_size" of 20 pixels
            #per aggregated pixel in a 1280x1280 px image would give a 64 x 64
            #stud mosaic).
            width, height = img.size

            #The "color_transitions_x" stores the "x,y" coordinates of any
            #pixel of which the preceding horizontal pixel's RGB value ("pix[x-1, y]")
            #differs from it. The "delta_x" list compiles the difference between the
            #"x" coordinates of successive pixels of the same "y" value within "color_transitions"
            color_transitions_x = [[x,y] for y in range(height) for x in range(1, width) if pix[x,y] != pix[x-1, y]]
            delta_x = [color_transitions_x[i][0] - color_transitions_x[i-1][0]
            for i in range(1, width) if color_transitions_x[i][1] == color_transitions_x[i-1][1]]

            if delta_x:
                #The minimum pixel distance in-between two color transition inflection points
                #is stored in the "minimum_delta_x".
                minimum_delta_x = min(delta_x)

            #A similar approach is taken for the vertical "y" axis.
            color_transitions_y = [[x,y] for x in range(height) for y in range(1, height) if pix[x,y] != pix[x, y-1]]
            delta_y = [color_transitions_y[i][1] - color_transitions_y[i-1][1]
            for i in range(1, height) if color_transitions_y[i][0] == color_transitions_y[i-1][0]]

            if delta_y:
                minimum_delta_y = min(delta_y)

            #Comparing the "minimum_delta_x" and "minimum_delta_y" will allow
            #to determine the size of an individual aggregated pixel. There needs
            #to be at least one aggregated pixel in the pixelated image that is
            #preceded and followed by aggregated pixels of a different color on
            #both the horizontal and vertical axes.
            if delta_x and delta_y:
                pixel_size = min(minimum_delta_x, minimum_delta_y)
            elif delta_x:
                pixel_size = minimum_delta_x
            elif delta_y:
                pixel_size = minimum_delta_y
            else:
                sys.exit("Please ensure that your pixelated image has at least one " +
                "aggregated pixel that is preceded and followed by aggregated pixels " +
                "of a different color on both the horizontal and vertical axes. " +
                "This will allow the code to figure out how many actual pixels fit " +
                "within one of the aggregated pixels.")

            #The list "same_color_side" will keep tabs on the sequences of aggregated pixels
            #of same color for constructing the clues on the left-hand side of the nonogram puzzle.
            #The dictionary "colors" will count the total number of 1x1 plates of each color that
            #are used throughout the mosaic.
            same_color_side = []
            colors = dict()
            #The "for y in range" and for x in range" loops start at the center
            #coordinates of the first aggregated pixel (math.floor(pixel_size/2)),
            #so that any slight misalignment of the image during cropping would not
            #impact the detected color ("pix[x,y]"). The step in these loops is equivalent
            #to the actual number of pixels in an aggregated pixel ("pixel_size"), thus
            #effectively jumping the center of one aggregated pixel to that of the next one.
            #For every row in the pixelated image, an empty list is appended to the
            #"same_color_side" list. Then, within that empty list, a new empty list
            #is placed at the start of the row, and each sequence of same colored
            #aggregated pixel is added to it up to the number of cells per side of
            #the square nonogram grid (thus completing the first "column chunk" for
            #that given row). Upon reaching that point, a new empty list is appended
            #to the last row element of the "same_color_side" list and some more
            #same-colored sequences are added in the same fashion, until the end
            #of the row is reached. The expression "(x-math.floor(pixel_size/2))%
            #(nonogram_cells*pixel_size) == 0" means that after cancelling the initial
            #offset of "pixel_size/2", the current "x" pixel is a multiple of the
            #pixel size of the pixelated image covered by the nonogram puzzle
            #(nonogram_cells*pixel_size) if there is no remainder to the modulus operation.

            #An example of a row of a pixelated image is as follows, with each actual pixel
            #represented by a letter and the aggregated pixels sharing the same successive
            #letters. The two "column chunks" illustrate that while the nonogram might have a
            #number of cells per side ("nonogram_cells", here represented by the length of a
            #column chunk) that is inferior to the total number of aggregated pixels per side
            #of the pixelated image, the latter needs to be a multiple of the pixel equivalent
            #of "nonogram_cells" ("nonogram_cells*pixel_size").

            #                                   Column chunk 1                  Column chunk 2
            #Row of a pixelated image OOOOXXXXOOOOXXXXOOOOXXXXOOOOXXXX OOOOXXXXOOOOXXXXOOOOXXXXOOOOXXXX

            for y in range (math.floor(pixel_size/2), height, pixel_size):
                same_color_side.append([])
                for x in range(math.floor(pixel_size/2), width, pixel_size):
                    if x == math.floor(pixel_size/2) or (x-math.floor(pixel_size/2))%(nonogram_cells*pixel_size) == 0:
                        same_color_side[-1].append([])
                    else:
                        #At the start of every new "column chunk" of a given "same_color_side" row index
                        #for the pixelated image, if the preceding aggregated pixel on the horizontal
                        #axis is the same as the preceding one, then the number of occurences of
                        #successive pixels of that color is added to the last "column chunk" element
                        #of the last row element ("same_color_side[-1][-1].append([2, pix[x,y]])").
                        if same_color_side[-1][-1] == []:
                            if pix[x, y] == pix[x-pixel_size, y]:
                                same_color_side[-1][-1].append([2, pix[x,y]])
                                #The color isn't already found in the "colors"
                                #dictionary, it is added at this point. Otherwise,
                                #the value of that color is incremented by two.
                                if pix[x,y] in colors:
                                    colors[pix[x,y]] = colors[pix[x,y]] + 2
                                else:
                                    colors[pix[x,y]] = 2
                            #If the current pixel color differs from that of the previous
                            #pixel on the "x" axis, then both are added in sequence to the
                            #last "column chunk" element of the last row element of "same_color_side".
                            else:
                                same_color_side[-1][-1].append([1, pix[x-pixel_size,y]])
                                same_color_side[-1][-1].append([1, pix[x,y]])
                                #For each of the differently colored successive aggregated pixels,
                                #if it isn't already found in the "colors" dictionary, it is added
                                #to it, otherwise its value is incremented by one.
                                if pix[x-pixel_size,y] in colors:
                                    colors[pix[x-pixel_size,y]] = colors[pix[x-pixel_size,y]] + 1
                                else:
                                    colors[pix[x-pixel_size,y]] = 1
                                if pix[x,y] in colors:
                                    colors[pix[x,y]] = colors[pix[x,y]] + 1
                                else:
                                    colors[pix[x,y]] = 1
                        #If the current "column chunk" index of a given row of "same_color_side" already contains at least
                        #one aggregated pixel entry, and that the current pixel's color matches that of the preceding one,
                        #then the preceding pixel entry is updated such as to increment the color count by one for that
                        #sequence of same-colored pixels. As the color was already encountered within the pixelated image,
                        #the value for that color within the "colors" dictionary can be incremented by one as well.
                        elif len(same_color_side[-1][-1]) > 0 and pix[x, y] == pix[x-pixel_size, y]:
                            same_color_side[-1][-1][-1] = [same_color_side[-1][-1][-1][0]+1, same_color_side[-1][-1][-1][1]]
                            colors[pix[x,y]] = colors[pix[x,y]] + 1
                        #If the current "column chunk" index of a given row of "same_color_side" already contains at least
                        #one aggregated pixel entry, and that the current pixel's color doesn't match that of the preceding one,
                        #then a new colored aggregated pixel is appended to the current "column chunk" of the last row of
                        #"same_color_side" with a counter of one.
                        elif len(same_color_side[-1][-1]) > 0 and pix[x, y] != pix[x-pixel_size, y]:
                            same_color_side[-1][-1].append([1, pix[x,y]])
                            #Once again, if the color isn't already found in the "colors" dictionary,
                            #it is added to it, otherwise its value is incremented by one.
                            if pix[x,y] in colors:
                                colors[pix[x,y]] = colors[pix[x,y]] + 1
                            else:
                                colors[pix[x,y]] = 1
            #The "same_color_top" list mirrors the "same_color_side" list and gathers the successive
            #aggregated pixels of same color on the "y" axis of the pixelated image, further separating
            #a given column into "row chunks" every time the pixel equivalent of "nonogram_cells" is
            #reached. Here the "colors" dictionary doesn't need to be generated again, as it has already
            #cycled through every aggregated pixel on the "x" axis and thus already contains every color
            #found in the pixelated image.
            same_color_top = []
            for x in range (math.floor(pixel_size/2), width, pixel_size):
                same_color_top.append([])
                for y in range(math.floor(pixel_size/2), height, pixel_size):
                    if y == math.floor(pixel_size/2) or (y-math.floor(pixel_size/2))%(nonogram_cells*pixel_size) == 0:
                        same_color_top[-1].append([])
                    else:
                        if same_color_top[-1][-1] == []:
                            if pix[x, y] == pix[x, y-pixel_size]:
                                same_color_top[-1][-1].append([2, pix[x,y]])
                            else:
                                same_color_top[-1][-1].append([1, pix[x,y-pixel_size]])
                                same_color_top[-1][-1].append([1, pix[x,y]])
                        elif len(same_color_top[-1][-1]) > 0 and pix[x, y] == pix[x, y-pixel_size]:
                            same_color_top[-1][-1][-1] = [same_color_top[-1][-1][-1][0]+1, same_color_top[-1][-1][-1][1]]
                        elif len(same_color_top[-1][-1]) > 0 and pix[x, y] != pix[x, y-pixel_size]:
                            same_color_top[-1][-1].append([1, pix[x,y]])

            #The "get_background()" function instantiates a new Image object from a blank JPEG file
            #of the selected dimensions (A4 if "A4" was passed in as an additional argument when
            #running the code, US Letter otherwise), at a resolution of 300 ppi. The "side" variable
            #keeps track of whether the clues for the side panel are being drawn. If so, the landscape
            #canvas needs to be rotated, as the numbers need to be drawn in portrait format to be
            #displayed right side up then placed adjacently to the nonogram grid.
            def get_background(A4, A4_margin, side):
                if A4 and side:
                    background_img = Image.open(os.path.join(cwd, "A4_blank_canvas.jpg")).rotate(270, expand = True)
                    #The "A4_margin" variable adds 25 pixels to the "y" coordinate
                    #where the puzzle title will be written on the clue pages, when
                    #generated in A4 format, to account for the greater height of
                    #an A4 page versus a US letter page.
                    A4_margin = 25
                    A4_margin = 0
                elif A4:
                    background_img = Image.open(os.path.join(cwd, "A4_blank_canvas.jpg"))
                    A4_margin = 25
                    A4_margin = 0
                elif not A4 and side:
                    background_img = Image.open(os.path.join(cwd, "US_letter_blank_canvas.jpg")).rotate(270, expand = True)
                elif not A4:
                    background_img = Image.open(os.path.join(cwd, "US_letter_blank_canvas.jpg"))

                background_img_width, background_img_height = background_img.size
                return background_img, background_img_width, background_img_height, A4_margin

            side = True
            background_img, background_img_width, background_img_height, A4_margin = get_background(A4, A4_margin, side)

            #All of the paths of the 1 x 1 plate scans stored in the "1 x 1 plate scans" are stored in the
            #"color_files" list. The file names are extracted from the paths and stored in the "color_file_names" list.
            path_colors = os.path.join(cwd, "1 x 1 plate scans", "*.jpg")
            color_files = glob.glob(path_colors)
            color_file_names = [color_files[i][:color_files[i].index(")") + 1].replace("\\", "/").split("/")[-1].strip() for i in range(len(color_files))]

            #The available horizontal space for the lego image is set as the width of the
            #"background_image" canvas, minus two times the equivalent of 0.75 inch margin
            #(2*225 px).
            available_horizontal_space_for_lego_image = background_img_width - 450
            #The top of the "lego mosaic" image will be at 454 px on the "y" axis in order
            #to line it up with the other image on the title page, which starts at the same point.
            available_vertical_space_for_lego_image = background_img_height - 454

            number_of_vertical_pixels = len(same_color_side)
            #The number of vertical studs in the "lego mosaic" is determined by
            #cycling through all of the elements of same_color_side[0], which
            #make up the different horizontal nonogram grids contained within the
            #first row, and then adding up the counts for each colors, including
            #the blanks.
            number_of_horizontal_pixels = 0
            for j in range(len(same_color_side[0])):
                for k in range(len(same_color_side[0][j])):
                    number_of_horizontal_pixels += same_color_side[0][j][k][0]

            #The number of actual vertical pixels per stud in the "lego mosaic" is determined
            #by dividing the "available_vertical_space_for_lego_image" by the number
            #of studs (aggregated pixels) in the vertical dimension ("number_of_vertical_pixels").
            #The same is done for the horizontal pixels, and the minimum of the two is
            #selected as the pixel size of an individual stud of the "lego mosaic" image.
            lego_pixel_size = math.floor(min([available_vertical_space_for_lego_image/number_of_vertical_pixels,
            available_horizontal_space_for_lego_image/number_of_horizontal_pixels]))

            #If the "lego_pixel_size" is superior to the available space in either dimension, its size is
            #decremented by one pixel until the full "lego mosaic" fits on the page.
            while not (number_of_horizontal_pixels * lego_pixel_size <= available_horizontal_space_for_lego_image and
            number_of_vertical_pixels * lego_pixel_size <= available_vertical_space_for_lego_image):
                lego_pixel_size -= 1

            #The horizontal and vertical pixel size of the "lego mosaic" are calculated using the
            #updated "lego_pixel_size".
            lego_image_horizontal_size = math.floor(number_of_horizontal_pixels * lego_pixel_size)
            lego_image_vertical_size = math.floor(number_of_vertical_pixels * lego_pixel_size)

            #The "x" coordinate at which the "lego mosaic" image will start being drawn is
            #set as the "perforations_margin", plus the difference in-between the center point of
            #the "blank_canvas_width" and of the "lego_image_horizontal_size".
            lego_starting_x = perforations_margin + math.floor((available_horizontal_space_for_lego_image - lego_image_horizontal_size)/2)

            #A dictionary of Pillow "Image" objects values is created for each of the
            #different RGB values (keys in the dictionary) for the colors making up the
            #"lego mosaic".
            color_images_dict = dict()
            for color in colors:
                for j in range(len(color_file_names)):
                    #The scans of the 1x1 plates are named after
                    #their RGB values, so all the colors of the
                    #image are screened against those present in the
                    #"1 x 1 plate scans" folder, and the matches are
                    #added to the "color_images_dict" dictionary.
                    if str(color) == color_file_names[j]:
                        color_image = eval("color")
                        color_images_dict[color_image] = (Image.open(color_files[j])
                        .resize((lego_pixel_size, lego_pixel_size)))

            #The "background_img_editable" instantiation of the "Draw" class will allow
            #to modify the background image by overlaying it with the text boxes.)
            background_img_editable = ImageDraw.Draw(background_img)

            #The variable "color_transition_threshold" stores the maximal number of clue squares that fit on one
            #row that spans the width of the page (in A4 or US Letter) format, after removing the pixels corresponding
            #to the perforations margin on one side of the page and the non printable margin on the other.
            color_transition_threshold = math.floor((background_img_width - perforations_margin - non_printable_area_margin)/stud_pixels)

            problematic_rows = []
            #The blank color for each nonogram grid making up the "lego mosaic"
            #will be determined in order to be able to later on assess whether
            #there are too many color transitions when excluding the blanks.
            if auto_blanks:
                #The "auto_blanks_grid_blanks" dictionary will store
                #the blank for each of the nonogram grids, using the
                #"j" and "k" baseplate row and baseplate column indices,
                #respectively as the keys and the RGB tuples of the blanks
                #as the values. Note that when accessing the "auto_blanks_grid_blanks"
                #dictionary within a "for" loop cycling through "same_color_top":, the
                #"j" and "k" indices will be reversed, as this list is
                #mirrored with respect to "same_color_side".
                auto_blanks_grid_blanks = dict()
                row_number_in_mosaic = 0
                #The "for j in range(math.ceil(len(same_color_side)/nonogram_cells))" allows
                #to loop over every different basplate row ("row chunks"). The "current_array"
                #simply slices the "same_color_side" array according to the current "j" index.
                #For example, the first "j" index of zero results in the slice to be as follows:
                #"same_color_side[0:0+32]". #A "deepcopy" is made here as some successive
                #same-colored 1 x 1 plate counts will be overwritten later on when flattening
                #the list. This will prevent also modifying the original "same_color_side" list.
                #Similarly, the "for k in range(math.ceil(width/pixel_size/nonogram_cells))"
                #loop loops over all of the different baseplate columns ("column chunks").
                for j in range(math.ceil(len(same_color_side)/nonogram_cells)):
                    current_array = copy.deepcopy(same_color_side[j*nonogram_cells: j*nonogram_cells + nonogram_cells])
                    for k in range(math.ceil(width/pixel_size/nonogram_cells)):
                        #The "colors_grayscale" list will store the flattened successive same-colored 1 x 1 plates
                        #found within the current nonogram grid ("current_array[k]"), preceded by their grayscale
                        #value. The format will be "[grayscale value, [number of successive same-colored 1 x 1 plates, (RGB tuple)]]".
                        #The list is sorted according to the RGB tuples to group the same-colored 1 x 1 plates occuring
                        #thoughout the nonogram grid together. This will allow to add up the total amount of same-colored
                        #1 x 1 plates throughout the nonogram grid and determine the blank based on the "auto_blanks_threshold".
                        colors_grayscale = sorted([[math.floor((current_array[line_index][k][element_index][1][0] +
                        current_array[line_index][k][element_index][1][1] + current_array[line_index][k][element_index][1][2])/3),
                        current_array[line_index][k][element_index]] for line_index in range(len(current_array))
                        for element_index in range(len(current_array[line_index][k]))], key = lambda x:x[1][1])

                        #The "number_grid_colors" list will "add up" the counts of same-colored 1 x 1 plates, and
                        #in order to get the total number of same-colored 1 x 1 plates throughout the nonogram grid.
                        #This will allow to determine the blank in the sorted list along the grayscale values.
                        number_grid_colors = []
                        for l in range(len(colors_grayscale)):
                            if l == 0 or colors_grayscale[l][1][1] != colors_grayscale[l-1][1][1]:
                                number_grid_colors.append(colors_grayscale[l])
                            elif colors_grayscale[l][1][1] == colors_grayscale[l-1][1][1]:
                                number_grid_colors[-1][1][0] += colors_grayscale[l][1][0]
                        #The "sorted_grid_colors" is sorted along the grayscale values in reverse order, so as
                        #to cycle through this list from the palest color to the darkest one, and select the
                        #color that has a number of 1 x 1 plates at least equal to the "color_transition_threshold"
                        #times the number of studs in the nonogram grid ("if sorted_grid_colors[l][1][0] >=
                        #math.ceil(nonogram_cells*nonogram_cells*auto_blanks_threshold)").
                        sorted_grid_colors = sorted(number_grid_colors, key = lambda x:x[0], reverse = True)
                        for l in range(len(sorted_grid_colors)):
                            if sorted_grid_colors[l][1][0] >= math.ceil(nonogram_cells*nonogram_cells*auto_blanks_threshold):
                                blank_tuple = sorted_grid_colors[l][1][1]
                                blank = str(blank_tuple)
                                auto_blanks_grid_blanks[str(j) + ", " + str(k)] = [blank, blank_tuple]
                                break
                            #Upon reaching the end of the "sorted_grid_colors" list, if no color had a sufficient
                            #number of 1 x 1 plate to meet the "color_transition_threshold", an error message
                            #is displayed.
                            elif l == len(sorted_grid_colors)-1:
                                sorted_grid_colors.sort(key = lambda x:x[1][0], reverse = True)
                                sys.exit('There is a maximum of ' + str(sorted_grid_colors[0][1][0]) +
                                ' one by one plates of the folowing RGB value ' + str(sorted_grid_colors[0][1][1]) +
                                ' in the baseplate row number ' + str(j+1) + ' and baseplate column number ' + str(k+1) +
                                ". This represents a blank percentage of " +
                                str(round(sorted_grid_colors[0][1][0]/(nonogram_cells*nonogram_cells)*100, 1)) +
                                '%, while your specified minimum proportion of one by one plates of the blank was set to ' +
                                str(round(auto_blanks_threshold*100, 1)) + "%. Please select a lower threshold.")
                        #This "for" loop appends the problematic lines that have too many color transitions to
                        #have all of their clues printed out on the clue sheets to the "problematic_rows" list.
                        row_number_in_mosaic = j*nonogram_cells
                        for l in range(len(current_array)):
                            row_number_in_mosaic += 1
                            number_of_color_transitions = len([element for element in current_array[l][k] if element[1] != blank_tuple])
                            #If a problematic line has been detected, its location and "number_of_color_transitions"
                            #will be appended to "problematic_rows".
                            if number_of_color_transitions > color_transition_threshold:
                                problematic_rows.append([row_number_in_mosaic, j+1, l+1, k+1, number_of_color_transitions])
            #A similar procedure will be done here, where the
            #blank is the same for all of the nonogram grids
            #making up the "lego mosaic".
            else:
                current_baseplate_row = 0
                current_y_index = 1
                #The "current_baseplate_row" variable keeps track of the which base plate row the
                #current "j" index is at in the pixelated image. The current_y index keeps tabs on
                #the curent row index within that baseplate. These, along with the "column chunk"
                #index "k", will facilitate locating problematic rows having a number of color
                #inflection points in excess of the "color_transition_threshold" in the pixelated
                #image in order to simplify it.
                for j in range(len(same_color_side)):
                    if j % nonogram_cells == 0:
                        current_baseplate_row += 1
                        current_y_index = 1
                    else:
                        current_y_index += 1
                    for k in range(len(same_color_side[j])):
                        #The number of transitions corresponds to the total number of
                        #successive same-colored aggregated pixels in a given "column chunk"
                        #of a row of the pixelated image, should the "no_blanks" argument
                        #have been passed in. Otherwise, only the colors different from the
                        #blank will be included when determining that number.
                        if no_blanks == True:
                            number_of_color_transitions = len(same_color_side[j][k])
                        else:
                            number_of_color_transitions = len([element for element in same_color_side[j][k] if element[1] != blank_tuple])
                        #If a problematic line has been detected, its location and "number_of_color_transitions"
                        #will be appended to "problematic_rows".
                        if number_of_color_transitions > color_transition_threshold:
                            problematic_rows.append([j+1, current_baseplate_row, current_y_index, k+1, number_of_color_transitions])

            #A similar approach is used for the "problematic_columns"
            problematic_columns = []
            if auto_blanks:
                for j in range(math.ceil(len(same_color_top)/nonogram_cells)):
                    current_array = same_color_top[j*nonogram_cells: j*nonogram_cells + nonogram_cells]
                    for k in range(math.ceil(width/pixel_size/nonogram_cells)):
                        column_number_in_mosaic = j*nonogram_cells
                        for l in range(len(current_array)):
                            #Note that when accessing the "auto_blanks_grid_blanks"
                            #dictionary within a "for" loop cycling through "same_color_top":, the
                            #"j" and "k" indices will be reversed, as this list is
                            #mirrored with respect to "same_color_side".
                            blank_tuple = auto_blanks_grid_blanks[str(k) + ", " + str(j)][1]
                            column_number_in_mosaic += 1
                            number_of_color_transitions = len([element for element in current_array[l][k] if element[1] != blank_tuple])
                            #If a problematic line has been detected, its location and "number_of_color_transitions"
                            #will be appended to "problematic_rows".
                            if number_of_color_transitions > color_transition_threshold:
                                problematic_rows.append([column_number_in_mosaic, j+1, l+1, k+1, number_of_color_transitions])

            else:
                current_baseplate_column = 0
                current_x_index = 1
                for j in range(len(same_color_top)):
                    if j % nonogram_cells == 0:
                        current_baseplate_column += 1
                        current_x_index = 1
                    else:
                        current_x_index += 1
                    for k in range(len(same_color_top[j])):
                        if no_blanks == True:
                            number_of_color_transitions = len(same_color_top[j][k])
                        else:
                            number_of_color_transitions = len([element for element in same_color_top[j][k] if element[1] != blank_tuple])
                        if number_of_color_transitions > color_transition_threshold:
                            problematic_columns.append([j+1, current_baseplate_column, current_x_index, k+1, number_of_color_transitions])

            #Should there be any rows or columns of which the number of successive same-colored
            #aggregated pixels in any given "column chunk" or "row chunk" exceed "color_transition_threshold",
            #you will be notified of their location within the pixelated image, so that you could reduce the
            #number of color inflections at those positions.
            if problematic_rows or problematic_columns:
                print("\n\nA problem has arisen while processing your image: " + image_name + ":")
                if problematic_rows:
                    print('\nThe following rows (given as the stud row numbers in the mosaic, ' +
                    'followed by the baseplate row numbers and the row numbers in those baseplates) have a number of color ' +
                    'transitions (excluding the blanks) above the maximal amount of ' + str(color_transition_threshold) +
                    ' that fit on a page.')

                    for j in range(len(problematic_rows)):
                        print("\n- Mosaic stud row number " + str(problematic_rows[j][0]) +
                        " (baseplate row number " + str(problematic_rows[j][1]) + ", row number " +
                        str(problematic_rows[j][2]) + " in the basplate, baseplate column number " +
                        str(problematic_rows[j][3]) + ") has a total of " + str(problematic_rows[j][4]) +
                        " color transitions.")

                if problematic_columns:
                    print('\nThe following columns (given as the stud column numbers in the mosaic, ' +
                    'followed by the baseplate column numbers and the column numbers in those baseplates) have a number of color ' +
                    'transitions (excluding the blanks) above the maximal amount of ' + str(color_transition_threshold) +
                    ' that fit on a page.')

                    for j in range(len(problematic_columns)):
                        print("\n- Mosaic stud column number " + str(problematic_columns[j][0]) +
                        " (baseplate column number " + str(problematic_columns[j][1]) + ", column number " +
                        str(problematic_columns[j][2]) + " in the baseplate, baseplate row number " +
                        str(problematic_columns[j][3]) + ") has a total of " + str(problematic_columns[j][4]) +
                        " color transitions.")

                sys.exit('\nPlease simplify your image and try again.\n')


            #The "paste_plate" function instantiates an Image object corresponding to
            #a 1x1 vectorized image, then draws a polygon corresponding to its outline
            #on "background_img_editable" with a fill equivalent to "color" and then
            #pastes the plate image on top of it using itself as a mask to allow the
            #background color to show through.
            def paste_plate(x, y, color, background_img, background_img_editable):
                plate_image = Image.open("one by one plate.png").convert("RGBA")
                background_img_editable.polygon([(x + 56, y + 0), (x + 1, y + 33),
                (x + 1, y + 47), (x + 46, y + 89), (x + 101, y +57), (x + 101, y + 43)],
                fill = color, outline = color)
                background_img.paste(plate_image, (x,y), mask=plate_image)
                return background_img, background_img_editable

            #At his point of the code, for the first image only, the "create_cover_page"
            #function creates a cover page for both PDF documents "side_panel_pdf_name"
            #and "top_panel_pdf_name". It takes in a "color_list" corresponding to a
            #list of RGB values that will be used to draw a border of 1x1 plates of various
            #colors, which differ for the two PDF documents.

            def get_text_font_size(font, string):
                string_box = font.getbbox(string)
                string_size = [math.floor((string_box[2]-string_box[0])),
                math.floor((string_box[3]-string_box[1]))]
                string_length = string_size[0]
                string_height = string_size[1]
                return string_length, string_height

            def create_cover_page(A4, color_list, non_printable_area_margin, background_img,
            background_img_editable, background_img_width, background_img_height, text_string,
            cover_page_heading_font, cover_page_heading_font_size, cover_page_subtitle_font,
            cover_page_subtitle_font_size):
                #The "side_index" variable will keep track of the current side when
                #drawing the 1x1 border around the page, starting with the left vertical
                #side and proceeding counterclockwise.
                side_index = 0
                #The starting "x,y" coordinates vary sligthly depending on whether the
                #PDF document is generated in A4 or US Letter format, which differ in size.
                if not A4:
                    x, y = non_printable_area_margin + 150, non_printable_area_margin + 247
                    A4_modifyer = 0
                else:
                    x, y = non_printable_area_margin + 100, non_printable_area_margin + 275
                    A4_modifyer = 50
                #The "x_increment" and "y_increment" will move counterclockwise around
                #the page when drawing the 1x1 border.
                x_increment = 200
                y_increment = 170
                while side_index < 4:
                    for color in color_list:
                        background_img, background_img_editable = paste_plate(x, y,
                        color, background_img, background_img_editable)
                        #The various "if" and "elif" statements will determine
                        #where the next 1x1 is to be drawn on the canvas, depending
                        #on the current side ("side_index"), and the available room
                        #left on the page on that side.
                        if side_index == 0:
                            if (y + y_increment <= background_img_height -
                            (y_increment + non_printable_area_margin)):
                                y += y_increment
                            else:
                                side_index += 1
                                x += x_increment
                        elif side_index == 1:
                            if (x + x_increment <= background_img_width -
                            (x_increment + non_printable_area_margin)):
                                x += x_increment
                            else:
                                side_index += 1
                                y -= y_increment
                        elif side_index == 2:
                            if y + y_increment >= non_printable_area_margin + 250 + A4_modifyer:
                                y -= y_increment
                            else:
                                side_index += 1
                                x -= x_increment
                        elif side_index == 3:
                            if x - x_increment >= non_printable_area_margin:
                                x -= x_increment
                            else:
                                side_index += 1
                                break

                #The next two "while" loops automatically adjust the size of the
                #cover page heading and subtitle so that they fit within the
                #border of 1x1 plates.

                #The cover heading is automatically resized horizontally.
                string_length, string_height = get_text_font_size(cover_page_heading_font,
                cover_page_heading_string)
                #The available horizontal space in-between two opposing 1x1 plates in
                #the border was determined to be 1500, when a little buffer was included
                #so as to prevent the text to be cramped.
                available_horizontal_space_for_text = 1500
                while True:
                    cover_page_heading_length, cover_page_heading_height = get_text_font_size(cover_page_heading_font,
                    cover_page_heading_string)
                    if (cover_page_heading_length > available_horizontal_space_for_text):
                        cover_page_heading_font_size -= 1
                        cover_page_heading_font = ImageFont.truetype(cover_page_heading_font_files[0],
                        cover_page_heading_font_size)
                    else:
                        break
                cover_page_heading_font = ImageFont.truetype(cover_page_heading_font_files[0],
                cover_page_heading_font_size)

                #The cover page subtitle is automatically resized horizontally.
                string_length, string_height = get_text_font_size(cover_page_subtitle_font,
                side_cover_page_subtitle_string)
                while True:
                    cover_page_subtitle_length, cover_page_subtitle_height = get_text_font_size(cover_page_subtitle_font,
                    side_cover_page_subtitle_string)
                    if (cover_page_subtitle_length > available_horizontal_space_for_text):
                        cover_page_subtitle_font_size -= 1
                        cover_page_subtitle_font = ImageFont.truetype(cover_page_subtitle_font_files[0], cover_page_subtitle_font_size)
                    else:
                        break

                #Should the fonts used for the cover page heading and subtitle be the same, they would then both
                #be set to the lowest font size between the two, as differently sized text of the same font would
                #look strange.
                cover_page_heading_font_name = ("".join(cover_page_heading_font_files[0]
                .split(".")[:-1]).replace("\\", "/").split("/")[-1])
                cover_page_subtitle_font_name = ("".join(cover_page_subtitle_font_files[0]
                .split(".")[:-1]).replace("\\", "/").split("/")[-1])

                if cover_page_heading_font_name == cover_page_subtitle_font_name:
                    cover_page_heading_font_size = min([cover_page_heading_font_size,
                    cover_page_subtitle_font_size])
                    cover_page_heading_font = ImageFont.truetype(cover_page_heading_font_files[0],
                    cover_page_heading_font_size)
                    cover_page_subtitle_font_size = cover_page_heading_font_size
                #Similarly, if the height of the subtitle is greater than that of the heading, its
                #font size will be decremented until it reaches the height of the heading.
                else:
                    #The function "get_heading_height()" creates an image of the text string's bounding box
                    #dimensions and then writes the string on it. It then assembles the "y" coordinates
                    #of the black pixels within the image in the "string_color_transitions_y" list, which
                    #is afterwards sorted to allow to determine the actual string height by subtracting
                    #the first "y" coordinate from the last one.
                    def get_heading_height(font_name, string, string_length, string_height):
                        string_image = Image.new("RGB", (string_length, string_height), (255,255,255))
                        string_image_editable = ImageDraw.Draw(string_image)
                        string_image_editable.text((math.floor(string_length/2), 0),
                        string, fill="Black", font=font_name, anchor="ms")
                        pix = string_image.load()

                        string_color_transitions_y = ([y for x in range(string_length)
                        for y in range(string_height) if pix[x,y] == (0,0,0)])
                        string_color_transitions_y.sort()

                        return string_color_transitions_y[-1]-string_color_transitions_y[0]

                    actual_heading_height = get_heading_height(cover_page_heading_font, cover_page_heading_string,
                    cover_page_heading_length, cover_page_heading_height)
                    actual_subtitle_height = get_heading_height(cover_page_subtitle_font, cover_page_heading_string,
                    cover_page_heading_length, cover_page_heading_height)

                    #Should the "actual_subtitle_height" be greater than the "actual_heading_height",
                    #then it means that the font size of the subtitle needs to be decreased until it
                    #reaches the height of the heading.
                    if actual_subtitle_height > actual_heading_height:

                        while actual_subtitle_height > actual_heading_height:
                            if actual_subtitle_height > actual_heading_height:
                                #Since this "while" loop is computationally
                                #costly, with the "get_heading_height()" function
                                #creating an image and cycling through all its
                                #pixels, the step of the decrementation is set
                                #to five instead of one, and the results seem
                                #adequate, with much better run times.
                                cover_page_subtitle_font_size -= 5
                                cover_page_subtitle_font = ImageFont.truetype(cover_page_subtitle_font_files[0], cover_page_subtitle_font_size)
                                actual_subtitle_height = get_heading_height(cover_page_subtitle_font, cover_page_heading_string,
                                cover_page_heading_length, cover_page_heading_height)

                cover_page_subtitle_font = ImageFont.truetype(cover_page_subtitle_font_files[0], cover_page_subtitle_font_size)

                #The title "cover_page_heading_string" is centered on the "x" axis
                #and written on the third of the page height.
                title_x = math.floor(background_img_width/2)
                title_y = math.floor(background_img_height/3)
                background_img_editable.text((title_x, title_y), cover_page_heading_string,
                font=cover_page_heading_font, anchor="ms", fill="Black")

                #The height of the title will be used to walk down the page
                #to a point where a 1x1 divider will be drawn in-between
                #the title and the subtitle "text_string".
                string_box = cover_page_heading_font.getbbox(cover_page_heading_string)
                string_size = [math.floor((string_box[2]-string_box[0])),
                math.floor((string_box[3]-string_box[1]))]
                string_half_height = math.floor(string_size[1]/2)

                #The four 1x1 divider are drawn here using the same "color_list"
                #that was used to draw the border, each being separated by 200
                #pixels horizontally.
                x = math.floor((background_img_width-600)/2)-50
                y = title_y + math.floor(title_y/2) - string_half_height
                for j in range(4):
                    background_img, background_img_editable = paste_plate(x, y,
                    color_list[j], background_img, background_img_editable)
                    x += 200

                #The "text_string" is written two thirds the way down the page
                #("2*title_y", "title_y" being  "math.floor(background_img_height/3)").
                y = 2*title_y
                background_img_editable.text((title_x, y), text_string,
                font=cover_page_subtitle_font, anchor="ms", fill="Black")
                return background_img, background_img_editable, cover_page_heading_font_size, string_size[0]


                #A background image needs to be created with  the "get_background()" function,
                #before it gets passed into the "create_cover_page()" function.
                background_img, background_img_width, background_img_height, A4_margin = get_background(A4, A4_margin, side)
                background_img = background_img
                background_img_editable = ImageDraw.Draw(background_img)

            background_img, background_img_editable, cover_page_heading_font_size, cover_page_heading_width = create_cover_page(A4,
            [(228, 176, 74), (255, 255, 255), (161, 165, 168), (107, 110, 104)],
            non_printable_area_margin, background_img, background_img_editable,
            background_img_width, background_img_height, side_cover_page_subtitle_string,
            cover_page_heading_font, cover_page_heading_font_size,
            cover_page_subtitle_font, cover_page_subtitle_font_size)

            #Once the cover page is assembled, it is saved as a PDF document and will
            #constitute the first page of the document, to which the next "Side Panel Clue"
            #pages get appended to.
            background_img.save(os.path.join(cwd, "Images", image_name, image_name + side_panel_pdf_name),
            quality=100, resolution=300)

            #A similar approach is taken for the "top_cover_page_subtitle_string".
            background_img, background_img_width, background_img_height, A4_margin = get_background(A4, A4_margin, side)
            background_img = background_img
            background_img_editable = ImageDraw.Draw(background_img)

            background_img, background_img_editable, cover_page_heading_font_size, cover_page_heading_width = create_cover_page(A4,
            [(74, 126, 228), (255, 255, 255), (161, 165, 168), (107, 110, 104)],
            non_printable_area_margin, background_img, background_img_editable,
            background_img_width, background_img_height, top_cover_page_subtitle_string,
            cover_page_heading_font, cover_page_heading_font_size,
            cover_page_subtitle_font, cover_page_subtitle_font_size)

            background_img.save(os.path.join(cwd, "Images", image_name, image_name + top_panel_pdf_name),
            quality=100, resolution=300)

            #The title page heading text is automatically resized horizontally in the "while" loop.
            #The longest string between the title page and cover page's headers is selected to calculate
            #the "title_page_heading_font_size", as it is assumed that the cover page heading will only
            #be the plural form of the title page's heading ("Nonogram Puzzles" vs "Nonogram Puzzle").
            if len(cover_page_heading_string) > len(title_page_heading_string):
                string_length, string_height = get_text_font_size(title_page_heading_font,
                cover_page_heading_string)
            else:
                string_length, string_height = get_text_font_size(title_page_heading_font,
                title_page_heading_string)
            #The 600 is to account for the space taken up by the 1 x 1 plates and the spacers
            #in-between them and the heading text.
            available_horizontal_space_for_text = (background_img_width -
            perforations_margin - non_printable_area_margin - 600)
            while True:
                string_length, string_height = get_text_font_size(title_page_heading_font,
                cover_page_heading_string)
                if (string_length > available_horizontal_space_for_text or
                string_length > cover_page_heading_width):
                    title_page_heading_font_size -= 1
                    title_page_heading_font = ImageFont.truetype(title_page_heading_font_files[0],
                    title_page_heading_font_size)
                else:
                    break
            #The "title_page_heading_font" is updated.
            title_page_heading_font = ImageFont.truetype(title_page_heading_font_files[0],
            title_page_heading_font_size)

            #The longest string of body text is automatically resized horizontally
            #in the "while" loop. The list "title_page_text_strings" is sorted according
            #to the string lengths and the longest string is selected in order to determine
            #the "title_page_text_font_size". The strings that are compared in length will
            #depend on what type of blanks are included in the puzzles ("auto_blanks", "no_blanks"
            #or the standard lightest color used as a blank for all the nonogram grids of a
            #given mosaic).
            if auto_blanks == True:
                title_page_text_strings = [[len(title_page_materials_string), title_page_materials_string],
                [len(title_page_auto_blanks_string), title_page_auto_blanks_string]]

            elif no_blanks == True:
                title_page_text_strings = [[len(title_page_materials_string), title_page_materials_string],
                [len(title_page_no_blanks_string), title_page_no_blanks_string]]

            else:
                title_page_text_strings = [[len(title_page_materials_string), title_page_materials_string],
                [len(title_page_blank_string), title_page_blank_string]]

            title_page_text_strings.sort(key = lambda x:x[0])

            longest_title_page_text_string = title_page_text_strings[-1][1]

            string_length, string_height = get_text_font_size(title_page_text_font,
            longest_title_page_text_string)

            available_horizontal_space_for_text = (background_img_width -
            perforations_margin - non_printable_area_margin)
            while True:
                string_length, string_height = get_text_font_size(title_page_text_font,
                longest_title_page_text_string)
                if (string_length > available_horizontal_space_for_text):
                    title_page_text_font_size -= 1
                    title_page_text_font = ImageFont.truetype(title_page_text_font_files[0], title_page_text_font_size)
                else:
                    break

            #The "title_font" ImageFont instantiation takes is done here in case
            #the title didn't need to be resized.
            title_page_text_font = ImageFont.truetype(title_page_text_font_files[0], title_page_text_font_size)

            #Here a verification is made as to whether the "title_page_blank_string" or
            # is not in fact the longest string on the title page when factoring in the
            #space taken by the 1x1 plate that is pasted onto the image after it.
            #A separate "if" statement is used here as the measurements of the blank
            #string needs to be determined in order to paste the 1x1 plate later on
            #in the code, whether or not string is the longest one on the title page.
            if blank:
                title_page_blank_string_length, title_page_blank_string_height = get_text_font_size(title_page_text_font,
                title_page_blank_string)
            if not no_blanks and title_page_blank_string_length + 150 > title_page_text_strings[-1][0]:
                longest_title_page_text_string = title_page_blank_string
                #The "150" pixels accounts for the presence of a spacer and the pasted 1x1 plate image.
                available_horizontal_space_for_text = (background_img_width -
                perforations_margin - non_printable_area_margin - 150)

                while True:
                    string_length, string_height = get_text_font_size(title_page_text_font,
                    longest_title_page_text_string)
                    if (string_length > available_horizontal_space_for_text):
                        title_page_text_font_size -= 1
                        title_page_text_font = ImageFont.truetype(title_page_text_font_files[0], title_page_text_font_size)
                    else:
                        break
                title_page_blank_string_length, title_page_blank_string_height = get_text_font_size(title_page_text_font,
                title_page_blank_string)

            #In order to ensure proper spacing and for all of the rows to be
            #displayed on the page, a sample title string is automatically
            #resized horizontally and vertically in the "while" loop.
            string_length, string_height = get_text_font_size(title_font,
            image_name + " (" + top_string + ", " + row_string + " 10, " + column_string + " 10)")
            #The "-150" accounts for the number of pixels taken up by
            #the pasted 1 x 1 plate depicting the blank color, in the
            #upper left corner of the clue sheets.
            available_horizontal_space_for_text = (background_img_width -
            perforations_margin - non_printable_area_margin - 150)
            #The "available_vertical_space_for_text" describes the
            #available vertical space for the title, which is the total
            #height of the canvas ("background_img_height"), minus the
            #non-printable margins at the top and bottom of the page,
            #the space taken up by up to 32 clue boxes and the 60-pixel
            #spacer in-between the "y" coordinate directly below the
            #title text and the start of the first clue box.
            available_vertical_space_for_text = (background_img_height -
            (2*non_printable_area_margin + 60 + 32*stud_pixels))
            while True:
                string_length, string_height = get_text_font_size(title_font,
                image_name + " (" + top_string + ", " + row_string + " 10, " + column_string + " 10)")
                if (string_height > available_vertical_space_for_text or
                string_length > available_horizontal_space_for_text):
                    title_font_size -= 1
                    title_font = ImageFont.truetype(title_font_files[0], title_font_size)
                else:
                    break
            #The "title_font" ImageFont instantiation takes is done here in case
            #the title didn't need to be resized.
            title_font = ImageFont.truetype(title_font_files[0], title_font_size)

            #The longest string of body text is automatically resized horizontally
            #in the "while" loop.
            string_length, string_height = get_text_font_size(numbers_font, "32")
            while True:
                string_length, string_height = get_text_font_size(numbers_font, "32")
                available_space = math.floor(0.85*stud_pixels)

                if string_length > available_space or string_height > available_space:
                    numbers_font_size -= 1
                    numbers_font = ImageFont.truetype(numbers_font_files[0], numbers_font_size)
                else:
                    break
            numbers_font = ImageFont.truetype(numbers_font_files[0], numbers_font_size)

            def calculate_correction_pixels(stud_pixels, numbers_font, string):
                string_length, string_height = get_text_font_size(numbers_font, string)

                number_image = Image.new("RGB", (stud_pixels, stud_pixels), (255,255,255))
                number_image_editable = ImageDraw.Draw(number_image)
                number_image_editable.text((math.floor(stud_pixels/2),
                math.floor(stud_pixels/2)), string, fill="Black",
                font=numbers_font, anchor="mm", stroke_width=3, stroke_fill="Black")
                pix = number_image.load()

                center = math.floor(stud_pixels/2 - string_height/2)

                number_color_transitions_x = [x for y in range(stud_pixels)
                for x in range(stud_pixels) if pix[x,y] == (0,0,0)]
                number_color_transitions_x.sort()

                starting_x_pixel = number_color_transitions_x[0]
                starting_x_pixel_reverse = stud_pixels - number_color_transitions_x[-1]

                x_pixel_adjustment = math.floor((starting_x_pixel_reverse - starting_x_pixel)/2)

                number_color_transitions_y = ([y for x in range(stud_pixels)
                for y in range(stud_pixels) if pix[x,y] == (0,0,0)])
                number_color_transitions_y.sort()

                starting_y_pixel = number_color_transitions_y[0]
                starting_y_pixel_reverse = stud_pixels - number_color_transitions_y[-1]

                y_pixel_adjustment = math.floor((starting_y_pixel_reverse - starting_y_pixel)/2)

                return x_pixel_adjustment, y_pixel_adjustment

            x_pixel_adjustment_double_digit, y_pixel_adjustment_double_digit = calculate_correction_pixels(stud_pixels, numbers_font, "32")
            x_pixel_adjustment_single_digit, y_pixel_adjustment_single_digit = calculate_correction_pixels(stud_pixels, numbers_font, "3")

            #Another background image is generated to create the title page.
            background_img, background_img_width, background_img_height, A4_margin = get_background(A4, A4_margin, side)
            background_img_editable = ImageDraw.Draw(background_img)

            title_x = math.floor(background_img_width/2)
            background_img_editable.text((title_x,225), title_page_heading_string,
            font=title_page_heading_font, anchor="mm", fill="Black")

            string_box = title_page_heading_font.getbbox(title_page_heading_string)
            string_size = [math.floor((string_box[2]-string_box[0])),
            math.floor((string_box[3]-string_box[1]))]
            string_half_length = math.floor(string_size[0]/2)
            string_half_height = math.floor(string_size[1]/2)

            #Two 1x1 plate images are pasted on either side of the "title_page_heading_string" heading.

            #For the 1x1 plate on the left side, an extra hundred pixels are
            #subtracted from the "x" coordinate, in order to factor in the
            #width of the 1 x 1 plate image itself
            background_img, background_img_editable = paste_plate(title_x -
            string_half_length - 100 - 100, 175, (255,255,255), background_img,
            background_img_editable)

            background_img, background_img_editable = paste_plate(title_x +
            string_half_length + 100, 175, (160, 165, 169), background_img,
            background_img_editable)

            #The "lego_initial_starting_y" sets the "y" coordinate
            #of the top of the "lego mosaic" image, such that it lines up with
            #the "y" coordinate at which the other image starts on the title page
            #(405 px is used instead of 375 to line them up).
            lego_initial_starting_y = 405 + string_half_height - 30
            lego_starting_y = lego_initial_starting_y
            lego_initial_starting_x = lego_starting_x
            #These nested "for" loops will cycle through every row of
            #the "same_color_side" list ("j" index), then every horizontal
            #nonogram grid fitting within that row ("k" index), then every
            #group of consecutive same color studs ("l" index) within that
            #horizontal nonogram grid and paste the image stored in the
            #"color_images_dict" dictionary using the RGB value as the key.
            #The 1 x 1 colored images will be pasted "m" times, where "m"
            #equals the number of successive studs of that color.
            for j in range(len(same_color_side)):
                for k in range(len(same_color_side[j])):
                    for l in range(len(same_color_side[j][k])):
                        for m in range(same_color_side[j][k][l][0]):
                            try:
                                background_img.paste(color_images_dict[same_color_side[j][k][l][1]], (lego_starting_x,lego_starting_y))
                                #"lego_starting_x" is incremented by "lego_pixel_size" so that
                                #the next pasted image is to its right.
                                lego_starting_x += lego_pixel_size
                            except KeyError as e:
                                print("\n" + e)
                                os.exit('There was a problem when generating the mosaic thumbnail and the answer key. ' +
                                'Either you have forgotten to add the 1 x 1 plate scan of the RGB color listed above to the ' +
                                '"1 x 1 plate scans" folder (see the PDF document on the Brickogram github page for more details), ' +
                                'or there were some partially transparent pixels in one of your layers, resulting in a pixel color ' +
                                'of a different color for those pixels. You would then need to delete these transparent pixels ' +
                                'and draw them again with full opacity. Transparent pixels can be created when ' +
                                'you remove the background of a subject and add an alpha channel to your layer.')

                #Upon completing a row, the "x" coordinate is reset to
                #the "lego_initial_starting_x" and the "lego_starting_y"
                #is incremented by "lego_pixel_size" so that the next
                #pasted image is at the start of the next row, down the
                #page.
                lego_starting_x = lego_initial_starting_x
                lego_starting_y += lego_pixel_size

            #A copy of "background_img" is made in order to
            #crop and save it as the thumbnail image.
            thumbnail = background_img
            thumbnail.crop((lego_initial_starting_x, lego_initial_starting_y, (lego_initial_starting_x +
            lego_image_horizontal_size), (lego_initial_starting_y + lego_image_horizontal_size))).save(os.path.join(cwd, "Images", image_name, image_name + " Thumbnail Image.png"))

            #Bright green ("Chartreuse") lines will be drawn on the "lego mosaic" image to delineate the different
            #nonogram grids making up the mosaic, provided that the mosaic is composed of more than one nonogram grid
            #("if number_of_horizontal_grids > 1" and "if number_of_vertical_grids > 1"). The number of horizontal
            #and vertical grids is determined by dividing the "lego image" size in pixels by the "lego_pixel_size"
            #and then by the number of cells per nonogram grid side.
            number_of_horizontal_grids = math.floor(lego_image_horizontal_size / lego_pixel_size / nonogram_cells)

            number_of_vertical_grids = math.floor(lego_image_vertical_size / lego_pixel_size / nonogram_cells)

            if number_of_horizontal_grids > 1:
                grid_starting_x = lego_initial_starting_x + lego_pixel_size * nonogram_cells
                for j in range(number_of_horizontal_grids-1):
                    background_img_editable.line([(grid_starting_x, lego_initial_starting_y - 2*lego_pixel_size),
                    (grid_starting_x, lego_initial_starting_y + lego_image_vertical_size + 2*lego_pixel_size)], fill = "Chartreuse", width = 5)
                    grid_starting_x += lego_pixel_size * nonogram_cells


            if number_of_vertical_grids > 1:
                grid_starting_y = lego_initial_starting_y + lego_pixel_size * nonogram_cells
                for j in range(number_of_vertical_grids-1):
                    background_img_editable.line([(lego_initial_starting_x - 2*lego_pixel_size, grid_starting_y),
                    (lego_initial_starting_x + lego_image_horizontal_size + 2*lego_pixel_size, grid_starting_y)], fill = "Chartreuse", width = 5)
                    grid_starting_y += lego_pixel_size * nonogram_cells

            #The "lego mosaic" image page is appended to both PDF documents.
            background_img.save(os.path.join(cwd, "Images", image_name, image_name + side_panel_pdf_name),
            append=True, quality=100, resolution=300)

            background_img.save(os.path.join(cwd, "Images", image_name, image_name + top_panel_pdf_name),
            append=True, quality=100, resolution=300)

            #Another background image is generated to create the title page.
            background_img, background_img_width, background_img_height, A4_margin = get_background(A4, A4_margin, side)
            background_img_editable = ImageDraw.Draw(background_img)

            background_img_editable.text((title_x,225), title_page_heading_string,
            font=title_page_heading_font, anchor="mm", fill="Black")

            #The pixelated image will be pasted onto the title page. It is
            #instantiated as an Image object, and its width and height allow
            #to calculate its aspect ratio, which will be used to resize it,
            #should either of those dimensions exceed the avilable space on
            #the page.
            title_page_image = Image.open(img_files[i])

            title_page_image_width, title_page_image_height = title_page_image.size

            aspect_ratio = title_page_image_width/title_page_image_height

            #The available vertical height on the page for the image corresponds to the difference in-between
            #a third of the total vertical space on the page and the "y" coordinate right after the heading
            #of the title page (0.75 inch or 225 pixels at 300 ppi plus half the height in pixels of the heading).
            available_vertical_space_for_image = math.floor(background_img_height/3) - (225 + string_half_height)
            #"Delta_height" is equal to the difference between the available vertical space on the page for the image
            #and the image height. If "delta_height" is negative, it means that the image is too large and needs to
            #be scaled down to the available space. The width is then adjusted based on the "aspect_ratio".
            delta_height = available_vertical_space_for_image - title_page_image_height
            if delta_height < 0:
                title_page_image_height = available_vertical_space_for_image
                title_page_image_width = math.floor(available_vertical_space_for_image*aspect_ratio)

            #Similarly, the available width (determined as the total width of the page, minus the left and right margins)
            #is compared to the image width and it is resized if necessary.
            available_horizontal_space_for_image = background_img_width - perforations_margin - non_printable_area_margin
            delta_width =  available_horizontal_space_for_image - title_page_image_width

            if delta_width < 0:
                title_page_image_width = background_img_width - perforations_margin - non_printable_area_margin
                title_page_image_height = math.floor(title_page_image_width/aspect_ratio)
            if delta_height < 0 or delta_width < 0:
                #The resampling filter is set to "Resampling.BOX", such that each pixel in the starting image
                #maps to a pixel in the resized image, without any antialiasing.
                title_page_image = title_page_image.resize((title_page_image_width, math.floor(title_page_image_height)), resample = Image.Resampling.BOX)
            #If the image is smaller than both the available horizontal and vertical space,
            #it will then be scaled such that its vertical side reaches the "available_vertical_space_for_image".
            #This is because the "available_horizontal_space_for_image" is much greater than the
            #"available_vertical_space_for_image". The horizontal dimension of the image is then
            #scaled according to its aspect ratio.
            elif delta_width > 0 and delta_height > 0:
                title_page_image_width = math.floor(available_vertical_space_for_image*aspect_ratio)
                title_page_image_height = available_vertical_space_for_image
                title_page_image = title_page_image.resize((title_page_image_width, title_page_image_height), resample = Image.Resampling.BOX)

            #The image is centered along the horizontal axis.
            image_top_left_x = math.floor((background_img_width-title_page_image_width)/2)

            #A shadow of matching dimensions to the resized image is created and pasted onto the "background_img",
            #slightly offset to the position where the resized image will be pasted thereafter.
            shadow_image = Image.new("RGBA", (title_page_image_width + 100, title_page_image_height + 100), (255,255,255))
            shadow_image_editable = ImageDraw.Draw(shadow_image)
            shadow_image_editable.rectangle([(50,50), (title_page_image_width+50, title_page_image_height+50)], fill=(160, 165, 169))
            shadow_image = shadow_image.filter(ImageFilter.GaussianBlur(7))

            background_img.paste(shadow_image, (image_top_left_x-30, 375 + string_half_height - 30))

            background_img.paste(title_page_image, (image_top_left_x, 375 + string_half_height))

            #Two 1x1 plate images are pasted on either side of the "title_page_heading_string" heading.

            #For the 1x1 plate on the left side, an extra hundred pixels are
            #subtracted from the "x" coordinate, in order to factor in the
            #width of the 1 x 1 plate image itself
            background_img, background_img_editable = paste_plate(title_x -
            string_half_length - 100 - 100, 175, (255,255,255), background_img,
            background_img_editable)

            background_img, background_img_editable = paste_plate(title_x +
            string_half_length + 100, 175, (160, 165, 169), background_img,
            background_img_editable)

            #The "y" coordinate is updated to 0.75 inch (225 pixels at 300 ppi resolution)
            #below the "y" coordinate directly below the pasted image.
            y_required_materials = 375 + string_half_height + title_page_image_height + 225
            y = y_required_materials

            #If you have passed in the "no_blanks" argument when running the code, then
            #the following message will be printed on the title page, using a "x" starting
            #coordinate corresponding to a the "perforations_margin" (default of 0.75 inch).
            if no_blanks == True:
                background_img_editable.text((perforations_margin, y), title_page_no_blanks_string,
                font=title_page_text_font, anchor="ls", fill="Black")
                #The height of the string is stored in the "string_height" variable for use
                #when factoring in the height of the body text when incrementing the "y"
                #coordinates and moving down the page.
                string_box = title_page_text_font.getbbox(title_page_blank_string)
                string_size = [math.floor((string_box[2]-string_box[0])),
                math.floor((string_box[3]-string_box[1]))]
                string_height = string_size[1]
            #If you have passed in the "auto_blanks" argument when running the code, then
            #the following message will be printed on the title page, using a "x" starting
            #coordinate corresponding to a the "perforations_margin" (default of 0.75 inch).
            elif auto_blanks == True:
                background_img_editable.text((perforations_margin, y), title_page_auto_blanks_string,
                font=title_page_text_font, anchor="ls", fill="Black")
                #The height of the string is stored in the "string_height" variable for use
                #when factoring in the height of the body text when incrementing the "y"
                #coordinates and moving down the page.
                string_box = title_page_text_font.getbbox(title_page_blank_string)
                string_size = [math.floor((string_box[2]-string_box[0])),
                math.floor((string_box[3]-string_box[1]))]
                string_height = string_size[1]

            #Otherwise, a 1x1 plate of the same color as "blank_tuple" will be pasted after
            #"title_page_blank_string".
            else:
                background_img_editable.text((perforations_margin, y), title_page_blank_string,
                font=title_page_text_font, anchor="ls", fill="Black")
                #The width of the string needs to be determined in order to know at what "x"
                #coordinate to paste the 1x1 plate (its top left corner is the "x,y" coordinate
                #used in the "paste()" method).

                #The "y - title_page_blank_string_height" is just to line up the 1x1 plate
                #with the text vertically.
                background_img, background_img_editable = paste_plate(perforations_margin +
                title_page_blank_string_length + 50, y - title_page_blank_string_height,
                blank_tuple, background_img, background_img_editable)
                #The height of the string is stored in the "string_height" variable for use
                #when factoring in the height of the body text when incrementing the "y"
                #coordinates and moving down the page.
                string_box = title_page_text_font.getbbox(title_page_blank_string)
                string_size = [math.floor((string_box[2]-string_box[0])),
                math.floor((string_box[3]-string_box[1]))]
                string_height = string_size[1]

            #The "y" coordinate is incremented by the equivalent of 150 pixels plus the
            #blank string height below the blank string (which had a text anchoring of "ls",
            #meaning that the "y" coordinate is situated at the lower left corner of the string).
            y += 150 + string_height

            #This string precedes all of the different colored 1x1 plates (with their corresponding
            #quantity) that are required to complete the mosaic project.
            background_img_editable.text((perforations_margin, y), title_page_materials_string,
            font=title_page_text_font, anchor="ls", fill="Black")

            x = perforations_margin
            #The "y" coordinate is incremented by the equivalent of 0.50 inch below the
            #blank string (which had a text anchoring of "ls", meaning that the "y" coordinate
            #is situated at the lower left corner of the string).
            y += 150
            x_counter = 0
            #The value, key pairs of the "colors" dictionary are transposed into list
            #format and sorted in descending order along the values, as the 1x1 plates
            #with the highest required number should be brought to your attention first.
            colors_sorted = []
            for color, number in colors.items():
                colors_sorted.append([number, color])
            colors_sorted.sort(reverse = True)
            for j in range(len(colors_sorted)):
                background_img, background_img_editable = paste_plate(x, y, colors_sorted[j][1], background_img,
                background_img_editable)
                background_img_editable.text((x+135, y + 75), "x " + str(colors_sorted[j][0]),
                font=title_page_text_font, anchor="ls", fill="Black")
                #The "x_counter" variable stores the number of times that a 1x1 plate
                #was pasted in a given row. The "x" coordinate is incremented by a value
                #that is deemed sufficient to provide ample spacing that would accomodate
                #larger plate count numbers.
                x_counter +=1
                if x_counter < 4:
                    x += 585
                #If the "x_count" number is equal to four, then it means
                #that four plates have already been pasted in the row and
                #that it is now time to move to the next row. The same
                #"string_height" that was determined above (for the
                #"title_page_no_blanks_string", "title_page_auto_blanks_string"
                #or "In this puzzle, the blank color is:" string) is used to increment the "y"
                #coordinate when moving to the next row. The "(y + 750 + string_height)"
                #expression is to adjust the available vertical space left
                #on the page to factor in that there needs to be enough room
                #to write "continued_string" without any overlaps (see below). If the
                #"elif" statement conditions are met, it means that there is
                #enough room for another row of 1x1 plates, and the "y" coordinate
                #is incremented and the "x" coordinate is reset to the left margin
                #("perforations_margin"). The "x" counter is reset to zero,
                #as a new row of 1x1 plates is started.
                elif y + 750 + string_height < background_img_height - 225:
                    x_counter = 0
                    x = perforations_margin
                    y += 125 + string_height

                #Should there be no more space for another row and still some plates to
                #be drawn ("j < len(colors_sorted)-1"), then another canvas is created
                #(after saving the current one in both PDF files), and the list of 1x1
                #plates is continued onto another page. The "x" counter is reset to zero,
                #as a new row of 1x1 plates is started.
                elif j < len(colors_sorted)-1:
                    background_img_editable.text((background_img_width-150, background_img_height-150), continued_string,
                    font=title_page_text_font, anchor="rd", fill="Black")

                    background_img.save(os.path.join(cwd, "Images", image_name, image_name + side_panel_pdf_name),
                    append=True, quality=100, resolution=300)

                    background_img.save(os.path.join(cwd, "Images", image_name, image_name + top_panel_pdf_name),
                    append=True, quality=100, resolution=300)

                    x_counter = 0

                    background_img, background_img_width, background_img_height, A4_margin = get_background(A4, A4_margin, side)
                    background_img_editable = ImageDraw.Draw(background_img)

                    background_img_editable.text((perforations_margin, 225), continued_string_new_page,
                    font=title_page_text_font, anchor="lt", fill="Black")
                    x = perforations_margin
                    y = 325 + string_height

            #Upon completing the title page, it is appended to both PDF files and
            #a new canvas is opened to start printing the side panel instructions,
            #with "side" still being equal to "True", meaning that the canvas
            #is in portrait mode.
            background_img.save(os.path.join(cwd, "Images", image_name, image_name + side_panel_pdf_name),
            append=True, quality=100, resolution=300)

            background_img.save(os.path.join(cwd, "Images", image_name, image_name + top_panel_pdf_name),
            append=True, quality=100, resolution=300)

            background_img, background_img_width, background_img_height, A4_margin = get_background(A4, A4_margin, side)
            background_img_editable = ImageDraw.Draw(background_img)

            #The "margin" variable stores the number of pixels in-between the bottom of the
            #title text and the point where the clue boxes start to be drawn.
            #95 pixels seem to align the text nicely such that there is a spacer of around 60-70
            #pixels.
            margin = 95 + string_height

            #The "for j in range(math.ceil(len(same_color_side)/nonogram_cells))" allows
            #to loop over every different basplate row ("row chunks"). The "current_array"
            #simply slices the "same_color_side" array according to the current "j" index.
            #For example, the first "j" index of zero results in the slice to be as follows:
            #"same_color_side[0:0+32]". Similarly, the "for k in range(math.ceil(width/
            #pixel_size/nonogram_cells))" loop loops over all of the different baseplate
            #columns ("column chunks"). The "starting_y" coordinate is reinitialized to
            #the the pixel count of the "non-non_printable_area_margin" at the top of the
            #page, plus margin (which is the sum of the title "string_height" and the 60
            #pixel spacer in-between the "y" coordinate below the title and the top of the
            #first clue box). This effectively creates a side panel clue sheet for each
            #baseplate, as the "side_panel_pdf_name" file is saved at the end of
            #the "for m in range(len(current_array))" loop looping through all of the rows
            #of the pixelated image.
            for j in range(math.ceil(len(same_color_side)/nonogram_cells)):
                current_array = same_color_side[j*nonogram_cells: j*nonogram_cells + nonogram_cells]
                for k in range(math.ceil(width/pixel_size/nonogram_cells)):
                    if auto_blanks:
                        blank_tuple = auto_blanks_grid_blanks[str(j) + ", " + str(k)][1]

                    starting_y = margin + non_printable_area_margin
                    for l in range(len(current_array)):
                        #The "row_colors" list is populated with every color ("element[1]") of
                        #a sequence of consecutive same-colored aggregated pixels, along with
                        #the number of aggregated pixels in theses sequences ("element[0]").
                        #Only the colors that are not the blank are included in the "row_colors"
                        #list, unless you have specified "no_blanks", in which case they are
                        #all present in the list.
                        row_colors = []
                        for element in current_array[l][k]:
                            if no_blanks == True or element[1] != blank_tuple:
                                row_colors.append([element[0], element[1]])
                        #The "starting_x" coordinate of where the clue boxes will start to
                        #be drawn is determined by subtracting the "perforations_margin"
                        #and the number of pixels taken up by all of the clue boxes for
                        #that row ("len(row_colors)*stud_pixels") from the total width
                        #of the canvas ("background_img_width").
                        starting_x = background_img_width - (perforations_margin + len(row_colors)*stud_pixels)
                        #The clue boxes are drawn, using the clue color ("element[1]") as the fill.
                        for element in row_colors:
                            background_img_editable.rectangle([starting_x, starting_y,
                            starting_x+stud_pixels, starting_y+stud_pixels],
                            fill=element[1])

                            number_string = str(element[0])
                            #The number of consecutive same-colored aggregated pixels ("number_string")
                            #is written within the clue boxes.
                            if len(number_string) > 1:
                                background_img_editable.text((math.floor(starting_x + stud_pixels/2 + x_pixel_adjustment_double_digit),
                                math.floor(starting_y + stud_pixels/2 + y_pixel_adjustment_double_digit)), number_string, fill="White",
                                font=numbers_font, anchor="mm", stroke_width=3, stroke_fill="Black")
                            else:
                                background_img_editable.text((math.floor(starting_x + stud_pixels/2 + x_pixel_adjustment_single_digit),
                                math.floor(starting_y + stud_pixels/2 + y_pixel_adjustment_single_digit)), number_string, fill="White",
                                font=numbers_font, anchor="mm", stroke_width=3, stroke_fill="Black")

                            #After drawing each box, the "starting_x" corresponding to the top-left
                            #corner "x" coordinate is incremented by the number of pixels taken up
                            #by a stud on the base plate ("stud_pixels"). The boxes are being drawn
                            #in the direction of the "perforations_margin", as the first clue is
                            #farthest from the perforations.
                            starting_x += stud_pixels
                        #After each iteration of the "for element in row_colors" loop, the
                        #"starting_y" is incremented by "stud_pixels", as the rows of clue
                        #boxes are being drawn from the top to the bottom of the page.
                        starting_y += stud_pixels
                    #A line spanning the length of all the rows of clue boxes, including
                    #those that only contain blanks is drawn along the "perforations_margin".
                    #this will enable you to line up the clue sheets properly on the base plate
                    #nonogram grid.
                    line_x = background_img_width - perforations_margin
                    background_img_editable.line([(line_x, margin + non_printable_area_margin),
                    (line_x, margin + non_printable_area_margin + stud_pixels*nonogram_cells)],
                    fill=(200,200,200), width=10)

                    if not no_blanks:
                        background_img, background_img_editable = paste_plate(perforations_margin,
                        non_printable_area_margin + A4_margin, blank_tuple, background_img, background_img_editable)

                    #The title is added to the page, with the base plate row and column number.
                    puzzle_text = (image_name + " (" + side_string + ", " + row_string +
                    "  " + str(j+1) + ", "  + column_string + " " + str(k+1) + ")")

                    background_img_editable.text((math.floor(background_img_width/2) + 150,
                    non_printable_area_margin + A4_margin), puzzle_text, fill="Black",
                    font=title_font, anchor="mt")

                    #The final image is outputted in PDF format.
                    background_img.rotate(180).save(os.path.join(cwd, "Images", image_name, image_name + side_panel_pdf_name),
                    append=True, quality=100, resolution=300)

                    #A new "background_img" canvas is generated for the next iteration of the
                    #nested for loops.
                    background_img, background_img_width, background_img_height, A4_margin = get_background(A4, A4_margin, side)
                    background_img_editable = ImageDraw.Draw(background_img)


            #The mirror case scenario is applied to the top clue panel, with
            #"side" being set to "False", as the digits will be written in landscape
            #mode, since the panel will be laid down in landscape mode above the
            #base plate.
            side = False
            background_img, background_img_width, background_img_height, A4_margin = get_background(A4, A4_margin, side)
            background_img_editable = ImageDraw.Draw(background_img)

            top_image_objects = []
            for j in range(math.ceil(len(same_color_top)/nonogram_cells)):
                current_array = same_color_top[j*nonogram_cells: j*nonogram_cells + nonogram_cells]
                for k in range(math.ceil(width/pixel_size/nonogram_cells)):
                    if auto_blanks:
                        #Note that when accessing the "auto_blanks_grid_blanks"
                        #dictionary within a "for" loop cycling through "same_color_top":, the
                        #"j" and "k" indices will be reversed, as this list is
                        #mirrored with respect to "same_color_side".
                        blank_tuple = auto_blanks_grid_blanks[str(k) + ", " + str(j)][1]

                    starting_x = margin + non_printable_area_margin
                    for l in range(len(current_array)):
                        row_colors = []
                        for element in current_array[l][k]:
                            if no_blanks == True or element[1] != blank_tuple:
                                row_colors.append([element[0], element[1]])
                        starting_y = background_img_height - (perforations_margin + stud_pixels*len(row_colors))
                        for element in row_colors:
                            background_img_editable.rectangle([starting_x, starting_y,
                            starting_x+stud_pixels, starting_y+stud_pixels],
                            fill=element[1])

                            number_string = str(element[0])
                            if len(number_string) > 1:
                                background_img_editable.text((math.floor(starting_x + stud_pixels/2 + x_pixel_adjustment_double_digit),
                                math.floor(starting_y + stud_pixels/2 + y_pixel_adjustment_double_digit)), number_string, fill="White",
                                font=numbers_font, anchor="mm", stroke_width=3, stroke_fill="Black")
                            else:
                                background_img_editable.text((math.floor(starting_x + stud_pixels/2 + x_pixel_adjustment_single_digit),
                                math.floor(starting_y + stud_pixels/2 + y_pixel_adjustment_single_digit)), number_string, fill="White",
                                font=numbers_font, anchor="mm", stroke_width=3, stroke_fill="Black")

                            starting_y += stud_pixels
                        starting_x += stud_pixels

                    line_y = background_img_height - perforations_margin
                    background_img_editable.line([(margin + non_printable_area_margin, line_y),
                    (margin + non_printable_area_margin + stud_pixels*nonogram_cells, line_y)],
                    fill=(200,200,200), width=10)

                    background_img_rotated = background_img.rotate(270, expand = True)
                    background_img_rotated_editable = ImageDraw.Draw(background_img_rotated)

                    if not no_blanks:
                        background_img_rotated, background_img_rotated_editable = paste_plate(perforations_margin,
                        non_printable_area_margin + A4_margin, blank_tuple, background_img_rotated, background_img_rotated_editable)

                    puzzle_text = (image_name + " (" + top_string + ", " + row_string +
                    "  " + str(k+1) + ", "  + column_string + " " + str(j+1) + ")")

                    background_img_rotated_editable.text((math.floor(background_img_height/2) + 150,
                    non_printable_area_margin + A4_margin), puzzle_text, fill="Black",
                    font=title_font, anchor="mt")

                    #As the nested for loops are mirrored in the case of the top panel clues when
                    #compared to the side panel clues, the clue sheets are created by walking down
                    #a column, instead of down a row. The "k" index mapping to the current "column chunk"
                    #and the "j" index corresponding to the current "row chunk", followed by the
                    #"background_img_rotated" object are appended to the "top_image_objects" list.
                    #The list is sorted after completing the nested for loop and the images are
                    #appended to the  "top_panel_pdf_name" PDF document in the same order
                    #as they are found in the "side_panel_pdf_name", so that you may easily
                    #open the clue booklets at the same page for a given nonogram puzzle.
                    top_image_objects.append([k, j, background_img_rotated])

                    background_img, background_img_width, background_img_height, A4_margin = get_background(A4, A4_margin, side)
                    background_img_editable = ImageDraw.Draw(background_img)

            top_image_objects.sort()
            for j in range(len(top_image_objects)):
                #The final image is outputted in PDF format.
                top_image_objects[j][2].save(os.path.join(cwd, "Images", image_name, image_name + top_panel_pdf_name),
                append=True, quality=100, resolution=300)

            bar()
        except Exception as e:
            print(str(e))
            print("\n\n")
            sys.exit('Please ensure that the aggregated pixel count in both dimensions of the ' +
            'pixelated image matches the number of studs in the corresponding sides of your mosaic. ' +
            'These must in turn be a multiple of the dimension of your square nonogram grid. ' +
            '\nFor example, A 1280x2560 px image with 20 px per aggregated pixel ' +
            'would contain 64x128 aggregated pixels, both of which are a multiple of the default ' +
            'value of "nonogram_cells" of 32 (32 cells by side of the square nonogram grid). ' +
            "Please refer to the Brickogram github page's instructions on how to prepare your" +
            'pixelated images.')
