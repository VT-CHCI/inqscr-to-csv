import os



def convertAllFilesToCSVByEvent():

  folder = pickAFolder()
  print "Processing all files in :", folder
  dir = os.listdir( folder )
  
  convertGenderFiles( folder, dir, "F" )
  convertGenderFiles( folder, dir, "M" )
  
  return
 
def convertGenderFiles( folder, dir, gender ) :
  
  teamCount = 0
  entries = [ 0 ]
  files = folder
  for i in range( 1, 2*3600 ) :
    entries = entries + [ [i] ]
  
  for file in dir :
 
    if not (file.endswith( ".csv" ) or file.startswith( "." ) ):
      if (file.find( "_"+gender ) > 3) :
        teamCount = teamCount + 1
        print file
        entries = inqScribeToExcel( folder + file, gender, teamCount, entries )
        files = files + ", " + file
  
 
  fileNameOut = folder + gender + "ByEvent.csv"
  fileOut = open( fileNameOut , "wt" )  # create the csv file
  
  fileOut.write( files )
  fileOut.write("\n")
 
  totalSec = entries[0]
  totalSec = totalSec + 1
  commaStr = ",,,,,,,,,,,,,,,,,,"
  
  events = [[]]
  startTime = 1
  
  print " - finding events ...",
    
  for sec in range(1, totalSec )  :
  
       entry = entries[ sec ]
       
       if len(entry) > 3 :
 
         teamEntries = entry[2]
         observation = entry[3]
         team = 0
         tm = 0

         for teamIndex in range( 0, teamEntries, 4 ) :
       
            tm = observation[teamIndex]
            code = observation[teamIndex+1]
            startTime = observation[teamIndex+2]
            endTime = observation[teamIndex+3]

            events = addEvents( sec, events, code, tm, startTime, endTime )
      
  
       events[0] = []                              # create currently active event list

       for eventIndex in range(1, len(events) ) :                                             
       
         event = events[eventIndex]
         if event[3] >= sec :                      # is endTime yet to happen? then add event to list
            events[0] = events[0] + [eventIndex]
          
       
  print len(events)
  events[0] = []

  print " - writing " + fileNameOut
  
  for event in events :

    if len(event) > 1 :
    
        currentEvent = event
        
        fileOut.write( str(currentEvent[0]) )    #event number
        fileOut.write(",")
        
        code = currentEvent[1]
        fileOut.write( str(code) )    #event code
        fileOut.write(",")
        
        startTime = currentEvent[2]
        fileOut.write( str(startTime) )    #start time in seconds
        fileOut.write(",")

        endTime = currentEvent[3]
        fileOut.write( str(endTime) )    #end time in seconds
        fileOut.write(",")
        
        fileOut.write( secondsToTimeString(startTime) )    #start time in [dy:hr:mn:sec]
        fileOut.write(",")       
        
        fileOut.write( secondsToTimeString(endTime) )      #end time in [dy:hr:mn:sec]
        fileOut.write(",")
        
        team = currentEvent[ 4 ]          #list of teams finding this code
        fileOut.write( commaClean(str(team)) )
        fileOut.write(",")

        tmCount = 0
       
        for tm in team :
       
           fileOut.write( commaStr[ 0:(tm-tmCount)+1 ] )
           fileOut.write( code )
           tmCount = tmCount + 1

        fileOut.write("\n")  
  
  fileOut.close()

  return
 



def addEvents( sec, events, code, team, startTime, endTime ) :
 
  currentlyActiveEvents = events[0]

  if len(currentlyActiveEvents) > 0 :
    
    for eventIndex in currentlyActiveEvents :
  
     event = events[ eventIndex ]
     
     if event[ 1 ] == code :
        teamList = event[4]
        event[4] = addItem( teamList, team )
        if startTime < event[3] and endTime > event[3] :
          event[3] = endTime                                    # extend length of event
        events[ eventIndex ] = event
        return events
     
  eventIndex = len( events )
  events = events + [[eventIndex, code, startTime, endTime, [team] ] ] 

  return events












