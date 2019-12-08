#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 12:27:11 2019

@author: natewagner
"""

import plotly.graph_objects as go
from plotly.offline import plot
import psycopg2
import sys
conn = psycopg2.connect("dbname=LEGOS user=nwagner")
cur = conn.cursor()




# function to clean the results from a query:
def clean(i):
    holder = []
    for x in range(0, len(i) ):
        holder.append(i[x][0])
    return holder

# returns cleaned SQL output 
def printdata(sets, names, percents):
    for x in range(0, len(sets)):
        print(str(sets[x]) + '    ' + str(names[x]) + '     ' + str(percents[x]))


def findOtherSets(setnums):
    ''' 
    Function takes in lego set-numbers and outputs an interactive chart showing
    the percent of parts you have needed to build other lego sets

    '''
    
    # User will input the set_nums from sets that they have
    #setnums = input("Please enter the set_num associated with the set you have, seperated by a comma: ")
    #setnums = "0013-1, 0013-10, 0055-1, 00222-1, 0009995-1"
    
    
    # clean the user input
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
    
    
    
    
    # clean parts
    ALLPartsList = clean(ALLPartsList)
    
    
    # initialize query to get quantity of parts we have
    GetParts = "select inventory_id, part_num, quantity from inventory_parts where part_num = " + "'" + ALLPartsList[0] + "'" 
    
    
    # create query:
    # this adds the additional part_nums to end of query:
    for i in range(1, len(ALLPartsList)):
        whereStatement = " or part_num = " + "'" + str(ALLPartsList[i]) + "'" 
        if len(ALLPartsList) == 1:
            GetParts = "select inventory_id, part_num, quantity from inventory_parts where inventory_id = " + "'" + str(ALLPartsList) + "'" 
        else:
            GetParts = GetParts + whereStatement
    

    
    cur.execute("select set_num, set_name, sum/num_parts::float*100 as percentParts from (select a.set_num, a.sum, b.set_name, b.num_parts from (select a.set_num, b.sum from inventories a, (select inventory_id, sum(quantity) from (" + GetParts + ") hold group by hold.inventory_id order by sum desc) b where a.inventory_id = b.inventory_id) a, sets b where a.set_num = b.set_num) a order by percentParts desc limit 20;")
    InventoryID_SumParts = cur.fetchall()
    #print(InventoryID_SumParts)
    
    sets = []
    names = []
    percents = [] 
    for x in InventoryID_SumParts:
        sets.append(x[0])
        names.append(x[1])
        percents.append(x[2])

#    # If user wants to see how many complete sets they can build:
#    if numFull == True:
#        cur.execute("select count(*) from (select set_num, set_name, sum/num_parts::float*100 as percentParts from (select a.set_num, a.sum, b.set_name, b.num_parts from (select a.set_num, b.sum from inventories a, (select inventory_id, sum(quantity) from (" + GetParts + ") hold group by hold.inventory_id order by sum desc) b where a.inventory_id = b.inventory_id) a, sets b where a.set_num = b.set_num) a order by percentParts desc) b where percentparts >= 100 ;")
#        numberOfCompletes = cur.fetchall()
#        print("You can build " + str(clean(numberOfCompletes)[0]) + " complete sets.")
#    else:
#        pass
    
    #printdata(sets, names, percents)
    
     #make setnum pretty:
    numss = []
    for x in sets:
        numss.append("Set Number: " + x)




    # plot chart:
    data = [go.Bar(
                x=names,
                y=percents,
                text = numss
                )]

    plot(data, auto_open=True, filename='/var/www/Legos/Legos/plot_resultNATE.html')
    
    return ALLPartsList, setnums

    
  
    

findOtherSets(str(sys.argv[1]))



