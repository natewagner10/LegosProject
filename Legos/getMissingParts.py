#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 13:18:00 2019

@author: natewagner
"""
import sys
import psycopg2
conn = psycopg2.connect("dbname=LEGOS user=nwagner")
cur = conn.cursor()

# function to clean the results from a query:
def clean(i):
    holder = []
    for x in range(0, len(i) ):
        holder.append(i[x][0])
    return holder


def getMissingParts(setnums, getMissing):
    '''
    Function takes in a lego set-number and outputs the parts you need to 
    build that set 
    
    '''
    
    setnums = setnums.split(",")
    setnums = [x.replace(' ', '') for x in setnums]
    
    
    # initiate query to obtain inventory_id's form the corresponding set_nums
    InventoryID = "select inventory_id from inventories where set_num = " + "'" + setnums[0] + "'"
    
    # create query:
    # this adds the " or set_num =  " to end of the query depending on how many sets the user has
    for i in range(1, len(setnums)):
        whereStatement = " or set_num = " + "'" + setnums[i] + "'" 
        if len(setnums) == 1:
            InventoryID = "select inventory_id from inventories where set_num = " + "'" + setnums + "'" 
        else:
            InventoryID = InventoryID + whereStatement
        
    # finalize query:
    InventoryID = InventoryID + ";"
    
    # execute SQL command:
    cur.execute(InventoryID)
    InventoryIDS = cur.fetchall()
    
    
        
    
    IDs = clean(InventoryIDS)
    
    # intialize query to get the associated parts and how many:
    PartsList = "select part_num from inventory_parts where inventory_id = " + str(IDs[0])
    
    # create query:
    # this adds the additional inventory_ids to end of query:
    for i in range(1, len(IDs)):
        whereStatement = " or inventory_id = " + str(IDs[i])
        if len(IDs) == 1:
            PartsList = "select part_num from inventory_parts where inventory_id = " + str(IDs) 
        else:
            PartsList = PartsList + whereStatement
    
    # finalize query:
    PartsList = PartsList + ";"
    
    # execute in SQL
    cur.execute(PartsList)
    ALLPartsList = cur.fetchall()
    
    
    
    # prompt user to see which parts they need 
    #getMoreInfo = input("Do you want to see what parts you need for non-full sets?   Enter yes or no: ")
    #if getMoreInfo == "yes":
    #getMissing = input("Enter the set number to see which parts you need: ")
    
    
    
    # find inventory ID from set_num
    cur.execute("select inventory_id from inventories where set_num = " + "'" + getMissing + "'" + ";")
    InvenID = cur.fetchall()
    InvenID = clean(InvenID)
    
    # Find all parts from the set of interest:
    cur.execute("select part_num from inventory_parts where inventory_id = " + str(InvenID[0]) + ";")
    MissingParts = cur.fetchall()
    
    # loop through list and see which parts we don't have 
    # run time is O(n), can probably reduce to O(logN)
    ALLPartsList = clean(ALLPartsList)
    Needed = []
    for i in MissingParts:
        if i[0] not in ALLPartsList:
            Needed.append(i)
        else:
            pass
    
    for x in Needed:
        print (x[0])
        

    
getMissingParts(str(sys.argv[1]), str(sys.argv[2]))

