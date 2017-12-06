# Irish Sheet Music Creation

This repository contains code that downloads and generates a [PDF] of Irish
tunes.  It's highly personalized, however, it is easy to update using your own
set of tunes.

This uses the awesome [thesession] Irish Music database to automatically create
the [PDF] document of tunes.


## Usage

To personalize:

1. Edit the [tunes spreadhsheet]--you need Apple Numbers for this.
   If anyone is willing to add to [tex generator] to make this more robust
   please let me know.
2. Download the ABC files you want from [thesession].
3. Use [scrapesession]: `$ src/sh/run-scrape.sh <abc ID>`
4. Generate the [Tunes.pdf] in the `dervied` directory: `$ make`


![Tunes](derived/Tunes.pdf)


<!-- links -->
[PDF]: https://en.wikipedia.org/wiki/Portable_Document_Format
[tunes spreadhsheet]: data/tune-list.numbers
[tex generator]: src/python/mktunetex.py
[thesession]: https://thesession.org
[scrapesession]: src/sh/run-scrape.sh
[Tunes.pdf]: derived/Tunes.pdf
