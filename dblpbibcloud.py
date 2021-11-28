#!/usr/bin/python3
# -*- coding: latin-1 -*-

####
####  dblpbibcloud.py
####  based on bibcloud.py
####

# Copyright 2015-21 Ecole Polytechnique Federale Lausanne (EPFL)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

#
# dblpbibcloud :
#  -- all input arguments are in the code itself 
#  -- input: set of principal investigators (lab heads) with start date
#  -- input: set of conferences
#  -- input: exclusion list



import sys
import os
import xml.etree.ElementTree as ET
import subprocess
import time
import locale
import requests
import functools
import bibtexparser
import itertools

DEBUG = 0

AUTHORS = {
    "bugnion": {"dblp":"b/EBugnion"},
    "larus" :{"dblp":"l/JamesRLarus"},
    "candea" :{"dblp":"c/GeorgeCandea"},
    "argyraki": {"dblp":"71/6861"},
    "kashyap": {"dblp":"145/0912","year":2020},
    "ailamaki" : {"dblp":"a/AnastassiaAilamaki"},
    "guerraoui" :{"dblp":"g/RachidGuerraoui"},
    "kermarrec": {"dblp":"86/676"},
    "falsafi" : {"dblp":"f/BabakFalsafi"},
    "payer" : {"dblp":"31/1273"},
    "ford" : {"dblp":"f/BryanFord"}
}


CONFERENCES_ORG = [
    "ASPLOS",
    "SOSP", "OSDI", 
    "SIGCOMM", "NSDI",  "ISCA", "MICRO", 
    "SIGMOD", "VLDB", "PVLDB",
    "MobiCom", "MobiSys", "SenSys", "IMC", 
    "SIGMETRICS", 
    "PLDI", "CCS", "SP", "USS"
     #### not on George's orginal list
     "Eurosys"
     ]


CONFERENCES = [x.upper() for x in CONFERENCES_ORG]
DEBUG and print(CONFERENCES)


CONFERENCES_PRETTY = {
    "SP" : "IEEE Security and Privacy",
    "USS" : "USENIX Security"
}


############
### globals
############
 
PUBLICATIONS = {}
KEYPUBS = []
BIBALL = {}


#### added for dblpbbibcloud

def sort_lambda(a,b):
    if a["year"] == b["year"]:
        if a["conf"] < b["conf"]:
            return -1
        elif a["conf"] > b["conf"]:
            return 1
        else:
            return 0
    else:
        return b["year"]-a["year"]


def normalize_title(a):
    x = a.find("  ")
    if x==len(a)-1:
        return normalize_title(a[:x])
    elif x>=0:
        return normalize_title(a[:x]+a[x+1:])
    else:
        dot = a[len(a)-1]
        if dot == ".":
            b = a[:len(a)-1] 
            return b.lower()
        else:
            return a.lower()

def print_bibentry(p,b):
    F.write("@article{"+b["ID"]+",\n")
    F.write(" title={"+b["title"]+"},\n")
    F.write(" author={"+b["author"]+"},\n")
    F.write(" abstract={"+b["abstract"]+"},\n")
    F.write(" url={"+b["url"]+"},\n")
    conf = p["conf"].upper()
    if conf in CONFERENCES_PRETTY:
        conf = CONFERENCES_PRETTY[conf]
    if "venue_short" in b:
        F.write(" venue_short={"+b["venue_short"]+"}}\n\n\n")
    else:
        F.write(" venue_short={"+conf+" '"+str(p["year"]-2000)+"}}\n\n\n")


###################################################
#################### main  ########################
###################################################
# process bib file from ARVG
print("dbbibcloud: This is dblpbibcloud ... Use at your own risk ... see source for documentation")


if not os.path.exists(".bibcloud"):
    os.mkdir(".bibcloud")

