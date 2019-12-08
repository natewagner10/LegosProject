import psycopg2
from flask import render_template, request
import json
import psycopg2
from theapp import app
import plotly
import plotly.graph_objs as go
import os

conn = psycopg2.connect(dbname='LEGOS')
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


def findOtherSets(setnums, getMissing):
    ''' 
    Function takes in lego set-numbers and outputs an interactive chart showing
    the percent of parts you have needed to build other lego sets

    Function takes in a given lego set-number and returns the parts needed to 
    complete that set

    Function also outputs the number of complete sets that the given part_numbers
    can create

    '''

    # sets the default setnum for initialization
    if setnums == None:
        setnums = '0013-1'

    # sets the default getMissing for initialization
    if getMissing == None:
        getMissing = setnums
        if len(getMissing) > 1:
            getMissing = '0013-1'
    
    # forget why I did this:
    setnums = setnums
    
    
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
    

    # From above, given a setnum(s) we,
    # look up the inventory_id(s)
    # look up every set that uses the parts from the given set, and we sum those parts, grouped by the inventory_id(s)
    # then we join that result with inventories to get the associated setnum(s)
    # then we join that table with the sets table, and we compare the sum of the parts we have, to the total number of parts needed to complete the set
    # query returns the top 20 sets, ordered by the percent complete, descending
    cur.execute("select set_num, set_name, Round(sum/num_parts::float*100)::int as percentParts from (select a.set_num, a.sum, b.set_name, b.num_parts from (select a.set_num, b.sum from inventories a, (select inventory_id, sum(quantity) from (" + GetParts + ") hold group by hold.inventory_id order by sum desc) b where a.inventory_id = b.inventory_id) a, sets b where a.set_num = b.set_num) a order by percentParts desc limit 20;")
   
    InventoryID_SumParts = cur.fetchall()
    
    # here we take the output of the above query, and put the output into seperate lists
    sets = []
    names = []
    percents = [] 
    for x in InventoryID_SumParts:
        sets.append(x[0])
        names.append(x[1])
        percents.append(x[2])

    # Similar query as above, however, now we count the number of complete sets that can be built
    cur.execute("select count(*) from (select set_num, set_name, sum/num_parts::float*100 as percentParts from (select a.set_num, a.sum, b.set_name, b.num_parts from (select a.set_num, b.sum from inventories a, (select inventory_id, sum(quantity) from (" + GetParts + ") hold group by hold.inventory_id order by sum desc) b where a.inventory_id = b.inventory_id) a, sets b where a.set_num = b.set_num) a order by percentParts desc) b where percentparts >= 100 ;")
   
    numberOfCompletes = cur.fetchall()
    numberOfCompletes = str(clean(numberOfCompletes)[0])
    
    
    # make setnum pretty:
    numss = []
    for x in sets:
        numss.append("Set Number: " + x)


    # plot chart:
    data = [go.Bar(
                x=numss,
                y=percents,
                text = names
                
                )]

    # save chart 
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    
    

    # here we find the inventory ID given the set_num, to find the missing parts
    cur.execute("select inventory_id from inventories where set_num = " + "'" + getMissing + "'" + ";")
    InvenID = cur.fetchall()
    InvenID = clean(InvenID)
    
    
    # Find all parts from the set of interest:
    cur.execute("select part_num from inventory_parts where inventory_id = " + str(InvenID[0]) + ";")
    MissingParts = cur.fetchall()
    
    # loop through list and see which parts we don't have 
    Needed = []
    for i in MissingParts:
        if i[0] not in ALLPartsList:
            Needed.append(i)
        else:
            pass
    
    # finally, return the chart, the needed parts for a given set, and the number of complete sets we can build:
    return graphJSON, Needed, numberOfCompletes







setnum = None

@app.route('/')
def index():
    global setnum
    set_num = request.args.get('set_num_search', default=setnum, type=str)
    setnum = set_num
    getParts = request.args.get('find_parts', default=None, type=str)
    bar, partslist, numComp = findOtherSets(setnum, getParts)
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'lego_logo_large_by_raukhaul_au-d9f9agw.jpg')    
    return render_template('index.html', plot=bar, len = len(partslist), partslist = partslist, numComp = numComp, user_image = full_filename)


