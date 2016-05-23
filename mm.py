#This Task was created based on the work of Castel et. al 2011. If you  use this program, please credit Castel et. al 2011.#
#Psychopy Version 1.82xx                                                                                                   #
#------------------------------------------------------------------------------------------------------------------------------
#TO DO
#Workaround for pyglet leak so this doesn't crash on low RAM computers
#


from __future__ import division
from psychopy import visual, core, gui, data, misc, event
import time, random
import re, csv, os, os.path,collections

# define experiment parameters
expInfo = {'Subject':'1','Session':'1', 'Version': ['A', 'B'], 'Round': ['1', '2','3','4','5']}
expInfo['dateStr'] = time.strftime("%Y_%m_%d_%H%M", time.localtime())

# ask for task parameters
dlg = gui.DlgFromDict(expInfo, title='Meta Memory', fixed=['dateStr'],order=['Subject','Session', 'Version', 'Round'])
if not dlg.OK: core.quit()

#define clocks
experimentclock = core.Clock()
trialClock = core.Clock()

#define window and mouse
mywin = visual.Window([1024,768],allowGUI=True,fullscr=True,monitor="testMonitor",units="pix",color="black")
myMouse = event.Mouse(win=mywin)
#-----------------------------------------------------------------------------------------------------------
#Define Variables and lists---------------------------------------------------------------------------------
subject = expInfo['Subject']
session = expInfo['Session']
version = expInfo['Version']
roundIWant = int(expInfo['Round'])

#load instructions
instructions = []
for n in range (0,3):
    instructions.append(visual.ImageStim(mywin,pos=[0,0],image='./Slides/%i.jpg' %(n+1)))
instructions2 = []
ins = ["prompt","howto","scoring","ready"]
for n in range (0,4):
    instructions2.append(visual.ImageStim(mywin,pos=[0,0],image='./Slides/%s.jpg' %(ins[n])))
intro = []
for n in range (0,4):
    intro.append(visual.ImageStim(mywin,pos=[0,0],image='./Slides/i%i.jpg' %(n+1)))
#load questions


questions = visual.ImageStim(mywin,pos=[0,0],image='./Slides/blankpage.jpg')
betAsk = visual.ImageStim(mywin, pos=[0,0], image = './Slides/R.jpg')

enter = response = visual.TextStim(mywin, height=25,text="press enter to continue",color='white',pos=(0, -250))
#File Names
fileName  = '%s_%s_bets.csv' %(subject,session)
scorefileName  = '%s_%s_score.csv' %(subject,session) #Maybe change this?
inputFileName = '%s_%s_input.csv' %(subject,session)

#Variables
round = roundIWant


score = 0
scoreYet = False
referenceWords = []
wordsTheyRecalled =[]
corrects = ''
loops = 3 #change to number of rounds desired.
#------------------------------------------------------------------------------------------------------------
#Functions---------------------------------------------------------------------------------------------------
def recordWordsTheyTyped(fileName, word):
    if os.path.exists(fileName):
        dataFile =open(fileName, 'a')
        fieldnames = ['Subject', 'Session','Word']
        dataFileWriter = csv.DictWriter(dataFile, lineterminator='\n', fieldnames = fieldnames)
        dataFileWriter.writerow({'Subject': expInfo['Subject'], 'Session': expInfo['Session'], 'Word': word})
        dataFile.close()
    else:
        with open(fileName, 'w') as dataFile:
            fieldnames = ['Subject', 'Session','Word']
            dataFileWriter = csv.DictWriter(dataFile, lineterminator='\n', fieldnames = fieldnames)
            dataFileWriter.writeheader()
            dataFileWriter.writerow({'Subject': expInfo['Subject'], 'Session': expInfo['Session'], 'Word': word})
            dataFile.close()

