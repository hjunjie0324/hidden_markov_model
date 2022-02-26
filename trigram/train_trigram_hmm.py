#!/usr/bin/python

# Junjie Han
# 2020-5

# Junjie Han
# 2020-5
# Code for maximum likelihood estimation of a trigram HMM from 
# column-formatted training data.

# Usage:  train_trigram_hmm.py tags text > hmm-file

# The training data should consist of one line per sequence, with
# states or symbols separated by whitespace and no trailing whitespace.
# The initial and final states should not be mentioned; they are 
# implied.  
# The output format is the HMM file format as described in viterbi.pl.

import sys,re
from itertools import izip
from collections import defaultdict
import random

TAG_FILE=sys.argv[1]
TOKEN_FILE=sys.argv[2]

vocab={}
OOV_WORD="OOV"
INIT_STATE="init"
#INIT_STATE0="init0"
#INIT_STATE1="init1"
FINAL_STATE="final"

SPECIAL_STATE="special"

emissions={}
transitions={}
transitionsTotal=defaultdict(int)
emissionsTotal=defaultdict(int)

states=set()

#number of lines is 39832
with open(TAG_FILE) as tagFile, open(TOKEN_FILE) as tokenFile:
	for tagString, tokenString in izip(tagFile, tokenFile):
		tags=re.split("\s+", tagString.rstrip())
		tokens=re.split("\s+", tokenString.rstrip())

		pairs=zip(tags, tokens)

		#prevtag=INIT_STATE
		prevtag0=INIT_STATE
		prevtag1=INIT_STATE

		for (tag, token) in pairs:

			# this block is a little trick to help with out-of-vocabulary (OOV)
			# words.  the first time we see *any* word token, we pretend it
			# is an OOV.  this lets our model decide the rate at which new
			# words of each POS-type should be expected (e.g., high for nouns,
			# low for determiners).

			"""
			if token not in vocab:
				vocab[token]=1
				token=OOV_WORD
			"""
			
			
			if token not in vocab:
				vocab[token]=1
				if random.random()<0.01:
					token=OOV_WORD
			

			if tag not in emissions:
				emissions[tag]=defaultdict(int)
			states.add(tag)
			#prevtag = prevtag0 + prevtag1
			if prevtag0 not in transitions:
				transitions[prevtag0]={}
			if prevtag1 not in transitions[prevtag0]:
				transitions[prevtag0][prevtag1]=defaultdict(int)
			if prevtag0 not in transitionsTotal:
				transitionsTotal[prevtag0]=defaultdict(int)

			# increment the emission/transition observation
			emissions[tag][token]+=1
			emissionsTotal[tag]+=1
			
			transitions[prevtag0][prevtag1][tag]+=1
			transitionsTotal[prevtag0][prevtag1]+=1

			#prevtag=tag
			prevtag0 = prevtag1
			prevtag1 = tag

		# don't forget the stop probability for each sentence
		if prevtag0 not in transitions:
			transitions[prevtag0]={}
		if prevtag1 not in transitions[prevtag0]:
			transitions[prevtag0][prevtag1]=defaultdict(int)
		if prevtag0 not in transitionsTotal:
			transitionsTotal[prevtag0]=defaultdict(int)

		transitions[prevtag0][prevtag1][FINAL_STATE]+=1
		transitionsTotal[prevtag0][prevtag1]+=1


"""
for prevtag in transitions:
	for tag in transitions[prevtag]:
		print "trans %s %s %s" % (prevtag, tag, float(transitions[prevtag][tag]) / transitionsTotal[prevtag])
"""


for prevtag0 in transitions:
	for prevtag1 in transitions[prevtag0]:
		taglist = set()
		for tag in transitions[prevtag0][prevtag1]:
			if transitions[prevtag0][prevtag1][tag]>0:
				taglist.add(tag)
				v = len(states)
				print "trans %s %s %s %s" % (prevtag0,prevtag1,tag,float(transitions[prevtag0][prevtag1][tag]+0.1)/(transitionsTotal[prevtag0][prevtag1]+0.1*v))
		tag_remained=states-taglist
		for tag in tag_remained:
			v = len(states)
			print "trans %s %s %s %s" % (prevtag0,prevtag1,tag,float(0.1)/(transitionsTotal[prevtag0][prevtag1]+0.1*v))

"""
for prevtag0 in transitions:
	for prevtag1 in transitions[prevtag0]:
		for tag in transitions[prevtag0][prevtag1]:
			if transitions[prevtag0][prevtag1][tag]>0:
				print "trans %s %s %s %s" % (prevtag0,prevtag1,tag,float(transitions[prevtag0][prevtag1][tag])/transitionsTotal[prevtag0][prevtag1])
"""

for tag in emissions:
	for token in emissions[tag]:
		print "emit %s %s %s " % (tag, token, float(emissions[tag][token]) / emissionsTotal[tag])



