import pyrebase
import time

print("iam in")

ResponseStartIDX=4   #holds where the response in response command is stored
ResponseEndIDX=6

SectionsCountStartIDX=4   #holds where the response in response command is stored
SectionsCountEndIDX=6


#Response Values according to TP
R_OK=0
R_NOT_SectionOffestViolation=1
R_NOT_SectionsOutOfScope=2
R_NOT_MismatchData=3

IDX=0               ##holds instant index in file
LastSavedIDX=0      ##hold last valid index in file
SentDataBlocks=0    ##Number of valid sent sections
SectionsCount=0     ##Total Number of Sections to send
DataToSend=" "
DataBlocks=0
f=open("tst.txt","r+")
lines = f.readlines()
f.close()

print("iam in 2")

SectionsCount = hex( int( lines[0][SectionsCountStartIDX : SectionsCountEndIDX] , 16) )
#print(SectionsCount)

config = {
   "apiKey": "AIzaSyCLVYhUGxHVeIfLW8DkWPZy7kBu4f1-79o",
    "authDomain": "fota-905e1.firebaseapp.com",
    "databaseURL": "https://fota-905e1.firebaseio.com",
    "projectId": "fota-905e1",
    "storageBucket": "fota-905e1.appspot.com",
    "messagingSenderId": "746270454506",
    "appId": "1:746270454506:web:32183900e0176d27b31d93",
    "measurementId": "G-ZE9JE4FGRP"
    }
#FireBase Initialization     
firebase = pyrebase.initialize_app(config)
db = firebase.database()

#Notification with New App
while True:
    result = db.child("FlashNewApp").get()
    if (result.val() == False ):
        break 
db.child("FlashNewApp").set(True)

#Sending Erase Command
Line = lines[IDX].split("\n")
db.child("Frame").set(Line[0])
db.child("ResponseRQT").set(True)
db.child("Send").set(True)              ##NOTE: Change to TRUE

#listen to Erase Command Response
while True:
    result = db.child("Send").get()
    if (result.val() == False ):
        break
print("iam in 3")
ResponseCommand = db.child("Frame").get()
ResponseCommand = ResponseCommand.val()
Response        = hex( int( ResponseCommand[ResponseStartIDX : ResponseEndIDX] , 16 ) )
db.child("ResponseRQT").set(False)

if Response == hex(R_OK) :
    f=open("./progress.txt","w")
    f.write(str(int(SectionsCount,16)) +" "+ str(SentDataBlocks) )
    f.close()
    IDX += 1 
    while hex(SentDataBlocks) < SectionsCount :
        #send 200 Data Frame
        for i in range(20) :
            #print(IDX)
            Line = lines[IDX].split("\n")
            DataToSend += Line[0]
            print(Line[0])
            IDX += 1 
        print("20 Bytes")
        db.child("Frame").set(DataToSend)
        db.child("Send").set(True)
        DataBlocks += 1
        #Raise ResponseRQT if it's Verification Command
        while True:
          result = db.child("Send").get()
          if (result.val() == False ):
            break
        if DataBlocks == 10:
          DataBlocks=0
          #Verification Command
          Line = lines[IDX].split("\n")
          db.child("Frame").set(Line[0])
          db.child("ResponseRQT").set(True)
          db.child("Send").set(True)
          while True:
            result = db.child("Send").get()
            if (result.val() == False ):
              break
          #Verification Command Response Analyse
          ResponseCommand = db.child("Frame").get()
          ResponseCommand = ResponseCommand.val()
          Response        = hex( int( ResponseCommand[ResponseStartIDX : ResponseEndIDX] , 16 ) )
          db.child("ResponseRQT").set(False)
  
          if( Response == hex(R_OK) ):
              SentDataBlocks +=1
              LastSavedIDX += IDX
              print("iam in 4")
              f=open("./progress.txt","w")
              f.write(str(int(SectionsCount,16)) +" "+ str(SentDataBlocks) )
              f.close()
          else:
              IDX = LastSavedIDX
        DataToSend=""
        
         
    #db.child("FlashNewApp").set(False)
else:
    print("Erase Failed and Flash operation Stopped")


   