def WaitForKeyInput():
    timer= core.CountdownTimer(5)
    trialClock.reset()
    text='...'
    feedback = visual.Rect(mywin, width= 200,height = 200, pos = (0,-100), lineWidth=5.0, lineColor = 'black')
    response = visual.TextStim(mywin, height=36,text=text,color="white",pos=(0,-100))
    #until return pressed, listen for letter keys & add to text string
    while event.getKeys(keyList=['return'])==[]:
        letterlist=event.getKeys(keyList=['0', '1', '2', '3', '4',  '5' , '6', '7', '8', '9','backspace','q'])
        color = 'black'
        if timer.getTime() >= 3:
            color = 'green'
        elif timer.getTime() >=0:
            color = 'yellow'
        elif timer.getTime() <0:
            color = 'red'
        feedback.lineColor= color
        betAsk.draw()
        feedback.draw()
        response.text = text
        core.wait(0.05)
        if text != '...':
            response.draw()
        mywin.flip()
        for l in letterlist:
            if l == 'q':
                core.quit()
            #if key isn't backspace, add key pressed to the string
            if l !='backspace':
                if text =="...":
                    text=l
                    pressedkeys=l
                else:
                    text+=l
                    pressedkeys+=(";" + l)
            #otherwise, take the last letter off the string
            elif len(text)>0:
                text=text[:-1]
                pressedkeys+=(";backspace")
            #continually redraw text onscreen until return pressed
            event.clearEvents()
    return text
def writeToDataFile(dataFileName,wordToWrite,r,cs,acc):#r is the risk amount variable and cs is the Cumulative Score variable
    if os.path.exists(dataFileName):
        dataFile =open(dataFileName, 'a')
        fieldnames = ['Subject', 'Session', 'Round', 'Word','Points','Cumulative Score', 'Acc']
        dataFileWriter = csv.DictWriter(dataFile, lineterminator='\n', fieldnames = fieldnames)
        dataFileWriter.writerow({'Subject': expInfo['Subject'], 'Session': expInfo['Session'], 'Round':round-1, 'Word': wordToWrite, 'Points': r, 'Cumulative Score': cs, 'Acc': acc})
        dataFile.close()
    else:
        with open(dataFileName, 'w') as dataFile:
            fieldnames = ['Subject', 'Session', 'Round', 'Word','Points','Cumulative Score', 'Acc']
            dataFileWriter = csv.DictWriter(dataFile, lineterminator='\n', fieldnames = fieldnames)
            dataFileWriter.writeheader()
            dataFileWriter.writerow({'Subject': expInfo['Subject'], 'Session': expInfo['Session'], 'Round': round-1, 'Word': wordToWrite, 'Points': r, 'Cumulative Score': cs, 'Acc': acc})
            dataFile.close()

def populateOldWords():
    x=[(0,150),(0,100),(0,50),(0,0),(0,-50),(0,-100),(0,-150),(0,-200),(0,-250),(0,-300),(0,-350),(200,150),\
    (200,100),(200,50),(200,0),(200,-50),(200,-100),(200,-150),(200,-200),(200,-250),(200,-300),(200,-350),\
    (-200,150),(-200,100),(-200,50),(-200,0),(-200,-50),(-200,-100),(-200,-150),(-200,-200),(-200,-250),(-200,-300),\
    (-200,-350),(-400,150),(-400,100),(-400,50),(-400,0),(-400,-50),(-400,-100),(-400,-150),(-400,-200),\
    (-400,-250),(-400,-300),(-400,-350),(400,150),(400,100),(400,50),(400,0),(400,-50),(400,-100),\
    (400,-150),(400,-200),(400,-250),(400,-300),(400,-350)]
    c = 0
    for w in wordsTheyRecalled: #prints words they have already typed
        a = visual.TextStim(mywin, height=50,text=w,color="white",pos=(x[c]))
        a.draw()
        c += 1

def WaitForKeyInput2():
    text='...'
    global scoreYet
    response = visual.TextStim(mywin, height=75,text=text,color="white",pos=(0, 250))
    response.draw()
    instructions2[0].draw()
    populateOldWords()
    mywin.flip()
    #until return pressed, they can type word
    while event.getKeys(keyList=['return'])==[]:
        if scoreYet == True:
            break
        letterlist=event.getKeys(keyList=['q','w','e','r','t','y','u','i','o','p','a','s','d','f',
            'g','h','j','k','l','z','x','c','v','b','n','m', '6',\
            'backspace','f12'])
        for l in letterlist:
            if l == '6':
                scoreYet = True
                break
            #if key isn't backspace, add key pressed to the string
            if l !='backspace':
                if text =="...":
                    text=l
                    pressedkeys=l
                else:
                    text+=l
                    pressedkeys+=(";" + l)
            #otherwise, take the last letter off the string
            elif text != '...':
                text=text[:-1]
                pressedkeys+=(";backspace")
            #continually redraw text onscreen until return pressed
            instructions2[0].draw()
            populateOldWords()
            core.wait(0.08)
