#!/usr/bin/env python
import hashlib
import urllib2
import re
from sys import argv

# Very simple md5 cracking with Google, idea taken from 
# https://github.com/juuso/BozoCrack/blob/master/BozoCrack.rb

# Feel free to use =)

class PyCrack:
    """ PyCrack tries to google each hash trying to find
	an occurrence """
    def __init__(self, filename):
        self.hashes = []
        fhandle = open(filename,'r')
        hash_list = fhandle.read()
        self.hashes = re.findall(r"([a-fA-F\d]{32})", str(hash_list))
        self.hashes = list(set(self.hashes))  # removes duplicates

    def dictionary_attack(self, hash, wordlist):
        flag = False
        for key in wordlist:
            if hashlib.md5(key).hexdigest() == hash:
                result = "%s:%s" % (hash,key,)
                print result
                flag = True
                return result
        if flag == False:
            notfound = "Hash "+hash+" not found."
            print notfound

    def crack_single_hash(self):
        wordlist = []
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]

        for hash in self.hashes:
            try:
                sivu = opener.open('http://www.google.com/search?q='+hash+'', timeout=10)
            except urllib2.URLError:
                print "URL error."
                continue
            for word in re.split(r"\s+", str(sivu.read())):
                    wordlist.append(word)
            save = self.dictionary_attack(hash, wordlist)
            if save:
                f = open('output.txt', 'a+')
                f.write(save + '\n')  # saves output to file

# usage example

if __name__ == "__main__":
    if len(argv) > 1:
	filename = argv[1]
    else:
        filename = raw_input("File: ")  # file to search for hashes
    instance = PyCrack(filename = filename)
    instance.crack_single_hash()


