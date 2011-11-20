#!/usr/bin/env python
import hashlib
import urllib2
import re
import logging
from sys import argv
from libs.db import *

# Very simple md5 cracking with Google, idea taken from
# https://github.com/juuso/BozoCrack/blob/master/BozoCrack.rb

# Feel free to use =)

class PyCrack:
    """ PyCrack tries to google each hash trying to find
	an occurrence """
    def __init__(self, filename, wordlist = None):
        # Logger
        logging.basicConfig(
          level=logging.DEBUG,
          format='(%(threadName)-10s) %(message)s')
        self.logger = logging.getLogger()
        
        # Open hash file
        fhandle = open(filename,'r')
        hash_list = fhandle.read()
        
        # Get all the hashes.
        hashes = re.findall(r"([a-fA-F\d]{32})", str(hash_list))
        self.hashes = list(set(hashes))  # removes duplicates
        
        # Initialize wordlists
        self.wordlist = self.init_wordlist(wordlist)
        self.slicedWordlist = []
        
        # Urllib2 client
        self.opener = urllib2.build_opener()
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        self.default_timeout = 20
        
        # File handlers
        self.found_file = open('results/found.txt', 'a+')
        self.not_found_file = open('results/notfound.txt', 'a+')
        self.result_file  = open('results/results.txt', 'a+')
        
        # How many Google result pages to crawl
        self.pages = 2
        
        # Statistics :)
        self.found_counter = 0
        
        # Initialize sqlite db
        self.db = HashDatabase()
    
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
    
    def dictionary_attack(self, hash, wordlist, save):
        """ Goes throught the wordlist hash trying to find the hash. """
        occurrences = False
        for key in wordlist:
            if hashlib.md5(key).hexdigest() == hash:
                result = "%s:%s" % (hash,key,)
                print "    Found %s " % result
                occurrences = True
                # Saves hash to "found" list
                self.found(hash)
                # Saves result to results.txt
                self.save_result(result)
                self.db.hash(hash,key)
                return result
        if occurrences == False:
            notfound = "    Hash not found."
            print notfound
            # Saves hash to "not found" list
            if save == True:
                self.not_found(hash)
        return False

    def query_db(self, hash):
        key = self.db.hash(hash)
        if key == False or key == None:
            return False
        result = "%s:%s" % (hash,key,)
        print "    Found %s " % result
        
        # Saves hash to "found" list
        self.found(hash)
        # Saves result to results.txt
        self.save_result(result)
        return result
    
    def crack_hashes(self):
        """ Main function for searching the hashes. """
        from pprint import pprint
        for hash in self.hashes:
            print
            print "Starting search for: %s" % hash
            try:
                print "    Querying from local database.."
                result = self.query_db(hash)
                
            except:
                pass

            if result == False:
                print "    Starting Google crack..."
                for i in range(0,self.pages):
                    if self.pages > 1:
                        print "    Google crack, page %s/%s..." % (i+1,self.pages)
                    result = self.google_crack(hash, i)
                    # if not found, tries to parse results more
                    if result == False:
                        print "    Trying extended parser..."
                        result = self.extended_google_crack(hash, self.wordlist)
                        if result != False:
                            break
                    else:
                        break
            
            if result == False:
                print "    Falling back to MD5 site search..."
                result = self.reverse_site_search(hash)
    
    def reverse_site_search(self, hash):
        """ Polls various websites for hashes """
        
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
            result = self.dictionary_attack(hash, self.wordlist, True)
            return result

    def google_crack(self, hash, page):
        """ Do a google search for the hash and add found words to the wordlist """
        try:
            page_handle = self.opener.open('http://www.google.com/search?q=%s&start=%s' \
                                    % (hash,page*10), timeout=self.default_timeout)
        except urllib2.URLError as e:
            self.logger.warn("URL error %s", e.message)
            return False
            
        # Read page to a string
        google_wordlist = re.split(r"\s+", str(page_handle.read()))
        
        for word in google_wordlist:
            self.wordlist.append(word)
        result = self.dictionary_attack(hash, self.wordlist, False)
        return result
		
    def extended_google_crack(self, hash, wordlist):
        cache = []
        
        # splits wordlist into smaller chunks
        for i in range(0, len(wordlist)):
            cache.append(wordlist[i].split(":"))
        for i in range(0, len(cache)):
            self.slicedWordlist.extend(wordlist[i].split("."))
            
        result = self.dictionary_attack(hash, self.slicedWordlist, False)
        return result
            
# usage example

if __name__ == "__main__":
    if len(argv) > 1:
        filename = argv[1]
    else:
        filename = raw_input("File: ")  # file to search for hashes
    instance = PyCrack(filename = filename)
    instance.crack_hashes()