def addItem( lst, newItem ) :

  newLst = []
  if len(lst) < 1 :
    lst = [newItem]
    return lst
    
  for item in lst :
  
    if item == newItem :
      return lst

  lst = lst + [ newItem ]
  return lst




def inqScribeToExcel( fileName, gender, teamCount, entries ) :

  fileIn = open( fileName, "rt" )              # open the inqscribe file
   
  totalSeconds = 0
  code = " "
  time = " "
  codeTime = " "
  eventStart = 0
  startTimeString = ""

  contents = fileIn.read()
  line = parse( [contents, "text=", contents ] )
  line = parse( [line[2], "timecode.fps=", contents ] )
  
  contents = line[0]
    
  while len(contents) > 0 :
    entry = parse( [contents, u'\\' ] )
    contents = entry[2]
    if entry[0].find("[") > -1 :
      entry = parse( [entry[0], "," ] )
      observation = entry[2]
      entry = parse( [entry[0], "r"] )
      timeString = entry[0] + entry[2]
      eventTime = timeToSeconds( timeString )
      if len(timeString) > 14 :
        if len(observation) < 1 :
          entry = parse( [ timeString, "]" ] )
          observation = entry[2]
    
      if (code == " ") :
       eventStart = eventTime
       code = stripBlanks( observation )
      else :
  
        for sec in range( eventStart, eventTime ) :
          entries = addEntries( entries, teamCount, sec, code, eventStart, eventTime )
        
        if (observation[0:4] == "END ") :
          eventStart = eventTime + 1
          code = " "
        else :
          eventStart = eventTime
          code = stripBlanks( observation )
          
 
  
  fileIn.close()
 
  return entries
    
    
    
def addEntries( entries, teamCount, second, code, startTime, endTime ) :
  entry = entries[ second ]
  if len(entry) < 2:
     entries[ second ] = [ second, endTime, 0, [teamCount, code, startTime, endTime]]
  else :
    previousCount = entry[2]
    previousCode = entry[3]
    entries[ second ] = [second, entry[1], previousCount + 3, previousCode + [teamCount, code, startTime, endTime]]
    
  entries[0] = max(entries[0], second)
  
  return entries
   
 
def parse( parseTriplet ) :
  inString = parseTriplet[0]
  separator = parseTriplet[1]
  loc = inString.find( separator )
  outString = ""
  if loc > -1 :
     if loc < len(inString) :
       outString = inString[ loc + len(separator):len(inString) ]
     inString = inString[ 0:loc ]
 
  return [inString, separator, outString ]


  
def timeToSeconds( timeString ) :
  time = ""
  time = parse( [timeString, "["] )
  time = parse( [time[2], ":"] )
  hour = int( time[0] )
  time = parse( [time[2], ":"] )
  minute = int( time[ 0 ] )
  time = parse( [time[2], "]"] )
  secStr = time[0]
  sec = int( secStr[0:2] )
  if int( secStr[3:5] ) > 14 :
    sec = sec + 1
  
  return sec + (minute * 60) + (hour * 3600)
  
  
def secondsToTimeString( totalSecs ) :                    # convert total seconds to a string

  hours = int( totalSecs/3600 )
  minutes = int( (totalSecs - (hours * 3600))/60 )
  secs = totalSecs -((hours*3600) + (minutes * 60 ))
  
  return "[00:" + zeroPad( hours ) + ":" + zeroPad( minutes ) + ":" + zeroPad( secs ) + ".00]"
  
  
  
def zeroPad( amount ) :                                  # pre-pend a "0" to single digiits

  amount = str( amount )
  if len( amount ) == 1 :
    return "0" + amount
  else :
    return amount
    

def commaClean( strng ) :

  commaLoc = strng.find( "," )
  if commaLoc < 0 :
    return strng
  else :
    return commaClean( strng[0:commaLoc] + " " + strng[commaLoc+1:] )
 
  

def stripBlanks( strng ) :
  if strng[0:1] <> " " :
    return strng
  else :
    return stripBlanks( strng[1: ] )
  

def removeItem( lst, remove ) :

  lstNew = []
  for itm in lst :
  
    if itm <> remove :
      lstNew.append( itm )
      
  return lstNew
  
