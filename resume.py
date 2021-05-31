import pickle
import re
import os, time
import optparse
import codecs
from threading import Thread


class FileSearcher:

  def __init__(self, filelist, searchstr):
    self.filelist = filelist
    self.searchstr = searchstr
    self.curfile = 0
    self.curline = 0
    self.file = open(self.filelist[self.curfile], encoding='utf8')
    self.results = []
    self.done = False

  def isDone(self):
    return self.done
  
  def getResults(self):
    return self.results

  def getCurrent(self):
    return "Files done:" + str(self.curfile) + \
            "/" + str(len(self.filelist)) + \
            "\nCurrent File: " + self.filelist[self.curfile] + \
            "\nCurrent line: " + str(self.curline)

  def searchLine(self):
    self.curline += 1
    #print(self.curline)
    line = self.file.readline()
    if not line: # No more lines in this file
      self.curfile += 1 # Move to next file
      if not self.curfile < len(self.filelist): # If there are no more files?
        self.done = True # Done with last line in the last file
        print("Done searching. Printing results...")
        return # Exits function
      self.curline = 0
      self.file.close()
      self.file = open(self.filelist[self.curfile], encoding='utf8')
    # Going to try to search with just for in blah right here after comment out searchResult line
    
    
    # This is the old way to search the line for the string
    searchResult = re.search( self.searchstr, line, re.M|re.I) # Flags for multiline and ignore case

    if searchResult: # If the word is found, add it to the results list
      self.results.append(self.filelist[self.curfile] + ", line: " + str(self.curline))

  def __getstate__(self):
    tempDict = self.__dict__.copy()
    del tempDict['file']
    return tempDict

  def __setstate__(self, dict):
    listTemp = dict['filelist']
    ftemp = open(listTemp[dict['curfile']], encoding='utf8')
    for i in range(dict['curline']):
      ftemp.readline()
    self.__dict__.update(dict)
    self.file = ftemp


# FIXME: Was this placed outside of class FileSearcher on purpose?
def SaveProgress(obj, filename):
  with open(filename, 'wb') as out:
    pickle.dump(obj, out)


def Main():

  # Start timer
  start = time.time()

  parser = optparse.OptionParser("No inputs detected. Correct usage: python pubmed-searcher "+"-w <word> -d <dir>")
  parser.add_option('-w', dest='word', type='string', help='specify word to search for')
  parser.add_option('-d', dest='dir', type='string', help='specify dir to search')
  (options, args) = parser.parse_args()
  if (options.word == None) | (options.dir == None):
    print(parser.usage)
    exit(0)
  else:
    word = options.word
    print()
    path = options.dir
    print("Searching for occurrences of '{}' within '{}'".format(word, path))
    print()
  
  if os.path.isfile("sData.pkl"):
    # Had to add 'rb' here because there was decoding issue. That solved it I think
    with open("sData.pkl", 'rb', encoding='utf8') as infile:
      searcher = pickle.load(infile)
    print("Resuming at: \n")
    print(searcher.getCurrent())
  else:
    files = []
    for (dirpath, dirnames, filenames) in os.walk(path):
      for fpath in filenames:
        if fpath.endswith(".txt"):
          fpath = dirpath + "/" + fpath
          files.append(fpath)
          print("Currently appending path: '{}'".format(fpath))
    searcher = FileSearcher(files, word)
    print("searching...")

  while not searcher.isDone():
    searcher.searchLine()
    t1 = Thread(target=SaveProgress, args=(searcher, "sData.pkl"))
    t1.start()
    #time.sleep(0.05)

  for i in searcher.getResults():
    print(i)
      
  time.sleep(0.5)
  os.remove("sData.pkl")

  end = time.time()
  print("Time spent searching: '{}'".format(end - start))


if __name__ == '__main__':
  Main()
