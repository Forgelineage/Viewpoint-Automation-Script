#TODO: 
#Add graphical mode
#Turn into exec
#Add check for excursion at start of data
#Add validation checks to header parsing
#Add eof code




import pandas as pd
path=r"ViewPoint3.csv"

colnames = ['Time', 'Temp','Humidity'] #Create Headers

#df = pd.read_csv(path, delimiter="\t", header = 1, parse_dates=['Time'], nrows = 500)
#Pandas only supports 1 type per column, thus need to have two datasets.
dfdata = pd.read_csv(path, names = colnames, delimiter="\t", parse_dates=['Time']) #Pull data in
dfhead = pd.read_csv(path, names = colnames, delimiter="\t") #Pull Header information in

#Converts times to time objects
dfdata['Time'] = pd.to_datetime(dfdata.Time, format='%m/%d/%Y %I:%M:%S %p', errors ='coerce')
#Converts to temp to float objects
dfdata['Temp'] = pd.to_numeric(dfdata['Temp'], downcast='float', errors ='coerce')

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
#import sys
#!conda install --yes --prefix {sys.prefix} fpdf
#!{sys.executable} -m pip install fpdf
from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size = 15)
#pdf.cell(200, 10, txt = "Automated Viewpoint Report:", ln = 1, align = 'C')
#pdf.cell(200, 10, txt = "Alpha Version", ln = 2, align = 'C')
pdf.set_font("Arial", size = 12)



    
#from IPython.display import display
#pd.set_option('display.min_rows', 20)
#display(dfdata)
#display(dfhead)

f = open("Automated Viewpoint Report.rtf", "w")
#f.write("""{\\rtf1\\ansi\\deff0""")
f.write("""{\\rtf1\\ansi\\deff0\\nouicompat{\\fonttbl{\\f0\\fnil\\fcharset0 Calibri;}}
{\\colortbl ;\\red255\\green0\\blue0;\\red0\\green0\\blue0;}\n""")
f.write("\\pard\\sa200\\sl276\\slmult1\\f0\\fs22\\lang9\\")



import re
from datetime import datetime, timedelta
i = 0 #main index counter
starttime = 0 
SenErr = 0 #Sensor Error Flag (Array needed?)
TempErr = 0 #Out of Temp Range Error (Array Needed?)
maxtime = timedelta(0,0,0,0,0,3) #Maximum temp excursion length before NCR
#TODO: Fix addtime init to not be based on locations
addtime = dfdata.iloc[5][0] - dfdata.iloc[4][0] #Initializing addtime to be correct data type
output = 0 #initializing output?
err = 0
TempWarn = 0
unitname = "" #Keep track of which unit
long = 0 #Used for debug
smallexcur = 0
line = 3


def ParseHeader(index):
    #TODO: Add validation checks.
    global unitname
    global temps
    global high
    global low
    unitname = dfhead.iloc[index][0] #Update unit identity
    temps = re.findall(r"[-+]?\d*\.\d+|\d+", dfhead.iloc[index+2][1]) #Parse temp range
    high = float(temps[1]) #push high temp range to variable
    low = float(temps[0]) #push low temp range to variable
    
def TimeCheck():
    #true = is higher than max time
    global dfdata
    global i
    global starttime
    global maxtime
    if((dfdata.iloc[i][0] - dfdata.iloc[starttime][0]) > maxtime):
        return True
    else:
        return False
    
def StartTime():
    global starttime
    global i
    starttime = i

def TempCheck():
    global i
    global high
    global low
    if((dfdata.iloc[i][1] < high) and (dfdata.iloc[i][1] > low)):
        return True
    else:
        return False


