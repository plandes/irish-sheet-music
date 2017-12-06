# Irish Sheet Music Creation

This repository contains code that downloads and generates a [PDF] of Irish
tunes.  This uses the awesome [thesession] Irish Music database to
automatically create the [PDF] document of tunes.

It's highly personalized, however, it is easy to update using your own
set of tunes.  The toolset generates sheet music for single tunes or allows you
to create sets.  If the latter, it will assemble sets in groups.


## Usage

To personalize:

1. Edit the [tunes spreadsheet]--you need Apple Numbers for this.
   If anyone is willing to add to [tex generator] to make this more robust
   please let me know.
2. Download the ABC files you want from [thesession].
3. Use [scrapesession]: `$ src/sh/run-scrape.sh <abc ID>`
4. Generate the [Tunes.pdf] in the `dervied` directory: `$ make`


### Editing the *Tunes Spread Sheet*

There are two table of content types in the [tunes spreadsheet]:
* Single Tunes (these are one offs)
* Sets (to create a set populate the *Next Tune In Set* column).

When adding new tunes, the [scrapesession] program will find the tune, download
it and create a row to add to the spreadsheet.  This admittedly all a little
clunky but I haven't had time to stream line it.  Maybe you do!  If so I could
use you help.


## Process

It generates the [Tunes.pdf] from the following `make` target/dependency
process:

1. Convert ABC text files to Encapsulated Postscript Files (`.abc` to `.eps`).
2. Generate the Latex file using [tex generator], which reads the
   [tunes spreadsheet] file to create the sheet music entries.
3. Create a `.dvi` from the Latex source
4. Create the postscript `.ps` from the `.dvi`.
5. Finally, create the [PDF] from the postscript file.


## Tunes File

Click [here](derived/Tunes.pdf) to view the file.


<!-- links -->
[PDF]: https://en.wikipedia.org/wiki/Portable_Document_Format
[tunes spreadsheet]: data/tune-list.numbers
[tex generator]: src/python/mktunetex.py
[thesession]: https://thesession.org
[scrapesession]: src/sh/run-scrape.sh
[Tunes.pdf]: derived/Tunes.pdf