#            if text != textold:
            response.text = text
            response.draw()
            mywin.flip()
    event.clearEvents()
    return text

def findBet(wordinput): #if they stopped and restarted, this used their original bets
    if os.path.exists(fileName):
        dataFileRead=open(fileName, 'r')
        reader = csv.reader(dataFileRead)
        RowValue = []
        for row in reader:
            RowValue.extend(row)
        targetwordindex= RowValue.index(wordinput)
        targetbetindex = targetwordindex + 1
        bet = RowValue[targetbetindex]
        dataFileRead.close()
        return bet

def WaitForMouseInput():
    goforit = True
    ans = 0
    event.clearEvents()
    waitforrelease = False

    while goforit:
        while True:
            buttons, times = myMouse.getPressed(getTime=True)
            if sum(buttons)>0:
                waitforrelease = True
                event.clearEvents
                break
            if event.getKeys(keyList = "f12"):
                event.clearEvents()
                core.quit()
            event.clearEvents()
        while waitforrelease == True:
            buttons,times = myMouse.getPressed(getTime=True)
            if sum(buttons) == 0:
                RT = trialClock.getTime()
                mouseX,mouseY = myMouse.getPos()
                if mouseY > -300 and mouseY < 0:
                    if mouseX > -400 and mouseX <0:
                        ans = "yes"
                        goforit = False
                        event.clearEvents()
                        return ans
                        break
                    if mouseX > 0 and mouseX < 400:
                        ans = "no"
                        goforit = False
                        event.clearEvents()
                        return ans
                        break
                else:
                    myMouse.clickReset()
                    waitforrelease = False
                    continue

def RunBlock():
    already = True
    bet = 999
    global round
    #load words
    wordList = './words/%s/words%i.txt' %(version ,round)
    words = list(cor for cor in open(wordList).read().split("\n") if cor)
    w = visual.TextStim(mywin, height=55,text= '...',color="white",pos=(0,0))
    #show words
    i=0
    event.clearEvents()
    while event.getKeys(keyList=['return'])==[]:#wait till ready
        instructions2[3].draw()
        enter.draw()
        mywin.flip()
    while i <12:
        questions.draw()#draw blank
        w.text = words[i]
        if already == True:
            w.draw()
            mywin.flip()#show word
            core.wait(2)#wait 2 seconds
        while bet > 10:
            print bet
            betAsk.draw()#ask how much they want to bet
            mywin.flip()
            trialtime = core.Clock()
            trialtime.reset()
            bet = WaitForKeyInput() #recieve bet input
            try:
                bet = int(bet)
            except ValueError:
                bet = 999
                continue
            RT = trialtime.getTime()
        #write to data file
        bet = str(bet)
        bet = unicode(bet)
        if os.path.exists(fileName): #create/modify data file
            dataFile =open(fileName, 'a') #opens in 'a' not 'wb' in case they need to restart
            fieldnames = ['Subject', 'Session','Round','Word', 'Bet','RT']
            dataFileWriter = csv.DictWriter(dataFile, lineterminator='\n', fieldnames = fieldnames)
            try:
                print type(bet)
                if bet.isnumeric() == True: #if they did enter a bet, add this row
                    print "FIRST"
                    print bet
                    i +=1
                    already = True
                    global dataFileWriter
                    dataFileWriter.writerow({'Subject': expInfo['Subject'], 'Session': expInfo['Session'],'Round': round,\
                    'Word': words[i-1],'Bet':bet.encode("ascii"),'RT': RT})
            except AttributeError: #else repeat
                i=i
                already = False
                print "blank entered1"
                continue
            dataFile.close()
        else:
            with open(fileName, 'w') as dataFile:
                fieldnames = ['Subject', 'Session', 'Round', 'Word', 'Bet','RT']
                dataFileWriter = csv.DictWriter(dataFile, lineterminator='\n', fieldnames = fieldnames)
                dataFileWriter.writeheader()
                try:
                    print bet
                    if bet.isnumeric() == True: #if they did enter a bet, add this row
                        i +=1
                        already = True
                        global dataFileWriter
                        dataFileWriter.writerow({'Subject': expInfo['Subject'], 'Session': expInfo['Session'],'Round': round,\
                        'Word': words[i-1],'Bet':bet.encode("ascii"),'RT': RT})
                except AttributeError: #else repeat
                    i = i
                    already = False
                    print "blank entered2"
                    continue
                dataFile.close()
    instructions[2].draw() #"PREPARE FOR RECALL"
    mywin.flip()
    core.wait(3)
    wordList = './words/%s/words%i.txt' %(version, round)
    l = list(cor for cor in open(wordList).read().split("\n") if cor)#repopulate list because it was loading as a function
    global scoreYet
    event.clearEvents()#clear previous key presses so the below loop runs
    while event.getKeys(keyList=['return'])==[]:#draw window to recall words
        instructions2[1].draw()
        enter.draw()
        mywin.flip()
    scoreYet = False #so that this loop works past round 1
    while scoreYet == False:
        a = WaitForKeyInput2() #get text
        wordsTheyRecalled.append(a) #add word they typed to a list of words they Recalled
        if wordsTheyRecalled == []: scoreYet = False #don't let them go if they haven't done anything!
    round += 1
    return wordsTheyRecalled