while i < len(dfdata.index) - 2: #While loop goes over every row in data table
    #Nat + Nan
    if((pd.isnull(dfdata.iloc[i][0])) and (pd.isnull(dfdata.iloc[i][1]))): #Header Data, Sensor Out, or Malform
        if (dfhead.iloc[i+1][0] == 'Time' and dfhead.iloc[i+1][1] == 'Temperature'): #Found Unit Header Data
            if(smallexcur > 0):
                print(f"{bcolors.OKGREEN}\tNon-Excursions Detected and are within 3 hour window.{bcolors.ENDC}")
                #pdf.set_font("Arial", size = 12)
                #pdf.cell(200, 10, txt = f"{bcolors.OKGREEN}\tNon-Excursions Detected and are within 3 hour window.{bcolors.ENDC}", ln = line, align = 'R')
                #line = line + 1
            if (err > 1):
                
                #TODO NCR Bits
                
                if(TimeCheck()):
                    print(f"{bcolors.WARNING}\tExcursion Detected, check manually from :{bcolors.ENDC}")
                    print('\t\tTime: ' , dfdata.iloc[starttime][0], 'to', dfdata.iloc[i][0], ". End of Data, Please Manually Check")
                    print('\t\tDuration: ',dfdata.iloc[i][0] - dfdata.iloc[starttime][0])
                    #pdf.set_font("Arial", size = 12)
                    #pdf.cell(200, 10, txt = f"{bcolors.OKGREEN}\tExcursion Detected, check manually from :{bcolors.ENDC}", ln = line, align = 'R')
                    line = line + 1
                    err = 0
                else:
                    print(f"{bcolors.FAIL}\tPossible Excursion Detected, check manually from :{bcolors.ENDC}")
                    print('\t\tTime: ' , dfdata.iloc[starttime][0], 'to', dfdata.iloc[i][0], ". End of Data, Please Manually Check")
                    print('\t\tDuration: ',dfdata.iloc[i][0] - dfdata.iloc[starttime][0])
                    #f.write(f"{bcolors.FAIL}\tPossible Excursion Detected, check manually from :{bcolors.ENDC}/n")
                    err = 0
            ParseHeader(i)
            print(unitname , " , " , high , " to " , low) #Console Output
            f.write(str(unitname) + " , " + str(high) + " to " + str(low) + "\n \\line") #Text File Output
            err = 0 #Reset err for new unit
            smallexcur = 0 #Reset counter for new unit
            i = i+2 #Jumping over header info
    #Time + Nan OR Nat + Temp
    elif((pd.isnull(dfdata.iloc[i][0])) or (pd.isnull(dfdata.iloc[i][1]))): #Sensor Outage or Malformed, assumed Sensor.
        if(err == 0):
            print(f"{bcolors.FAIL}\tSensor Outage{bcolors.ENDC} at ", dfdata.iloc[i][0])
            #f.write("\\cf1 Sensor Outage at: " + str(dfdata.iloc[i][0])) #Text File Output
            #f.write(f"{bcolors.FAIL}\tSensor Outage{bcolors.ENDC} at " + str(dfdata.iloc[i][0]))
            err = 1
            StartTime()
    #Time + Temp
    else:
        if(err > 0 and TempCheck()):
            if(long == 1):
                print("err + Tempcheck true")
            if(TimeCheck()):
                print(f"{bcolors.FAIL}\tExcursion Detected:{bcolors.ENDC}")

                print('\t\tTime: ' , dfdata.iloc[starttime][0], 'to', dfdata.iloc[i][0])
                print('\t\tDuration: ',dfdata.iloc[i][0] - dfdata.iloc[starttime][0])
                err = 0
            else:
                smallexcur = 1
                err = 0
            if(long == 1):
                print('\t\ti: ' , i, " Start: ", starttime)
        elif(err > 0 and not TempCheck()):
            if(long == 1):
                print("err + Tempcheck false")
                print('\t\ti: ' , i, " Start: ", starttime)
        elif(err == 0 and TempCheck()):
            if(long == 1):
                print("err=0 + Tempcheck true")
                print('\t\ti: ' , i, " Start: ", starttime)
        elif(err == 0 and not TempCheck()):
            if(long == 1):
                print("err=0 + Tempcheck false")
            err = 1
            StartTime()
            if(long == 1):
                print('\t\ti: ' , i, " Start: ", starttime)
    i = i + 1

#EoF Check
if (err > 1):

    #TODO NCR Bits

    if(TimeCheck()):
        print(f"{bcolors.WARNING}\tExcursion Detected, check manually from :{bcolors.ENDC}") #This will be taken care of in error code later on.
        print('\t\tTime: ' , dfdata.iloc[starttime][0], 'to', dfdata.iloc[i][0], ". End of Data, Please Manually Check")
        print('\t\tDuration: ',dfdata.iloc[i][0] - dfdata.iloc[starttime][0])
        err = 0
    else:
        print(f"{bcolors.FAIL}\tPossible Excursion Detected, check manually from :{bcolors.ENDC}") #This will be taken care of in error code later on.
        print('\t\tTime: ' , dfdata.iloc[starttime][0], 'to', dfdata.iloc[i][0], ". End of Data, Please Manually Check")
        print('\t\tDuration: ', dfdata.iloc[starttime][0]-dfdata.iloc[i][0])
        err = 0

f.write("""f.write("\\par}""")
f.close()

import time
time.sleep(1)
f = open("Automated Viewpoint Report.rtf", "r")
for x in f:
    pdf.cell(200, 10, txt = x, ln = 1, align = 'R')
pdf.output("Viewpoint Auto Report.pdf")
f.close()