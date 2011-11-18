#!/usr/bin/env python
import hashlib
import urllib2
import re
import logging
from sys import argv

# Very simple md5 cracking with Google, idea taken from
# https://github.com/juuso/BozoCrack/blob/master/BozoCrack.rb

# Feel free to use =)

class PyCrack:
    """ PyCrack tries to google each hash trying to find
	an occurrence """
    def __init__(self, filename, wordlist = None):
        logging.basicConfig(
          level=logging.DEBUG,
          format='(%(threadName)-10s) %(message)s')
        self.logger = logging.getLogger()
        self.hashes = []
        fhandle = open(filename,'r')
        hash_list = fhandle.read()
        hashes = re.findall(r"([a-fA-F\d]{32})", str(hash_list))
        self.hashes = list(set(hashes))  # removes duplicates
        
        # Initialize wordlist
        self.wordlist = self.init_wordlist(wordlist)
        
        # Urllib2 client
        self.opener = urllib2.build_opener()
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        self.default_timeout = 20
        
        # File handlers
        self.found_file = open('results/found.txt', 'a+')
        self.not_found_file = open('results/notfound.txt', 'a+')
        self.result_file  = open('results/results.txt', 'a+')
        
        # Statistics :)
        self.found_counter = 0
    
    def init_wordlist(self, wl):
        """ Todo: Load some wordlist here, from sqlite/textfile or such """
        return []
    
    def found(self, result):
        """ Writes found string to file """
        if result:
            self.found_file.write(result + '\n')
            self.found_counter += 1
    
    def not_found(self, result):
        """ Writes to "not found" file """
        if result:
            self.not_found_file.write(result + '\n')
    
    def save_result(self, result):
        """Saves found hash to output.txt"""
        if result:
            self.result_file.write(result + '\n')
    
    def dictionary_attack(self, hash, wordlist):
        """ Goes throught the wordlist hash trying to find the hash. """
        occurrences = False
        for key in wordlist:
            if hashlib.md5(key).hexdigest() == hash:
                result = "%s:%s" % (hash,key,)
                print "Found %s " % result
                occurrences = True
                # Saves hash to "found" list
                self.found(hash)
                # Saves result to results.txt
                self.save_result(result)
                return result
        if occurrences == False:
            notfound = "Hash %s not found." % hash
            print notfound
            # Saves hash to "not found" list
            self.not_found(hash)
        return False

    def crack_hashes(self):
        for hash in self.hashes:
            print
            print "Starting Google crack"
            result = self.google_crack(hash)
            if result == False:
                print "Falling back to MD5 site search"
                result = self.reverse_site_search(hash)

    
    def reverse_site_search(self, hash):
        md5_crackers = ['http://md5.thekaine.de/?hash=',
                        'http://md5.rednoize.com/?&s=md5&go.x=0&go.y=0&q=']
        for site in md5_crackers:
            try:
                page_handle = self.opener.open('%s%s' % (site,hash), \
                                timeout=self.default_timeout)
            except urllib2.URLError as e:
                self.logger.warn("URL error %s", e.message)
                return
                
            # Read page to a string
            site_wordlist = re.split(r"\s+", str(page_handle.read()))

            for word in site_wordlist:
                self.wordlist.append(word)
            result = self.dictionary_attack(hash, self.wordlist)
            return result

    def google_crack(self, hash):
        """ Do a google search for the hash and add found words to the wordlist """
        try:
            page_handle = self.opener.open('http://www.google.com/search?q=%s' \
                                    % hash, timeout=self.default_timeout)
        except urllib2.URLError as e:
            self.logger.warn("URL error %s", e.message)
            return False
            
        # Read page to a string
        google_wordlist = re.split(r"\s+", str(page_handle.read()))
        
        for word in google_wordlist:
            self.wordlist.append(word)
        result = self.dictionary_attack(hash, self.wordlist)
        return result

# usage example

if __name__ == "__main__":
    if len(argv) > 1:
	filename = argv[1]
    else:
        filename = raw_input("File: ")  # file to search for hashes
    instance = PyCrack(filename = filename)
    instance.crack_hashes()


