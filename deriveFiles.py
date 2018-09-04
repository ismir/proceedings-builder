#!/usr/bin/python

'''Split up master list of paper titles, authors, and sessions
(completePaperList.txt) into the various files needed by other
scripts for generating the pdf proceedings (papers.tex) and the
electronic proceedings.

'''

#import csv
import collections
import os
import shutil
import io  
import sys  
import urllib.request  
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')

def unicode_tsv_reader(utf8FileName):
    "Generator for reading a tab-delimited file"
    # with open(utf8FileName, newline='', encoding='utf-8') as utf8file:
    with open(utf8FileName, encoding='utf-8') as utf8file:
        for line in utf8file.readlines():
            # yield [cell for cell in unicode(line, 'utf-8').rstrip('\n\r').split('\t')]
            yield [cell for cell in line.rstrip('\n\r').split('\t')]
            

def loadSessionInfo():
    return {k: (name, int(num)) for k, name, num
            in unicode_tsv_reader('data/sessionInfo.txt')}

'''--------------- generate paper.tex file ---------------'''        
def generatePapersDotTex():
    lastSession = ""
    sessionInfo = loadSessionInfo()
    authorCount = collections.defaultdict(int)
    
    # with io.open('2018_Proceedings_ISMIR/papers.tex', 'w', encoding='utf-8') as papersDotTex:
    # with codecs.open('2018_Proceedings_ISMIR/papers.tex', 'w', 'utf-8') as papersDotTex:
    with open('2018_Proceedings_ISMIR/papers.tex', 'w', encoding='utf-8') as papersDotTex:
        for title, authors, number, session in unicode_tsv_reader('data/completePaperList.txt'):
            authors = andToComma(authors)
            for author in authors.split(', '):
                authorCount[author] += 1
                
            if session != lastSession:
                name, page = sessionInfo[session]
                papersDotTex.write(papersSectionHeader(name, page))
            lastSession = session
            
            papersDotTex.write('\includepaper{%s}{%s}{articles/%d_Paper}\n'
                               % (latexEscape(title), authors, int(number)))

    #print sorted(authorCount.iteritems())
    
    print("Total authorings: %s" % sum(authorCount.values()))
    print("Unique authors: %s" % len(authorCount))
    #print "Total authorings: {sum(authorCount.values())}"
    #print "Unique authors: {len(authorCount)}"

def papersSectionHeader(name, page):
    chunk = """

\\thispagestyle{empty}\\cleardoublepage
\\addcontentsline{toc}{section}{%s}
\\includepdf[pages=%s,pagecommand=\\thispagestyle{empty}]{external/12_Sessions.pdf}%%
\\thispagestyle{empty}\\cleardoublepage

""" % (name, page)
    return chunk

def latexEscape(string):
    return string.replace('#','\#').replace('_','\_').replace('$','\$').replace('&','\&').replace('%','\%')

def andToComma(string):
    return string.replace(' and ', ', ')


'''----------------------------------------------------'''

'''----------------------- generate electronic TSV file ----------------------'''    
def generateElectronicTsvFiles():
    copySessionIndex()
    generateSessionFiles()
    
def copySessionIndex():
    """Copy session_index file, created manually in excel.  Could
    maybe be created automatically from table of contents file from
    latex, but this is easier for now.

    """
    outFile = '2018_Proceedings_ISMIR_Electronic_Tools/data/session_index.txt'
    inFile  = 'data/session_index.txt'
    shutil.copy(inFile, outFile)
    
def generateSessionFiles():
    sessionInfo = loadSessionInfo()
    sessions = collections.defaultdict(list)
    for title, authors, number, session in unicode_tsv_reader('data/completePaperList.txt'):
        sessions[session].append((title, authors, int(number)))
    for session, info in sessions.items():      # Python 3
    #for session, info in sessions.iteritems():   # Python 2
        fileName = os.path.join('2018_Proceedings_ISMIR_Electronic_Tools/data',
                                '%s.txt' % session)
        makeDirs(os.path.dirname(fileName))
        with open(fileName, 'w', encoding='utf8') as sessionFile:
            sessionFile.write('Title\tAuthors\tFile\n')
            for title, authors, number in info:
                sessionFile.write('%s\t%s\t%d_Paper.pdf\n'
                                  % (title, andToComma(authors), number))

def makeDirs(path):
    sub_path = os.path.dirname(path)
    if sub_path == path:
        raise "sub_path == path: %s" % path
    if len(sub_path) > 0 and not os.path.exists(sub_path):
        makeDirs(sub_path)
    if not os.path.exists(path):
        os.mkdir(path)

'''-----------------------------------------------------------------------'''

                
def main():
    generatePapersDotTex()
    generateElectronicTsvFiles()
    shutil.copy('data/reviewers.txt',
                '2018_Proceedings_ISMIR_Electronic_Tools/data/reviewers.txt')


if __name__ == '__main__':
    main()
    
