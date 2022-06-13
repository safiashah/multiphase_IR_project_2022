# Author: Safia Shah
# CMSC 476, Information Retrieval, Dr. Claudia Pearce
# Spring 2022
# Objective: this program is a baby tokenizer - gets rid of special characters, downcases, and only keeps all alphabetic words
# the option for (1) keeping alphanumeric characters, (2)different parser type, (3)different encoding type are all included
# but commented out in their respective places. 

import os
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
import requests
import codecs
import re
import time


#global variable
H_DICT = {}   # dictionary - functions as the hash table in phase 1, and will be used to 
                # keep count of the words

def write_dict(h_dict, filename):
    #write dictionary to a file
    with open(filename, 'w') as file: 
        for key, value in h_dict.items(): 
           file.write('%s %s\n' % (key, value))
   
def print_dict(h_dict):
    #Print the contents of dictionary
    for key in list(h_dict.keys()):
       print(key, ":", h_dict[key])

def sort_dictionary_keys(h_dict, filename):
    #sort dictionary by key/ token words, variable is a temp dictionary
    sortByKey = {k: v for k, v in sorted(h_dict.items())}
    write_dict(sortByKey, filename)

def sort_dictionary_values(h_dict, filename):
    #sort dictionary by values, aka by the frequency. variable is a temp dictionary
    sortByValue = {k: v for k, v in sorted(h_dict.items(), key=lambda v: v[1])}
    write_dict(sortByValue, filename)
    
def parse(soup, page, output_dir):
    output = soup.get_text()

    output = output.replace("\n", " ")
   
    output = output.split()

    with open("{}/{:0>3}_file.txt".format(output_dir,page), "w") as f:

        for word in output:
            word = re.sub(r'\W+','', word)
            #word = re.sub(r'[0-9]','', word) #would then get rid of numbers within tokens
            word = word.lower()

            #if(word != '' and word.isdigit() == False) #-> this consitional will allow the inclusion of alphanumeric tokens, but no numbers on its own
            
            # make sure there are no empty indexes, and 
            # non-alphabetic values. this will not allow the inclusion of mixed alphamuneric strings
            if(word != '' and word.isalpha() == True):

                if word in H_DICT:
                    H_DICT[word] = H_DICT[word] + 1
                else:
                    H_DICT[word] = 1

                f.write(word+'\n') #write the tokenizes and downcased word to the new file
                

    f.close()

def main():
    
    # get the input directory name and the output directory name
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help = "input directory name")
    parser.add_argument("output_dir", help = "output directory name")
    args = parser.parse_args()

    input_dir = str(args.input_dir)
    output_dir = str(args.output_dir)

    #page variable used in naming output files
    page = 1
    start = time.time()
  
    dir_loop = sorted(os.listdir(input_dir)) #sort the directory files, so outputs match the input file number
    count = 1
    for f in dir_loop:
        
        file = open("{}/{}".format(input_dir,f),'rb')
        # soup = BeautifulSoup(r.content, 'html5lib') 
        soup = BeautifulSoup(file, 'html.parser')#,from_encoding="iso-8859-1")
       # soup = BeautifulSoup(file, 'html.parser') #from_encoding="UTF-8") #utf-8 is the default, so doesnt need to be specified

       # print("Page: ", page)
        parse(soup, page, output_dir)
       
        page += 1 # for output file num format

        if count == 503: #used when getting time for a certain number of files
            break;
        count +=1

    sort_dictionary_keys(H_DICT, "{}/sorted_key.txt".format(output_dir))
    sort_dictionary_values(H_DICT, "{}/sorted_value.txt".format(output_dir))
    end = time.time()

    timeResult = end - start
    print("Time: ", timeResult)

main()

