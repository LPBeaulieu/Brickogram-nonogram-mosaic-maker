# Brickogram (nonogram mosaic maker)
This app lets you create nonogram puzzles from pixelated images, for solving using 1 x 1 plates, giving you stunning mosaics as a result!

![Brickogram Thumbnail](https://github.com/LPBeaulieu/Brickogram-nonogram-mosaic-maker/blob/main/Brickogram%20Thumbnail.png)
<h3 align="center">Brickogram</h3>
<div align="center">
  
  [![License: AGPL-3.0](https://img.shields.io/badge/License-AGPLv3.0-brightgreen.svg)](https://github.com/LPBeaulieu/TintypeText/blob/main/LICENSE)
  ![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
  ![macOS](https://img.shields.io/badge/mac%20os-000000?style=for-the-badge&logo=macos&logoColor=F0F0F0)
  ![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
  
</div>

---

<p align="left"> <b>Brickogram</b> is an app that creates nonogram puzzles from pixelated images, which you solve using 1 x 1 plates. Upon completing a puzzle, you get a mosaic that you can hang on your wall! Two clue sheet booklets are generated by the code, one for the top panel, and the other one for the side panel clues. You will place these beside your base plate that will serve as the nonogram grid. A neat feature about <b>Brickogram</b> is that it lets you choose the color of the blank, or, if you yould like an easier puzzle, you could opt to have all the colored clues included on the clue sheets (no blanks in the puzzle). <b>Brickogram</b> also tells you how many 1 x 1 plates of each color you will need for your project. You can now turn your favorite pictures into pixelated mosaic artwork by processing them with the GIMP software, according to the instructions included in the PDF document (https://github.com/LPBeaulieu/Brickogram-nonogram-mosaic-maker/blob/main/Brickogram%20Image%20Creation%20Tips.pdf) found on this github repo!
</p>

## 📝 Table of Contents
- [Limitations](#limitations)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Author](#author)
- [Acknowledgments](#acknowledgments)

## ⛓️ Limitations <a name = "limitations"></a>

- You can place different True Type Font (".ttf") files in the subfolders of the "Fonts" folder, should you like to have different fonts in the PDF documents, and their size and spacing
will adjust themselves automatically. The "Fonts" folder contains the "Cover Page Heading Font" subfolder (for the heading of the the cover pages, the default font being taken from the
"Nb Pixel Font Bundle 2", check them out at https://nimblebeastscollective.itch.io/nb-pixel-font-bundle).

  The other subfolders are "Cover Page Subtitle Font" (for the subtitle on the cover page), "Title Page Heading Font" and "Title Page Text Font" (for the heading and body text on the title page, respectively, the title page containing the pixelated image, blank color, along with the required 1 x 1 plates for making the mosaic), "Title Font" (for the headings on the actual clue sheets) and "Numbers Font" (for the clue numbers). It is important that you use a font that has monospaced digits for the numbers font to ensure proper spacing within the clue boxes, but most fonts use monospace digits, so this shouldn't be a problem for you.

- When generating custom palettes with GIMP based on the actual colors of your 1 x 1 plates (see the PDF document for details), you should only select the color of a given 1 x 1 plate once using the "Colour Picker Tool", and then take note of that hex code for later use in other palettes, or if you mistakenly delete your color palette. This way, all of the colors of the pixelated images that you generate will exactly match those that you initially detected when first creating your palette. Otherwise, the very closely related colors originating from several different "Colour Picker Tool" actions wouldn’t necessarily be equated by the code, resulting in frustration for you down the road, as these different colored clues wouldn’t be merged together (several closely related shades of yellow, for instance).

- Make sure that the number of aggregated pixels in each dimension of your pixelated image matches the number of pegs on the corresponding side of your mosaic. For example, starting with a cropped photo measuring 128 x 128 px, each pixel would be merged with its horizontal and vertical neighbor in order to give aggregated pixels of a size of 2 x 2 px. This way, each 1 x 1 plate making up the 64 x 64 peg mosaic would map to an aggregated pixel (128 px / 64 = 2 px).  This is important, as the Python code will "walk" along the image, one aggregated pixel at a time, to determine the color of the pixels in each row and column, so the relative dimension of these must line up with those of your mosaic. This may sound complicated, but as long as you follow the steps in the PDF instructions document, you should have no problems!

- Also, there should be at least one line of a width of one pixel or at least one isolated pixel surrounded by pixels of a different color in your pixelated image, so that the code may determine how many actual pixels make up an aggregated pixel. The reason for this is that the code "walks" across the image at increments equivalent to the aggregated pixel size, in order to gather a list of all the nonogram clue colors.  


## 🏁 Getting Started <a name = "getting_started"></a>

The following instructions will be provided in great detail, as they are intended for a broad audience and will allow to run a copy of <b>Brickogram</b> on a local computer.

The instructions below are for Windows operating systems, but the code runs very nicely on Linux as well.

Start by downloading the zipped working folder, by going to the top of this github repo and clicking on the green "Code" button, and then click on the "Download Zip" option. Extract the zipped folder to your desired location. Make sure that you keep the "Images" and "Font" folders within your working folder. You will place the pixelated images that you wish to be converted into nonograms in the "Images" folder, and the resulting title pages and clue sheets will be appended in sequence for each pixelated image to the two PDF documents (one for the side and the other for the top panel clues). These PDF files will be created in the "Image" folder as well. Next, hold the "Shift" key while right-clicking in your working folder, then select "Open PowerShell window here" to access the PowerShell in your working folder and enter the commands described below. 

<b>Step 1</b>- Install <b>Pillow</b> (Python module to handle the pixelated image files) using the following command:

```
py -m pip install --upgrade Pillow
```

<b>Step 2</b>- Install <b>alive-Progress</b> (Python module for a progress bar displayed in command line):
```
py -m pip install alive-progress
```

<b>Step 5</b>- You're now ready to use <b>Brickogram</b>! 🎉

## 🎈 Usage <a name="usage"></a>

- Once the pixelated images have been prepared, using <b>Brickogram</b> is actually very easy. Start by placing your pixelated images in the “Images” folder. Next, hold the "Shift" key while right-clicking in your working folder, then select "Open PowerShell window here" to access the PowerShell in your working folder and enter the following:

```
py brickogram.py
```
The code will take a few seconds to run, as it is creating two PDF documents containing your puzzle clues for the top and side panels. 

- There are a few arguments that you could pass in after the above command, should you like to get different outputs:

  - In order to print in A4 format instead of US Letter format, simply pass in “A4” when running the code (' py brickogram.py "A4" '). 

  - The number of cells per side of the square nonogram grid is set to 32 by default (as the standard square base plates measure 32 pegs per side), but may be changed to any number, as long as the total number of pegs in the mosaic is a multiple of that number. That is to say your nonogram grid will fit "x" times within the total width and "y" times in the total height of your final mosaic, where "x" and "y" are both integers. For example, a mosaic with a total width 64 pegs and a height of 128 pegs would require a nonogram grid size of 16 x 16 (16 pegs) or 32 x 32 (32 pegs), both of which are common base plate dimensions. Simply pass in the number of nonogram cells after the "nonogram_cells:" argument when running the code (for example: ' py brickogram "nonogram_cells:16" ' for a 16 x 16 peg nonogram grid).

  - The code automatically picks the lightest color in each pixelated image as the blank color for the puzzles making up that mosaic (each mosaic being normally made up of several nonogram grids). In order to specify a different blank color that will be applied to all the pixelated images within the “Images” folder, enter the color after the “blank:” argument, either in hex code or RGB format. The RGB colors need to be parenthesized (' py brickogram.py "blank:(255,255,255)" ' would select white as the blank for all the nonogram puzzles making up each pixelated image in the "Images" folder). 

    You can also designate a blank color for an individual image by placing the parenthesized RGB value at the end of the file name (for instance: 'my pixelated image name (0,0,0).jpg' would set the blank color as black for all the nonogram puzzles making up that pixelated image).

    Finally, you can choose to have nonograms without any blanks, with all the colors being included in the top and side panel clue sheets, by passing in the “no_blanks” argument when running the code.

- Make sure to place any arguments you pass in within quotes and to include a space in-between arguments when running the Python code.

- When solving the nonogram puzzles, line up your clue pages with the base plate that you will be using as a nonogram grid, using the grey lines that are drawn along the long edges of the clue sheets.

- You could choose to bind the clue sheet booklets using 2 x 8 Technic plates with 7 holes and flexible plastic binder rings that would be hooped through the holes. You would need to line up your clue booklets with the base plate that you will be using as a nonogram grid. Then, overlay the 2 x 8 Technic with 7 holes such that it overlaps both the base plate and your page. Draw where the holes will be punched in the paper with a pencil using the Technic plate holes as stencils. This will ensure that your instructions booklets are well aligned with the nonogram grid when you clip them to the base plate.

- When solving nonogram puzzles on 32 x 32 base plates, you could subdivide your grid by drawing horizontal and vertical lines on your base plate using my biodegradable and erasable ink (https://www.instructables.com/Recipe-for-a-Multipurpose-Biodegradable-and-Wet-Er/).
        
  <br><b>And there you have it!</b> You're now ready to turn your favorite pictures into fun nonogram puzzles, giving you stunning mosaics that you can hang on your wall! 🎉📖
  
  
## ✍️ Authors <a name = "author"></a>
- 👋 Hi, I’m Louis-Philippe!
- 👀 I’m interested in natural language processing (NLP) and anything to do with words, really! 📝
- 🌱 I’m currently reading about deep learning (and reviewing the underlying math involved in coding such applications 🧮😕)
- 📫 How to reach me: By e-mail! LPBeaulieu@gmail.com 💻


## 🎉 Acknowledgments <a name = "acknowledgments"></a>
- Hat tip to [@kylelobo](https://github.com/kylelobo) for the GitHub README template!




<!---
LPBeaulieu/LPBeaulieu is a ✨ special ✨ repository because its `README.md` (this file) appears on your GitHub profile.
You can click the Preview link to take a look at your changes.
--->