for author in AUTHORS:
    print("Fetching author",author,AUTHORS[author])
    url = "https://dblp.org/pid/" + AUTHORS[author]["dblp"] + ".xml"
    f = requests.get(url)
    xml = ET.ElementTree(ET.fromstring(f.text))
    root = xml.getroot()
    for child in root:
        if child.tag == "r":
            for paper in child:
                key = paper.attrib['key']
                if key in PUBLICATIONS:
                    PUBLICATIONS[key]["authors"].append(author)
                else:
                    PUBLICATIONS[key] = {"xml":paper,"authors":[author]}
 

for p in PUBLICATIONS:
    x = p.split("/")
    xml = PUBLICATIONS[p]["xml"]
    authors = PUBLICATIONS[p]["authors"]
    if x[1].upper() in CONFERENCES:
        year = 0
        title = ""
        for c in xml:
            if c.tag == "year":
                year = int(c.text)
            if c.tag == "title":
                title = c.text
        year==0 and sys.exit("could not find year for "+str(p))
        title=="" and sys.exit("could not find title for "+str(p))
        keep = 0
        for a in authors:
            minyear = 2019
            if "year" in AUTHORS[a]:
                minyear = AUTHORS[a]["year"]
                DEBUG and print("adjuting min year for",a,minyear)
            if year >= minyear:
                keep = 1
        if keep:
            DEBUG and print("key",p,x[1],year,authors)
            KEYPUBS.append({
                "key": p,
                "conf": x[1],
                "year": year,
                "authors": authors,
                "title":normalize_title(title)
            })

KEYPUBS.sort(key=functools.cmp_to_key(sort_lambda))

for x in KEYPUBS:
    print("%4d %10s  %30s %20s %s"% (x["year"],x["conf"],x["authors"],x["key"],x["title"]))


## add lab-specific file here for those who don't use infoscience
## (e.g.,gannimo)
for filename in ["bib/misc.bib"]:
    with open(filename) as bibtex_file:
        bib_db = bibtexparser.load(bibtex_file)
        print("reading local bib file",len(bib_db.entries),"entries")
        for x in bib_db.entries:
            title = normalize_title(x["title"])
            found = 0
            for y in KEYPUBS:
                if y["title"] == title:
                    print("  -- found",y["key"])
                    y["bib"] = x
                    found = 1
            if found==0:
                print("   -- not found; inserted",x["venue_short"],x["year"]),
                KEYPUBS.append({"key": "NONE",
                "conf": x["venue_short"],
                "year": int(x["year"]),
                "authors": "NONE",
                "title":title,
                "bib":x})

#sort again
KEYPUBS.sort(key=functools.cmp_to_key(sort_lambda))


for author in AUTHORS:
    url = "https://infoscience.epfl.ch/search?ln=en&p="+author+"&f=&rm=&ln=en&sf=&so=d&rg=1000&of=btex&fct__1=Conference+Papers"
    f = requests.get(url)
    bib_db = bibtexparser.loads(f.text)
    print("infoscience",author,len(bib_db.entries),"entries")
    for x in bib_db.entries:
        title = normalize_title(x["title"])
        DEBUG and print("infoscience",author,title)
        if title in BIBALL:
            if (BIBALL[title]["ID"] == x["ID"]):
                DEBUG and print(" === multiple author for:"+title)
            else:
                print()
                print("!!!! Duplicateentries for title (1/2)"+title)
                print(BIBALL[title])
                print("!!!! Duplicate  entries for title (2/2) "+title)
                print(x)
        else:
            BIBALL[title] = x




F = open("bib/pubs.bib","w")
F.write("%% DO NOT EDIT\n")
F.write("%% Generated by dblpbibcloud.py\n")
for p in KEYPUBS:
    key = p["key"]
    title = p["title"]
    if title in BIBALL:
        DEBUG and print("  match for",key)
        if "bib" in p:
            # also found locally ... which should not be the case
            print()
            print()
            print("REMOVE from bib/misc.pub",p["bib"])

        if "abstract" in BIBALL[title]:
            print_bibentry(p,BIBALL[title])
        else:
            print("No abstract in infoscience for ",p,BIBALL[title])
    elif "bib" in p:
        DEBUG and print("Found locally")
        print_bibentry(p,p["bib"])
    else:
        print("nomatch for",p)

F.close()
sys.exit(0)
 


