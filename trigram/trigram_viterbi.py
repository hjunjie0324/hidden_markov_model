#!/usr/bin/python
#Junjie Han

import sys,re
from collections import defaultdict
import math
import random

HMM_FILE = sys.argv[1]
TEXT_FILE = sys.argv[2]

INIT_STATE0="init"
INIT_STATE1="init"
FINAL_STATE="final"
OOV_WORD="OOV"

transitions=defaultdict()
emissions=defaultdict()

states=set()
voc=set()

#read the HMM file and store the probability as log probability
with open (HMM_FILE) as hmm_file:
    for train_data in hmm_file:
        data=re.split("\s+",train_data.rstrip())
        if data[0] == "trans":
            prevTag0 = data[1]
            prevTag1 = data[2]
            currTag = data[3]
            tranProb = math.log(float(data[4]))
            if prevTag0 not in transitions:
                transitions[prevTag0]=defaultdict()
            if prevTag1 not in transitions[prevTag0]:
                transitions[prevTag0][prevTag1]=defaultdict(int)
            transitions[prevTag0][prevTag1][currTag]=tranProb
            states.add(prevTag0)
            states.add(prevTag1)
            states.add(currTag)
        elif data[0]=="emit":
            tag = data[1]
            token = data[2]
            emiProb = math.log(float(data[3]))
            states.add(tag)
            voc.add(token)
            if tag not in emissions:
                emissions[tag]=defaultdict(int)
            emissions[tag][token]=emiProb

#tag text data
with open (TEXT_FILE) as text_file:
    for text in text_file:
        tokens=re.split("\s+", text.rstrip())
        n = len(tokens)
        backpointer={}
        viterbi={}

        for i in range(n):
            viterbi[i]=defaultdict(int)
            if tokens[i] not in voc:
                tokens[i]=OOV_WORD
        viterbi[n]={}
        viterbi[n+1]={}
        #base case for dynamic programming
        viterbi[0][INIT_STATE0] = 0.0
        viterbi[1][INIT_STATE1] = 0.0

        for i in range(2,n+2):
            backpointer[i]={}
            for currState in states:
                #viterbi[i][currState] = defaultdict(int)
                #backpointer[currState]={}
                for prevState1 in viterbi[i-1]:
                    if i>2:
                        for prevState0 in viterbi[i-1][prevState1]:
                            if prevState0 in transitions and prevState1 in transitions[prevState0] and currState in transitions[prevState0][prevState1] and currState in emissions and tokens[i-2] in emissions[currState]:
                                v = viterbi[i-1][prevState1][prevState0] + transitions[prevState0][prevState1][currState] + emissions[currState][tokens[i-2]]
                        
                                if currState not in viterbi[i]:
                                    viterbi[i][currState] = {}

                                if prevState1 not in viterbi[i][currState]:
                                    viterbi[i][currState][prevState1] = v
                                    if currState not in backpointer[i]:
                                        backpointer[i][currState]={}
                                    backpointer[i][currState][prevState1]=prevState0

                                elif v>viterbi[i][currState][prevState1]:
                                    viterbi[i][currState][prevState1] = v
                                    backpointer[i][currState][prevState1]=prevState0
                                

                    if i==2:
                        for prevState0 in viterbi[i-2]:
                             if prevState0 in transitions and prevState1 in transitions[prevState0] and currState in transitions[prevState0][prevState1] and currState in emissions and tokens[i-2] in emissions[currState]:
                                v = viterbi[i-1][prevState1] + transitions[prevState0][prevState1][currState] + emissions[currState][tokens[i-2]]
                                if currState not in viterbi[i]:
                                    viterbi[i][currState] = {}
                                if prevState1 not in viterbi[i][currState]:
                                    viterbi[i][currState][prevState1] = v
                                    if currState not in backpointer[i]:
                                        backpointer[i][currState]={}
                                    backpointer[i][currState][prevState1]=prevState0
                                elif v>viterbi[i][currState][prevState1]:
                                    viterbi[i][currState]={}
                                    viterbi[i][currState][prevState1] = v
                                    backpointer[i][currState][prevState1]=prevState0
                        
                   
        #backtrack  
        tags={}
        goal = -float('inf') 
        found_goal=0
        if n+1>2:
            for v in viterbi[n+1]:
                for u in viterbi[n+1][v]:
                    if u in transitions and v in transitions[u]:
                        if FINAL_STATE in transitions[u][v]:
                            temp = transitions[u][v][FINAL_STATE] + viterbi[n+1][v][u]
                            if(temp>goal):
                                goal = temp
                                tags[n]=v
                                tags[n-1]=u
                                found_goal=1
        
        if found_goal == 1:
            found_state1 = tags[n]
            found_state0 = tags[n-1]
            for i in range(n+1,2,-1):
                temp_state = backpointer[i][found_state1][found_state0]
                tags[i-3] = temp_state
                found_state1 = found_state0
                found_state0 = temp_state
         
            for i in range(1,n+1):
                if i==n:
                    print(tags[i])
                else:
                    print(tags[i]),

        if found_goal == 0:
            print("")
        
        
        

        #beam search
        """
            max = -float('inf')
            maxState = None
            for state in viterbi[i]:
                for prevState in states:
                    if prevState in viterbi[i][state] and viterbi[i][state][prevState]>max:
                        max = viterbi[i][state][prevState]
                        maxState = state

            print(viterbi[i])
            for state in viterbi[i].keys():
                if state is not maxState:
                    del viterbi[i][state]
        """

           
    
        
