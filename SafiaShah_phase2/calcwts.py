# Author: Safia Shah
# CMSC 476, Information Retrieval, Dr. Claudia Pearce
# Spring 2022
# Objective: Phase 2 of multiphase project

import os
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
import requests
import codecs
import re
import time


#global variables
H_DICT = {}   # dictionary - functions as the hash table in phase 1, and will be used to 
                # keep count of the words
stopwords = []
TERM_DICT = {} #dictionary to hold each documents number of terms

class Node:
    def __init__(self, freq, doc):
        self.freq= freq
        self.doc = doc
        self.next=None
        self.weight = 0 #default to 0

class linkedList:
    def __init__(self):
        self.head=None
      
    def insertAtEnd(self,freq, doc):
        temp=Node(freq, doc)
        if self.head==None:
            self.head=temp
        else:
            curr=self.head
            while curr.next!=None:
                curr=curr.next
            curr.next=temp
   
    def traverse(self):
        curr=self.head
        while curr!=None:
            print("Doc: {:<3}".format(curr.doc), " Freq: {:<6}".format(curr.freq), end= " ")
            curr=curr.next

    def countList(self):
        count = 0 
        curr= self.head
        while curr != None:
            count +=1
            curr = curr.next
        return count
    def computeWts(self, corpusNum, term_dict, df):# word):
        curr=self.head
        while curr!=None:
            pageSize = term_dict[curr.doc]
            tf = curr.freq / pageSize
            idf = corpusNum / df
            weight = tf * idf
            curr.weight = weight

           # if (word == "textplain"):
            #    print("term_dict[",curr.doc,"]: ", pageSize)
            #    print("size of corpus ", corpusNum)
            #    print("Doc: {:<3}".format(curr.doc), " Freq: {:<6}".format(curr.freq), "weight: ", curr.weight)
            
            curr=curr.next
    def writePostingsList(self, output_dir, word):
        curr=self.head
        while curr!=None:
            page = curr.doc
           # option "a" to append and not overwrite previous contents
            with open("{}/{:0>3}.wts".format(output_dir,page), "a") as f: 
                #print("word in write: ", word)
                f.write("{} {:.8f}\n".format(word,curr.weight))
            f.close()
            curr = curr.next


def write_dict(h_dict, filename):
    #write dictionary to a file
    with open(filename, 'w') as file: 
        for key, value in h_dict.items(): 
           file.write('%s %s\n' % (key, value))
   

def print_LLDict(h_dict):
      for word in h_dict:
        #print("this is index", n)
        print("{:<15}".format(word), end=' ')
        h_dict[word].traverse()
        print()

def print_dict(h_dict):
    #Print the contents of dictionary, used for temp dictionary
    for key in list(h_dict.keys()):
       print(key, ":", h_dict[key])

def write_to_dict(temp_dict, page):
    #write the current page's words and frequencies to the H_DICT
    for word in temp_dict:
        if word in H_DICT:
            H_DICT[word].insertAtEnd(temp_dict[word], page)
        else:
            H_DICT[word] = linkedList()
            H_DICT[word].insertAtEnd(temp_dict[word], page)


def parse(soup, page, output_dir, stopwords):
    output = soup.get_text()

    output = output.replace("\n", " ")
   
    output = output.split()
    
    temp_dict = {}

    numwords = 0
    for word in output:
        
        word = re.sub(r'\W+','', word)
        #word = re.sub(r'[0-9]','', word) #would then get rid of numbers within tokens
        
        word = word.lower()
        
        # make sure there are no empty indexes, and 
        # non-alphabetic values. this will not allow the inclusion of mixed alphamuneric strings
        # phase 2 additions: make sure length is > 1 and not a stopword
        if(word != '' and word.isalpha() == True and word not in stopwords and len(word) > 1):
            
            if word in temp_dict:
                temp_dict[word] = temp_dict[word] + 1 #add to the existings words frequency
            else:
                temp_dict[word] = 1
            numwords += 1
    TERM_DICT[page] = numwords #add the number of terms to the pages bucket
 
    write_to_dict(temp_dict, page) #write all terms to postings list dictionary


def editDict(H_dict, term_dict):
    #print original H_DICT
    term_array = []
    #print_LLDict(H_dict)
    #go through full corpus and get rid of buckets whose terms only have 1 file and the word freq in that file is 1 associated with them
    for word in H_DICT:
        count = H_dict[word].countList()
        #for each bucket, return count of the list
        if(count <= 1):
            page = H_dict[word].head.doc
            if(H_dict[word].head.freq == 1): 
            # subtract one from page number in term dict
                term_dict[page] -= 1
               # print("Page: ", page, " termfreq: ", term_dict[page], " word: ", word)
            # add words to term array to be using in deletion later
                term_array.append(word)
    #pop off words that are in term array (terms that occur once in the entire corpus).
    for i in term_array:
    #    print("term: ", i)
        H_dict.pop(i)
    
  #  print_LLDict(H_dict)
def computeWeights(H_DICT, TERM_DICT, totalPages, output_dir):
    #for each postings list in each bucket. calculate the words term weight for each document,
    #simultaneiously write to that document once that weight is complete
    for word in H_DICT:
        #need to traverse through each bucket in list
       # print("Word: ", word)
        df = H_DICT[word].countList()
      #  print("df: ", df)
        H_DICT[word].computeWts(totalPages, TERM_DICT, df)#, word)
      #  print()
        #write word into each of its document along with the words tf*idf score for that document
    for item in H_DICT:
        H_DICT[item].writePostingsList(output_dir, item)
        



def main():
    # get the input directory name and the output directory name
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help = "input directory name")
    parser.add_argument("output_dir", help = "output directory name")
    args = parser.parse_args()

    input_dir = str(args.input_dir)
    output_dir = str(args.output_dir)


    #load the stopwords from the given txt file into stopwords array
    stopFile = open('stoplist.txt', 'r')
    stopRead = stopFile.read()
    stopwords = stopRead.split()

    #remove strip non alpha characters from the stopwords. to make cmp easier
    stopwords = [re.sub(r'\W+' ,'', w) for w in stopwords]

    #page variable used in naming output files
    page = 1
    start = time.time()
    count = 1
    dir_loop = sorted(os.listdir(input_dir)) #sort the directory files, so outputs match the input file number
    for f in dir_loop:
        
        file = open("{}/{}".format(input_dir,f),'rb')
        # soup = BeautifulSoup(r.content, 'html5lib') 
        soup = BeautifulSoup(file, 'html.parser',from_encoding="iso-8859-1")

        parse(soup, page, output_dir, stopwords)
       
        if count == 503: #used when getting time for a certain number of files
            break;
        count +=1

        page += 1 # for output file num format and is used for the total number of documents
                   # as it will remain the number of the last document processed

    # remove words that occur once in the entire corpus
    editDict(H_DICT, TERM_DICT)

    #calculate tf*idf scores and write to the documents
    computeWeights(H_DICT, TERM_DICT, page, output_dir)
   # print_dict(TERM_DICT)
    print(TERM_DICT[1])
    end = time.time()

    timeResult = end - start
    print("Time: ", timeResult)


main()

