#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from appscript import *
import pprint
import pickle
import re
import unicodedata

#DAT_CACHE_FILE = None#'%s/view/music/irish/tex/target/tune-sets.dat' % os.environ['HOME']
TUNES_DELIM = '%{epstunes}%'

# http://www.biteyourownelbow.com/abcnotation.htm
ABC_FIELDS = { 'T': 'title',
               'K': 'key',
               'L': 'length',
               'C': 'composer',
               'D': 'discography ',
               'H': 'history ',
               'N': 'notes',
               'O': 'origin',
               'Q': 'tempo',
               'R': 'rhythm',
               'S': 'source',
               'Z': 'transcription note' }

class TuneFormatUtil:
    def stripThe(self, tuneName, fromFrontToo):
        match = re.search('(.*)\w*, The\w*$', tuneName)
        if match:
            tuneName = "The " + match.group(1)
        match = re.search('^The\w* (.+)$', tuneName)
        if fromFrontToo and match:
            tuneName = match.group(1)
        try:
            return tuneName#.decode('latin_1')
        except Exception as e:
            print(e)
            raise Exception("can't decode tune name: %s" % (tuneName))

class TunesAggregator:
    """Collect Tune Data and Aggregate"""

    def __init__(self, nameColHeader, nextTuneHeader, urlColHeader,
                 tuneSpreadsheetFile, abcDir, cacheFile):
        self.nameColHeader = nameColHeader
        self.nextTuneHeader = nextTuneHeader
        self.tuneSpreadsheetFile = tuneSpreadsheetFile
        self.abcDir = abcDir
        self.urlColHeader = urlColHeader
        self.cacheFile = cacheFile
        self.tuneNames = []
        self.tunesByName = {}
        self.tuneSets = []

    def readSpreadsheet(self):
        nu = app('Numbers')
        doc = nu.open(self.tuneSpreadsheetFile)
        try:
            if doc == k.missing_value:
                raise Exception("couldn't open number document: %s" % doc)
            # for sheet in doc.sheets():
            #     for table in sheet.tables():
            #         if table.selection_range():
            #             current_table = table
            sheet = nu.documents.first.sheets()[0]
            if sheet == None:
                raise Exception('Missing sheet')
            else:
                table = sheet.tables()[0]
                nameIdx = None
                nextTuneIdx = None
                urlIdx = None
                if table == None:
                    raise Exception('Missing table')
                else:
                    rows = table.row()
                    self.getColumnIndexes(rows[0])
                    self.addTuneEntry(rows)
        finally:
            doc.close()

    def getColumnIndexes(self, row):
        cells = row.cells()
        for i in range(0, len(cells)):
            cell = cells[i]
            if cell.value() == self.nameColHeader:
                self.nameIdx = i
            if cell.value() == self.nextTuneHeader:
                self.nextTuneIdx = i
            if cell.value() == self.urlColHeader:
                self.urlIdx = i
        if (self.nameIdx == None):
            raise Exception('Missing a column "%s"' % self.nameColHeader)
        if (self.nextTuneIdx == None):
            raise Exception('Missing a column "%s"' % self.nextTuneHeader)
        if (self.urlIdx == None):
            raise Exception('Missing a column "%s"' % self.urlColHeader)

    def addTuneEntry(self, rows):
        for rowIdx in range(1, len(rows)):
            row = rows[rowIdx]
            cells = row.cells()
            url = cells[self.urlIdx].value()
            if url == '?':
                continue
            tuneName = self.cleanUc(cells[self.nameIdx].value())
            nextTuneName = self.cleanUc(cells[self.nextTuneIdx].value())
            if (nextTuneName == 0.0):
                nextTuneName = None
            match = re.search('.*/(.+?)/?(?:\\.abc)?(?:\\?.+)?$', url)
            if match == None:
                raise Exception('Source URL for tune \'%s\' doesn\'t contain tune id: %s' % (url, tuneName))
            id = match.group(1)
            self.tuneNames.append(tuneName)
            self.tunesByName[tuneName] = {'name': tuneName, 'next': nextTuneName, 'url': url, 'id': id}

    def cleanUc(self, text):
        if (isinstance(text, str) or isinstance(text, str)):
            text = text.replace("\u2019", "'")
        return text

    def printTuneStructs(self):
        pp = pprint.PrettyPrinter(indent = 8)
        pp.pprint(self.tunesByName)

    def save(self):
        datFile = open(self.cacheFile, 'wb')
        try:
            pickle.dump(self.tuneNames, datFile)
            pickle.dump(self.tunesByName, datFile)
        finally:
            datFile.close()

    def load(self):
        datFile = open(self.cacheFile, 'rb')
        try:
            self.tuneNames = pickle.load(datFile)
            self.tunesByName = pickle.load(datFile)
        finally:
            datFile.close()

    def getSetForName(self, tuneDetail):
        tuneSet = []
        while True:
            tuneSet.append(tuneDetail['name'])
            nextTune = tuneDetail['next']
            if nextTune == None:
                break
            if nextTune in self.tunesByName:
                tuneDetail = self.tunesByName[nextTune]
            else:
                print("WARNING: couldn't find next tune '%s'" % (tuneDetail['name']))
                break
        return tuneSet

    def createPrevTuneEntries(self):
        for thisTune in list(self.tunesByName.values()):
            nextTuneName = thisTune['next']
            if nextTuneName != None:
                if nextTuneName in self.tunesByName:
                    nextTune = self.tunesByName[nextTuneName]
                    if nextTune != None:
                        nextTune['prev'] = thisTune['name']

    def createTuneSets(self):
        inSets = set()
        self.createPrevTuneEntries()
        for tuneName in self.tuneNames:
            thisTune = self.tunesByName[tuneName]
            if (tuneName not in inSets) and ('prev' not in thisTune):
                tuneSet = self.getSetForName(thisTune)
                self.tuneSets.append(tuneSet)
                inSets |= set(tuneSet)

    def printTunesSets(self):
        for tuneName in self.tuneSets:
            print(tuneName)

    def parseTuneInfoFromAbc(self, abcFile, tune):
        tf = TuneFormatUtil()
        file = open(abcFile, 'r')
        try:
            for line in file.readlines():
                match = re.search('^([A-Z]):[\t ]*(.+)$', line)
                if match:
                    (key, val) = (match.group(1), match.group(2))
                    if key == 'T':
                        val = tf.stripThe(val, False)
                    if key in ABC_FIELDS:
                        key = ABC_FIELDS[key]
                        tune[key] = val
        finally:
            file.close()

    def getTuneTitlesFromAbc(self):
        filesById = {}
        for f in os.listdir(self.abcDir):
            f = '%s/%s' % (self.abcDir, f)
            if os.path.isfile(f):
                m = re.search('.*\\/(.*?)\\.abc$', f)
                if m:
                    id = m.group(1)
                    filesById[id] = f
        for tune in list(self.tunesByName.values()):
            if tune['id'] not in filesById:
                print(('Missing tune \'%s\' ABC file for tune ID \'%s\'' % (tune['name'], tune['id'])))
                raise Exception('Missing tune \'%s\' ABC file for tune ID \'%s\'' % (tune['name'], tune['id']))
            self.parseTuneInfoFromAbc(filesById[tune['id']], tune)

    def getTuneSets(self):
        return self.tuneSets

    def getTunesByName(self):
        return self.tunesByName


