# Author: Safia Shah
# CMSC 476, Information Retrieval, Dr. Claudia Pearce
# Spring 2022
# Objective: Phase 4 of multiphase project

import os
import argparse
from pathlib import Path
from turtle import clear
from bs4 import BeautifulSoup
import requests
import codecs
import re
import time
import sys
import linecache
import operator
import math


#global variables
H_DICT = {}   # dictionary - functions as the hash table in phase 1, and will be used to 
                # keep count of the words
corpusSize =503


class dictInfo:
     def __init__(self, word, count, startLine):
         self.word = word
         self.count = count
         self.startLine = startLine

class Node:
    def __init__(self, doc, weight):
        self.weight = weight
        self.doc = doc
        self.next=None
        

class linkedList:
    def __init__(self):
        self.head=None
      
    def insertAtEnd(self, doc, weight):
        temp=Node(doc, weight)
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
            print("Doc: {:<3}".format(curr.doc), " Weight: {0:.8f}".format(curr.weight), end= "\n")
            curr=curr.next

    def countList(self):
        count = 0 
        curr= self.head
        while curr != None:
            count +=1
            curr = curr.next
        return count
    def compNumDen(self, cosineSim, query, word, denominator):
        curr=self.head
        while curr!=None:
        #full form DEN: SQRT( (wt(Q,w1)^2 + wt(Q,w2)^2 ) * SQRT(wt(doc_id,w1)^2 + wt(doc_id,w2)^2 )) (depending on num of queries)
        # Numerator = DOT(weight of query term j * weight of term in corpus j)
            cosineSim[curr.doc] += (query[word] * curr.weight)
            denominator[curr.doc] += curr.weight**2 #sq each of the term weights for each query in the doc
            #print("current denom value: ", denominator[curr.doc])
            #print("current doc: ", curr.doc, "query[word]: ", query[word], "cosineSim: ", cosineSim[curr.doc], "doc weight: ", curr.weight)
            curr=curr.next 

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

def printDictInfo(infoDict):
    for key in list(infoDict.keys()):
       print(key, ":", infoDict[key].word , " count: ", infoDict[key].count, " startLine", infoDict[key].startLine )


def parseQuery(arguments, dict):
    
    counter = 2 # counter starts at 2 bc 0 => .py filename, 1 => will be a weight, 2=>first query word 
    while(counter <= len(sys.argv)):
        if(counter % 2 == 0): # if the index is an even number then its a query, counter -1 = wt
            word = arguments[counter]
          # stripped = re.sub(r'[0-9]' ,'', word)
          # query[stripped] = arguments[counter-1]
            word = word.lower()
            dict[word] = float(arguments[counter-1])
        counter += 2 #increment by 2 to go to the next query word (skip the weight)
    
def getDictValue(query,dictResp):
    count = 0

    with open("dictionary.txt", 'r') as dictFile:
        for line in dictFile:
            
            line = line.strip() #get rid of newline char, present in the file, dictionary values come in sets of 3 pieces of data
            if (line in query):
                indexCount = int(next(dictFile).strip()) #next line after query word in the dict is the number of buckets
                startL = int(next(dictFile).strip()) #the line after the num of buckets is the start line in the postings list
                print(line, " ", indexCount, " ", startL)
                dictResp[line] = dictInfo(line, indexCount, startL)
            #print(count)
            # count += 1
            # if(count == 45):
            #     break 

def getPostValue(dictResp, H_DICT):
    # Using values from dictResp, find the corresponding data from the postings file and create H_DICT inverted index
    with open("postings_file.txt", 'r') as postingsFile:
        for key in dictResp:
        
            if key not in H_DICT: #since its a query, even if it occursmore than once, will only get a term once
                count = 1

                H_DICT[key] = linkedList()
              
                for i in range(dictResp[key].count):
                    getFirst = linecache.getline("postings_file.txt", dictResp[key].startLine+i)
                    getFirst = getFirst.strip()
                    id_weight = getFirst.split(',')
                    H_DICT[key].insertAtEnd(int(id_weight[0]),float(id_weight[1])) #made id an int var this time to match, cosineSim doc id intitialization
                   # print(count,". ",key, " ", id_weight[0], " ", id_weight[1]) #indx 0 is the doc_id, index 2 is the weight
                    count += 1
def sort_dictionary_values(h_dict):
    #sort dictionary by values, aka by the frequency. variable is a temp dictionary
    sortByValue = dict(sorted(h_dict.items(), key=operator.itemgetter(1),reverse=True))
    
    #print_dict(sortByValue)

    count = 1 #print out top 10 cosine sim scores
    for key in list(sortByValue.keys()):
        
        print("{:0>3}.html".format(key), ": ", sortByValue[key])
        if count == 12:
            break
        count +=1


def finishCosSim(query, H_DICT, cosineSim, denominator):
    # full form SQRT( (wt(Q,w1)^2 + wt(Q,w2)^2 ) * SQRT(wt(doc_id,w1)^2 + wt(doc_id,w2)^2 )) (depending on num ofqueries)
    queryWeightSQ = 0
    for word in query: #this will be the same for all files
        queryWeightSQ += query[word] * query[word] #for each query word, access the weight^2 and add alternative -> (query[word]**2)
    queryWeightSQ = math.sqrt(queryWeightSQ)
    #print(queryWeightsSQ)
   
    for id in cosineSim:
       # print(cosineSim[id], " ", queryWeightSQ * math.sqrt(denominator[id] ))

        if cosineSim[id] != 0:  #meaning the queries existed in this document
            #print(cosineSim[id], " ", queryWeightSQ, " ", math.sqrt(denominator[id] ))
            newValue = cosineSim[id] / (queryWeightSQ * math.sqrt(denominator[id]))
            cosineSim[id] = newValue

  
def main():

    # no input directory or output directories
    # first index of cmd line arguments will always be the file name
    # extra cred for term weight inclusion and managing things between disk and memory
    arguments = sys.argv
    #print("The filename:", arguments[0])
    #variables not including H_DICT - inverted index (made as a global variable)
    cosineSim = {key: 0 for key in range(corpusSize+1)} #holds the doc ids and their partials scores till its done, or could be a array?
    denominator = {item: 0 for item in range(corpusSize+1)} #will hold denom values for final computation
    #cosineSim = [0] * corpusSize #list to store partial scores, index of this list will be the doc_id
    query = {}
    dictResp = {}
    

    #parse the query words and their weights, store into query dictioanry
    parseQuery(arguments, query)
   # print_dict(query)

    # Find and store the query words and their corresponding data within the dictResp dictionary
    getDictValue(query,dictResp)       
    # printDictInfo(dictResp)

    # Using values from dictResp, find the corresponding data from the postings file and create H_DICT inverted index
    getPostValue(dictResp,H_DICT)
    # print_LLDict(H_DICT)
 
    # loop terms in query or inverted index. going to need both (will skip index 0, since no doc id are = 0)
    for word in query: #loop through each query terms LL and add all dot products
        if word in H_DICT:
            H_DICT[word].compNumDen(cosineSim, query, word, denominator) #partial sums computed by doing DOT prod and adding for each term into cosineSIm 
        else:
            print(word, " does not exist in this dictionary, so will not be used")

    finishCosSim(query, H_DICT, cosineSim, denominator)

    sort_dictionary_values(cosineSim) #sorting after so the traversal of cosineSim can be in order so finding docs are in order)

    #  for n in range(len(cosineSim)): #printing the cosSim values for TaaT
        #     print(n, " ", cosineSim[n])
main()

