import hashlib
import urllib2
import re

# Very simple md5 cracking with Google, idea taken from 
# https://github.com/juuso/BozoCrack/blob/master/bozocrack.rb

# Feel free to use =)

class BozoCrack:

	def __init__(self):
		self.hashes = []
		filename = raw_input("File: ") # file to search for hashes
		filee = open(filename,'r')
		filee = filee.read()
		self.hashes = re.findall(r"([a-fA-F\d]{32})", str(filee))
		self.hashes = list(set(self.hashes)) # removes duplicates

	def dictionary_attack(self, hash, wordlist):
		flag = False
		for key in wordlist:
			if hashlib.md5(key).hexdigest() == hash:
				result = ""+hash+":"+key+""
				print result
				return result
				flag = True
				break
		if flag == False:
			notfound = "Hash "+hash+" not found."
			print notfound
			return notfound
		
	def crack_single_hash(self):
		wordlist = []
		for hash in self.hashes:
			opener = urllib2.build_opener()
			opener.addheaders = [('User-agent', 'Mozilla/5.0')]
			try:
				sivu = opener.open('http://www.google.com/search?q='+hash+'', timeout=10)
			except urllib2.URLError:
				print "URL error."
				pass
			for word in re.split(r"\s+", str(sivu.read())):
				wordlist.append(word)
			save = self.dictionary_attack(hash, wordlist)
			f = open('output.txt', 'a+')
			f.write(save + '\n') # saves output to file
			
# usage example

instance = BozoCrack()
instance.crack_single_hash()