def fScore():
    global score
    roundscore = 0
    wordsToScore = wordsTheyRecalled
    wordList = './words/%s/words%s.txt' %(version, round-1)
    throwAwayWords = list(cor for cor in open(wordList).read().split("\n") if cor)
    for w in wordsToScore:
        instructions2[2].draw()
        core.wait(0.1)
        if w in throwAwayWords:
            risk = int(findBet(w))
            throwAwayWords.remove(w)
            score += risk
            roundscore += risk
            acc = 1
            writeToDataFile(scorefileName,w,risk,score,acc)
            print score
    for w in throwAwayWords:
        risk = int(findBet(w))
        score -= risk
        roundscore -= risk
        acc = 0
        writeToDataFile(scorefileName,w,risk,score, acc)
        print score
    return score,roundscore
def showInstructions(n):
    while event.getKeys(keyList=['return'])==[]:
        intro[n].draw()
        mywin.flip()

feed = visual.TextStim(mywin, height=50,text='Your Score For This Level Was: ',color="white",pos=(0,0))
rst = visual.TextStim(mywin, height=50,text= 'x',color="white",pos=(0,-100))
def feedback(levelscore):
    rst.text = str(levelscore)
    questions.draw()
    feed.draw()
    rst.draw()
    mywin.flip()
    core.wait(6)
def practice():
    w = visual.TextStim(mywin, height=55,text= 'hi',color="white",pos=(0,0))
    already = True
    bet = 999
    wordList = ['one', 'two', 'three']
    #show words
    i=0
    event.clearEvents()
    while event.getKeys(keyList=['return'])==[]:#wait till ready
        instructions2[3].draw()
        enter.draw()
        mywin.flip()
    while i <3:
        bet = 999
        questions.draw()#draw blank
        w.text = wordList[i]
        w.draw()
        mywin.flip()#show word
        core.wait(2)#wait 2 seconds
        while bet > 10:
            print type(bet)
            print bet
            print bet > 10
            core.wait(0.05)

            betAsk.draw()#ask how much they want to bet
            mywin.flip()
            trialtime = core.Clock() #TIMING
            trialtime.reset()#TIMING
            bet = WaitForKeyInput() #recieve bet input
            try:
                bet = int(bet)
            except ValueError:
                bet = 999
                continue
        i+=1
#--------------------------------------------------------------------------------------------
if round ==1:
    for i in range(0,4):
        showInstructions(i)
#Practice betting---------------------------------------------------------------------------
    practice()
#--------------------------------------------------------------------------------------------
#Run------------------------------------------------------------------------------------------
for x in range(round-1,loops):
    k = RunBlock()
    for word in wordsTheyRecalled: #still record the words they typed.
        recordWordsTheyTyped(inputFileName,word)
    s,rs = fScore() #Score input and return score
    feedback(rs) #show them their score
    wordsTheyRecalled= [] #hopefully this makes it so that it doesnt show the old words
#----------------------------------------------------------------------------------------------
#Thank you-------------------------------------------------------------------------------------
event.clearEvents()
thanks = visual.TextStim(mywin, height=30,text='Thank you for completing this task!',color="white",pos=(0, 0))
questions.draw()
thanks.draw()
mywin.flip()
core.wait(6)
core.quit()