class TuneLatexWriter:
    """Outputs a Latex File based on Tune Aggregation"""

    def __init__(self, tuneAggregator, texInput, texOutput):
        self.tuneAggregator = tuneAggregator
        self.texInput = texInput
        self.texOutput = texOutput
        self.abcIncFormat = "{{{id}}}{{{id}.eps}}{{{name}}}{{{title}}}{{{key}}}{{{rhythm}}}{{{url}}}{{{aka}}}"

    def processTunes(self):
        tf = TuneFormatUtil()
        for tune in list(self.tuneAggregator.getTunesByName().values()):
            stripTitle = tf.stripThe(tune['title'], True)
            stripName = tf.stripThe(tune['name'], True)
            #stripName = stripName.encode('utf-8')
            #stripTitle = stripTitle.encode('utf-8')
            if stripTitle != stripName:
                tune['aka'] = 'a.k.a: %s' % stripName
            else:
                tune['aka'] = ''

    def outputTuneEntries(self, outFile):
        tf = TuneFormatUtil()
        tunes = self.tuneAggregator.getTunesByName()
        for tuneSet in self.tuneAggregator.getTuneSets():
            if len(tuneSet) > 1:
                outFile.write("\\tuneset{" + " / ".join([tf.stripThe(x, True) for x in tuneSet]) + "}{%\n")
                for tuneName in tuneSet:
                    tune = tunes[tuneName]
                    outFile.write(("\\abcincs" + self.abcIncFormat + "\n").format(**tune))
                outFile.write("}\n")
        for tuneSet in self.tuneAggregator.getTuneSets():
            if len(tuneSet) == 1:
                tune = tunes[tuneSet[0]]
                text = ("\\abcinc" + self.abcIncFormat + "\n").format(**tune)
                outFile.write(text)

    def createLatexTunesFile(self):
        template = open(self.texInput, 'r')
        outFile = None
        try:
            outFile = open(self.texOutput, 'w')
            for line in template.readlines():
                if line.rstrip() == TUNES_DELIM:
                    self.outputTuneEntries(outFile)
                else:
                    outFile.write(line)
        finally:
            template.close()
            if outFile != None:
                outFile.close()

def main(argv):
    if len(argv) != 5:
        sys.stdout.write('usage: %s <music tex template> <abc dir> <tune spreadsheet> <output tex file> <cache dir>\n' %
                         os.path.basename(sys.argv[0]))
        sys.exit(1)
    (texInput, abcDir, tuneSpreadsheetFile, texOutput, datCacheFile) = argv
    datCacheFile = datCacheFile + '/tunes-cache.dat'
    print('using dat cache file: %s' % datCacheFile)
    tu = TunesAggregator(tuneSpreadsheetFile = tuneSpreadsheetFile,
                         abcDir = abcDir,
                         urlColHeader = 'Source',
                         nameColHeader = 'Name',
                         nextTuneHeader = 'Next Tune In Set',
                         cacheFile = datCacheFile)
    latexWriter = TuneLatexWriter(tuneAggregator = tu,
                                  texInput = texInput,
                                  texOutput = texOutput)
    if datCacheFile:
        if not os.path.isfile(datCacheFile):
            tu.readSpreadsheet()
            tu.save()
        else:
            tu.load()
    tu.createTuneSets()
    #tu.printTuneStructs()
    #tu.printTunesSets()
    tu.getTuneTitlesFromAbc()
    latexWriter.processTunes()
    latexWriter.createLatexTunesFile()

if __name__ == "__main__":
    main(sys.argv[1:])
