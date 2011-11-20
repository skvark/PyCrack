## PyCrack
The idea behind this rather simple piece of software can be found from here:      

[BozoCrack](https://github.com/juuso/BozoCrack)

Differences:

* Sqlite3 support
* Logging support
* Option to crawl multiple Google result pages
    * Uses multiple different characters as delimiters when parsing results
* Uses some MD5 search engines as a fallback, if Google does not give desired results

### Usage 

Just run the script and specify a file which contains md5 hashes.

Example:     
 
    python pycrack.py hashes.txt    

    or
     
    python pycrack.py        

Output will be saved to results.txt, notfound.txt and found.txt.      
Script prints into command line too.

Some hashes for testing:

     fcf1eed8596699624167416a1e7e122e
     bed128365216c019988915ed3add75fb
     d0763edaa9d9bd2a9516280e9044d885
     dfd8c10c1b9b58c8bf102225ae3be9eb
     ede6b50e7b5826fe48fc1f0fe772c48f
     1ad99cbe9e425d4f19c53a29d4f12597
     ff384074e7a9c58ee229a82e0d870410

## License

Public domain, feel free to use, modify etc. =)