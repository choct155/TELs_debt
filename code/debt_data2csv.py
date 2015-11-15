
# coding: utf-8

# This Notebooks converts the fixed width format of Reuters subnational debt data files to CSV. For the narrative 
# accompanying the development of this script, see DataTest.ipynb

import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import glob
import sys

#Define file for conversion
file_test=sys.argv[1]
print '\n\n\n'
print '*********************************************'
print 'Processing '+file_test
print '*********************************************'

#Create container for header lines
header=[]

#Capture the 4th-8th lines
with open(file_test,'r') as f:
    for i in range(4):
        tmp_line=f.readline()
    #Capture line 4
    header.append(tmp_line)
    #Capture 5-8
    for i in range(4):
        header.append(f.readline())
    

#Create container to hold field positions
field_pos=[]

#For each character in the first line...
for i,c in enumerate(header[0]):
    #...define the test...
    old_spaces=((header[0][i-3].isspace()) & (header[0][i-2].isspace()))
    new_letters=~((header[0][i-2].isspace()) & (header[0][i-1].isspace()))
    new_field=old_spaces & new_letters
    #...if a new field has begun...
    if new_field:
        #...capture the position at which it started
        #field_pos.append(i-4) clipped first digit of net interest cost
        field_pos.append(i-5)

#Define function to insert delimeters
def delim(line,line_len,field_pos=field_pos):
    '''Function takes fields positions and turns an ugly string into a nicely delimited list'''
    #Capture padding needed to equal length of first string as list
    pad=(line_len-len(list(line)))
    #Capture string as a list
    line_list=list(line)+[' ']*pad
    #For each new field...
    for pos in field_pos:
        #...convert the start position from space to comma
        line_list[pos]='|'
    #Convert list back to string
    line=''.join(line_list)
    #Strip space
    line=[s.strip() for s in line.split('|')]
    return line

#Generate container to hold all processed header lines
pheader=[]

#For each header line...
for i,hl in enumerate(header):
    #...process that line
    tmp_line=delim(hl,len(header[0]))
    pheader.append(tmp_line)

#Generate container to hold variables
varlist=[]

#For each variable...
for i in range(len(pheader[0])):
    #...create a temporary container to hold the variable components from each line...
    var_tmp=[]
    #...and for each line...
    for j in range(len(pheader)):
        #...put the variable components in var_tmp...
        try:
            var_tmp.append(pheader[j][i])
        except:
            print '***',j,i
            print len(pheader),len(pheader[0])
    #...convert to string and throw the variable in varlist
    varlist.append(' '.join(var_tmp).strip())

#Capture start and stop positions in DF
fp_df=DataFrame({'stop':field_pos,
                 'start':Series(field_pos).shift()+1})

#Make sure we start at position 0
fp_df.ix[0,'start']=0

#Add last field position par
last_pair=DataFrame({'start':fp_df.iloc[-1]['stop']+1,
                     'stop':len(header[0])},index=[fp_df.index[-1]+1])
fp_df=pd.concat([fp_df,last_pair])

#Match up fields positions and labels
fp_df['var']=varlist

#Assign arbitrary label to first field 
fp_df.ix[0,'var']='Number'

#Convert field positions parameters to int
for var in ['start','stop']:
    fp_df[var]=fp_df[var].astype(int)

#Define function get rid of dups
def pos_append(varlist):
    '''Function appends position of variable to variable name to uniquely identify variables 
    that appear more than once'''
    #Create an output varlist
    varlist_out=['']*len(varlist)
    #For each variable...
    for idx,v in enumerate(varlist):
        #...identify the instances of the variable and their positions
        instances=[(i,var) for i,var in enumerate(fp_df['var'].values) if var==v]
        #...if the variable appears more than once...
        if len(instances)>1:
            #...for each item in instances...
            for item in instances:
                #...append the variable position to the duplicate instance...
                varlist_out[item[0]]=varlist[item[0]]+str(item[0])
        #...otherwise leave the variable alone
        else:
            varlist_out[idx]=varlist[idx]
    return varlist_out
    
#Make the variables unique    
fp_df['u_var']=Series(pos_append(fp_df['var'].values))

print 'Capturing data'
#Create container for data lines
data=[]
#Capture the 9th line forward
with open(file_test,'r') as f:
    data=f.readlines()[8:-15] #(there are session details at the end of the file)
    f.close()
        
print 'Processing data'
#Generate container to hold all processed data lines
data_lines=[]

#For each data line...
for i,dl in enumerate(data):
    #...process that line
    data_lines.append(delim(dl,len(header[0])))
    if i%10000==0:
        print '>>Processing data line #',i
        
print 'Consolidating lines (vertical concatenation)'

#Capture start position of each issue (vertical)
issue_start=[(line[0],i) for i,line in enumerate(data_lines) if line[0]!='']

#Capture in DF and include stop position
issue_pos=DataFrame({'issue':[iss[0] for iss in issue_start],
                     'start':[iss[1] for iss in issue_start],
                     'stop':Series([iss[1] for iss in issue_start]).shift(-1)-1})

#Fill in last stop position
issue_pos.ix[issue_pos.index[-1],'stop']=len(data_lines)

#Convert positions to integer
for var in ['issue','start','stop']:
    issue_pos[var]=issue_pos[var].astype(int)
    
#Set index
issue_pos.set_index('issue',inplace=True)

#Create a container for consolidated data lines
data_lines_con=[]

#For each issue...
for issue in issue_pos.index:
    #...create a container for a consolidated, issue-specific line...
    new_data_line=[]
    #...if there is more than one line allocated to that issue...
    if issue_pos.ix[issue]['start']<issue_pos.ix[issue]['stop']:
        #...capture the data lines in that issue...
        iss_lns=data_lines[issue_pos.ix[issue]['start']:issue_pos.ix[issue]['stop']]
        #...and for each variable in those data lines...
        for idx in range(len(data_lines[0])):
            #...vertically concatenate to form a new consolidated data line...
            new_data_line.append(' '.join([line[idx] for line in iss_lns]).strip())
    #...otherwise, just rename the single line...
    new_data_line=data_lines[issue_pos.ix[issue]['start']]
    #...and then throw the new line in data_lines_con
    data_lines_con.append(new_data_line)
    
print 'Collecting data in dictionary'
#Create dictionary to hold data
data_dict={}

#For each variable...
for i,var in enumerate(fp_df['u_var']):
    #...once all lines are collected, update the dictionary
    data_dict.update({var:[data_lines_con[row][i] for row in range(len(data_lines_con))]})
    if i%50==0:
        print '>>Capturing variable #',i
    
    
#Convert data dictionary into DF
debt=DataFrame(data_dict)

#Write data to disk
debt[fp_df['u_var']].to_csv(file_test[:-3]+'csv')