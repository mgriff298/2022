from cProfile import run
from curses.ascii import BS
from glob import glob
from pickle import FALSE, TRUE
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ingest words and create initial dataframe 
def readData():
    global numOfGuesses
    numOfGuesses = 0

    wordListInit = pd.read_excel('Wordle_words.xlsx', sheet_name='FullList')
    wordListInit['active'] = 1
    wordListInit['notGuessed'] = 1
    wordListInit['repeatLets'] = 1
    return wordListInit

# create dataframe of letters
def containLets(wordList):
    lets = []
    letsList = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    dfLets = pd.DataFrame(lets)

    for let in letsList:
        dfLets.loc[let,('counts')] = len(wordList[wordList['Words'].str.contains(let)])

    return dfLets

# create full dataframe used moving forward, includes analysis of which letters will yield the most information when guessed
def createFullDf(wordList2):
    wordList = wordList2[wordList2['active']==1]

    if wordList.shape[0] == 1:
        wordList.loc[:,('firstLetVal')] = 1
        wordList.loc[:,('secondLetVal')] = 1
        wordList.loc[:,('thirdLetVal')] = 1
        wordList.loc[:,('fourthLetVal')] = 1
        wordList.loc[:,('fifthLetVal')] = 1
    else:
        firstStats = wordList['firstLetter'].value_counts()
        secondStats = wordList['secondLetter'].value_counts()
        thirdStats = wordList['thirdLetter'].value_counts()
        fourthStats = wordList['fourthLetter'].value_counts()
        fifthStats = wordList['fifthLetter'].value_counts() 

        dfLetters = containLets(wordList)
        firstCont = dfLetters.loc[wordList['firstLetter']].squeeze()
        secondCont = dfLetters.loc[wordList['secondLetter']].squeeze()
        thirdCont = dfLetters.loc[wordList['thirdLetter']].squeeze()
        fourthCont = dfLetters.loc[wordList['fourthLetter']].squeeze()
        fifthCont = dfLetters.loc[wordList['fifthLetter']].squeeze()
    
        firstMaxVal = firstStats.loc[wordList['firstLetter']]
        secondMaxVal = secondStats.loc[wordList['secondLetter']]
        thirdMaxVal = thirdStats.loc[wordList['thirdLetter']]
        fourthMaxVal = fourthStats.loc[wordList['fourthLetter']]
        fifthMaxVal = fifthStats.loc[wordList['fifthLetter']]


        wordList.loc[:,('probFG')] = firstMaxVal.values/len(wordList)
        wordList.loc[:,('probFB')] = (len(wordList)-firstCont.values)/len(wordList)
        wordList.loc[:,('probFM')] = (firstCont.values-firstMaxVal.values)/len(wordList)

        wordList.loc[:,('probSG')] = secondMaxVal.values/len(wordList)
        wordList.loc[:,('probSB')] = (len(wordList)-secondCont.values)/len(wordList)
        wordList.loc[:,('probSM')] = (secondCont.values-secondMaxVal.values)/len(wordList)

        wordList.loc[:,('probTG')] = thirdMaxVal.values/len(wordList)
        wordList.loc[:,('probTB')] = (len(wordList)-thirdCont.values)/len(wordList)
        wordList.loc[:,('probTM')] = (thirdCont.values-thirdMaxVal.values)/len(wordList)

        wordList.loc[:,('probFoG')] = fourthMaxVal.values/len(wordList)
        wordList.loc[:,('probFoB')] = (len(wordList)-fourthCont.values)/len(wordList)
        wordList.loc[:,('probFoM')] = (fourthCont.values-fourthMaxVal.values)/len(wordList)

        wordList.loc[:,('probFifG')] = fifthMaxVal.values/len(wordList)
        wordList.loc[:,('probFifB')] = (len(wordList)-fifthCont.values)/len(wordList)
        wordList.loc[:,('probFifM')] = (fifthCont.values-fifthMaxVal.values)/len(wordList)

        wordList = wordList.replace(0, 1)

        wordList.loc[:,('firstLetVal')] = np.log2(1/wordList['probFG'])*wordList['probFG']+ np.log2(1/wordList['probFB'])*wordList['probFB'] + np.log2(1/wordList['probFM'])*wordList['probFM']
        wordList.loc[:,('secondLetVal')] = np.log2(1/wordList['probSG'])*wordList['probSG'] + np.log2(1/wordList['probSB'])*wordList['probSB'] + np.log2(1/wordList['probSM'])*wordList['probSM']
        wordList.loc[:,('thirdLetVal')] = np.log2(1/wordList['probTG'])*wordList['probTG'] + np.log2(1/wordList['probTB'])*wordList['probTB'] + np.log2(1/wordList['probTM'])*wordList['probTM']
        wordList.loc[:,('fourthLetVal')] = np.log2(1/wordList['probFoG'])*wordList['probFoG'] + np.log2(1/wordList['probFoB'])*wordList['probFoB'] + np.log2(1/wordList['probFoM'])*wordList['probFoM']
        wordList.loc[:,('fifthLetVal')] = np.log2(1/wordList['probFifG'])*wordList['probFifG'] + np.log2(1/wordList['probFifB'])*wordList['probFifB'] + np.log2(1/wordList['probFifM'])*wordList['probFifM']
    
    return wordList

# calculates the information score after each guess
def calcScore(wordListScore):
    global numOfGuesses
    if numOfGuesses == 0 or numOfGuesses == 1:
        wordListScore.loc[:,('repeatLets')] = np.where(wordListScore['Words'].apply(lambda x: len(set(x)))!=5, 0, wordListScore['repeatLets'])
        wordListScore.loc[:,('score')] = (wordListScore['firstLetVal'] + wordListScore['secondLetVal'] + wordListScore['thirdLetVal'] + wordListScore['fourthLetVal'] + wordListScore['fifthLetVal'])*wordListScore['repeatLets']
        #print('numofguesses is 0)')
        print(wordListScore.sort_values(by=['score'], ascending=False))
        #wordListScore.loc[:,('active')] = 1
        #wordListScore.loc[:,('score')] = (wordListScore['firstLetVal'] + wordListScore['secondLetVal'] + wordListScore['thirdLetVal'] + wordListScore['fourthLetVal'] + wordListScore['fifthLetVal'])*wordListScore['active']
    elif numOfGuesses == 2:
        #wordListScore.loc[:,('notGuessed')] = np.where(wordListScore['Words'].apply(lambda x: len(set(x)))!=5, 0, wordListScore['notGuessed'])
        wordListScore.loc[:,('score')] = (wordListScore['firstLetVal'] + wordListScore['secondLetVal'] + wordListScore['thirdLetVal'] + wordListScore['fourthLetVal'] + wordListScore['fifthLetVal'])*wordListScore['active']
        #print('second guess?')
        print(wordListScore.sort_values(by=['score'], ascending=False))
        #wordListScore['score'] = (wordListScore['firstLetVal'] + wordListScore['secondLetVal'] + wordListScore['thirdLetVal'] + wordListScore['fourthLetVal'] + wordListScore['fifthLetVal'])*wordListScore['active']
    else:
        wordListScore.loc[:,('score')] = (wordListScore['firstLetVal'] + wordListScore['secondLetVal'] + wordListScore['thirdLetVal'] + wordListScore['fourthLetVal'] + wordListScore['fifthLetVal'])*wordListScore['active']
        print(wordListScore.sort_values(by=['score'], ascending=False))
    return wordListScore

# for manual usage, ingests user's guess
def getGuess():
    global numOfGuesses
    guess = input("Enter your guess: ")
    if len(guess)!=5:
        getGuess()
    numOfGuesses += 1
    return guess

# grabs the first letter of the guess
def getGuessLet1(guess):
    guess1Let1 = guess[0]
    return guess1Let1

# grabs the second letter of the guess
def getGuessLet2(guess):
    guess1Let2 = guess[1]
    return guess1Let2

# grabs the third letter of the guess
def getGuessLet3(guess):
    guess1Let3 = guess[2]
    return guess1Let3

# grabs the fourth letter of the guess
def getGuessLet4(guess):
    guess1Let4 = guess[3]
    return guess1Let4

# grabs the fifth letter of the guess
def getGuessLet5(guess):
    guess1Let5 = guess[4]
    return guess1Let5

# interprets the user given feedback of the guess for the first letter
def let1Feedback(guess1Let1,wordList):
    guess1Let1Feed = input("Feedback for letter 1? (g [letter in correct position]/ b [letter is not in word]/ m [letter is in word but not in the correct spot])")
    wordList.loc[:,('notGuessed')] = np.where(wordList['Words'].str.contains(guess1Let1),0,wordList['notGuessed'])
    if guess1Let1Feed == 'g':
        wordList.loc[:,('active')] = np.where(wordList['firstLetter']!=guess1Let1,0,wordList['active'])
    elif guess1Let1Feed == 'b':
        wordList.loc[:,('active')] = np.where(wordList['Words'].str.contains(guess1Let1),0,wordList['active'])
    elif guess1Let1Feed == 'm':
        wordList.loc[:,('active')] = np.where(wordList['firstLetter']==guess1Let1,0,wordList['active'])
        wordList.loc[:,('active')] = np.where(wordList['Words'].str.contains(guess1Let1) == False,0,wordList['active'])   
    else:
        print("Not a valid option.") 
        let1Feedback(guess1Let1, wordList)
    return wordList, guess1Let1Feed

# interprets the user given feedback of the guess for the second letter
def let2Feedback(guess1Let2, wordList):
    guess1Let2Feed = input("Feedback for letter 2? (g [letter in correct position]/ b [letter is not in word]/ m [letter is in word but not in the correct spot])")
    wordList.loc[:,('notGuessed')] = np.where(wordList['Words'].str.contains(guess1Let2),0,wordList['notGuessed'])
    if guess1Let2Feed == 'g':
        wordList.loc[:,('active')] = np.where(wordList['secondLetter']!=guess1Let2,0,wordList['active'])
    elif guess1Let2Feed == 'b':
        wordList.loc[:,('active')] = np.where(wordList['Words'].str.contains(guess1Let2),0,wordList['active'])
    elif guess1Let2Feed == 'm':
        wordList.loc[:,('active')] = np.where(wordList['secondLetter']==guess1Let2,0,wordList['active'])
        wordList.loc[:,('active')] = np.where(wordList['Words'].str.contains(guess1Let2) == False,0,wordList['active'])   
    else:
        print("Not a valid option.")
        let2Feedback(guess1Let2, wordList)
    return wordList, guess1Let2Feed

# interprets the user given feedback of the guess for the third letter
def let3Feedback(guess1Let3, wordList):
    guess1Let3Feed = input("Feedback for letter 3? (g [letter in correct position]/ b [letter is not in word]/ m [letter is in word but not in the correct spot])")
    wordList.loc[:,('notGuessed')] = np.where(wordList['Words'].str.contains(guess1Let3),0,wordList['notGuessed'])
    if guess1Let3Feed == 'g':
        wordList.loc[:,('active')] = np.where(wordList['thirdLetter']!=guess1Let3,0,wordList['active'])
    elif guess1Let3Feed == 'b':
        wordList.loc[:,('active')] = np.where(wordList['Words'].str.contains(guess1Let3),0,wordList['active'])
    elif guess1Let3Feed == 'm':
        wordList.loc[:,('active')] = np.where(wordList['thirdLetter']==guess1Let3,0,wordList['active'])
        wordList.loc[:,('active')] = np.where(wordList['Words'].str.contains(guess1Let3) == False,0,wordList['active'])   
    else:
        print("Not a valid option.")
        let3Feedback(guess1Let3, wordList)
    return wordList, guess1Let3Feed

# interprets the user given feedback of the guess for the fourth letter
def let4Feedback(guess1Let4, wordList):
    guess1Let4Feed = input("Feedback for letter 4? (g [letter in correct position]/ b [letter is not in word]/ m [letter is in word but not in the correct spot])")
    wordList.loc[:,('notGuessed')] = np.where(wordList['Words'].str.contains(guess1Let4),0,wordList['notGuessed'])
    if guess1Let4Feed == 'g':
       wordList.loc[:,('active')] = np.where(wordList['fourthLetter']!=guess1Let4,0,wordList['active'])
    elif guess1Let4Feed == 'b':
        wordList.loc[:,('active')] = np.where(wordList['Words'].str.contains(guess1Let4),0,wordList['active'])
    elif guess1Let4Feed == 'm':
        wordList.loc[:,('active')] = np.where(wordList['fourthLetter']==guess1Let4,0,wordList['active'])
        wordList.loc[:,('active')] = np.where(wordList['Words'].str.contains(guess1Let4) == False,0,wordList['active'])   
    else:
        print("Not a valid option.")
        let4Feedback(guess1Let4, wordList)
    return wordList, guess1Let4Feed

# interprets the user given feedback of the guess for the fifth letter
def let5Feedback(guess1Let5, wordList):
    guess1Let5Feed = input("Feedback for letter 5? (g [letter in correct position]/ b [letter is not in word]/ m [letter is in word but not in the correct spot])")
    wordList.loc[:,('notGuessed')] = np.where(wordList['Words'].str.contains(guess1Let5),0,wordList['notGuessed'])
    if guess1Let5Feed == 'g':
        wordList.loc[:,('active')] = np.where(wordList['fifthLetter']!=guess1Let5,0,wordList['active'])
    elif guess1Let5Feed == 'b':
        wordList.loc[:,('active')] = np.where(wordList['Words'].str.contains(guess1Let5),0,wordList['active'])
    elif guess1Let5Feed == 'm':
        wordList.loc[:,('active')] = np.where(wordList['fifthLetter']==guess1Let5,0,wordList['active'])
        wordList.loc[:,('active')] = np.where(wordList['Words'].str.contains(guess1Let5) == False,0,wordList['active'])   
    else:
        print("Not a valid option.")
        let5Feedback(guess1Let5, wordList)
    return wordList, guess1Let5Feed

# asks user if they want to continue the game and guess again
def guessAgain():
    again = input("Would you like to guess again? (y/n) ")
    if again != 'y' and again != 'n':
        print("Invalid input")
        guessAgain()
    return again

# for the automated usage, graphs the results of number of guesses it took for the computer to guess each of the words in the input list
def graphGuesses():
    global yAxis
    xAxis = [1,2,3,4,5,6,7,8,9,10]
    mult = []
    for i in range(len(xAxis)):
        mult.append(xAxis[i]*yAxis[i])
    plt.bar(xAxis,yAxis)
    plt.title('Avg Guesses = ' + str(sum(mult)/sum(yAxis)))
    plt.show()

# for the autoamted usage, compares top guess to the desired word
def compareWords(compGuess, word, wordList):
    global notGuessed, yAxis, numOfGuesses
    if compGuess == word:
        wordList = pd.DataFrame()
        if numOfGuesses <=10:
            yAxis[numOfGuesses-1] += 1
        else:
            print('too many guesses') 
        notGuessed = False
    else:
        compData = []
        for i in range(5):
            if compGuess[i] in word:
                compData.append(1)
            else:
                compData.append(0)

            if compGuess[i] == word[i]:
                compData[i] = 2

        for b in range(5):
            feedback = compData[b]
            wordList.loc[:,('notGuessed')] = np.where(wordList['Words'].str.contains(compGuess[b]),0,wordList['notGuessed'])
            if feedback == 2:
                wordList.loc[:,('active')] = np.where(wordList.iloc[:,b+1]!=compGuess[b],0,wordList['active'])
            elif feedback == 0:
                wordList.loc[:,('active')] = np.where(wordList['Words'].str.contains(compGuess[b]),0,wordList['active'])
            elif feedback == 1:
                wordList.loc[:,('active')] = np.where(wordList.iloc[:,b+1]==compGuess[b],0,wordList['active'])
                wordList.loc[:,('active')] = np.where(wordList['Words'].str.contains(compGuess[b]) == False,0,wordList['active']) 
    return wordList

# for automated usage, selects a word to be guessed
def generateWord(dfWords):
    global wordIndex, numOfGuesses, notGuessed
    notGuessed = True
    numOfGuesses = 0
    word = dfWords['Words'][wordIndex]
    wordIndex += 1
    #print(str(word), str(numOfGuesses), 'word')
    return word

# for automated usage, selects the guess that will yield the most information
def generateGuess(dfScores):
    global numOfGuesses
    numOfGuesses += 1
    guess = pd.DataFrame()
    guess['word'] = dfScores.sort_values(by=['score'], ascending=False)['Words'].head(1)
    guess2 = guess.reset_index()
    #print(str(guess2.loc[0].at['word']),str(numOfGuesses), 'guess')
    return guess2.loc[0].at['word']

# main code, allows you to pick manual or automated usage of the code to play wordle
def main():
    global wordIndex, yAxis
    #create df
    empty = False
    wordIndex = 0
    yAxis = [0,0,0,0,0,0,0,0,0,0]
    wordleDf = readData()


    runPath = input('Would you like to manually play or automate the game? (m/a) ')

    if runPath == 'a':
        num = input('How many words would you like to check the results of? (1-12972) ')
        while wordIndex < int(num):
            genWord = str(generateWord(wordleDf))
            wordleDf['active'] = 1
            wordleDf['notGuessed'] = 1
            wordleDfTemp = createFullDf(wordleDf)
            wordleDfTemp = calcScore(wordleDfTemp)
            
            genGuess = str(generateGuess(wordleDfTemp))
            dfComp = compareWords(genGuess, genWord, wordleDf)
            while notGuessed == True:
                wordleDfTemp = createFullDf(dfComp)
                wordleDfTemp = calcScore(wordleDfTemp)
                genGuess = str(generateGuess(wordleDfTemp))
                dfComp = compareWords(genGuess, genWord, wordleDf)
        graphGuesses()   
    elif runPath == 'm':
        wordleDf = readData()
        wordleDfTemp = createFullDf(wordleDf)
        wordleDfTemp = calcScore(wordleDfTemp)
        #get guess and break out the letters
        guess = getGuess()
        let1 = getGuessLet1(guess)
        let2 = getGuessLet2(guess)
        let3 = getGuessLet3(guess)
        let4 = getGuessLet4(guess)
        let5 = getGuessLet5(guess)

        #incorporate game feedback from guess
        let1FeedDf,let1Feed = let1Feedback(let1, wordleDf)
        let2FeedDf,let2Feed = let2Feedback(let2, let1FeedDf)
        let3FeedDf,let3Feed = let3Feedback(let3, let2FeedDf)
        let4FeedDf,let4Feed = let4Feedback(let4, let3FeedDf)    
        let5FeedDf,let5Feed = let5Feedback(let5, let4FeedDf)

        updatedDf = createFullDf(let5FeedDf)
        updatedDf = calcScore(updatedDf)

        if let1Feed== 'g' and let2Feed== 'g' and let3Feed== 'g' and let4Feed== 'g' and let5Feed == 'g' and updatedDf.shape[0] == 1:
            guessed = True
        elif updatedDf.shape[0]==0:
            guessed = True
            empty = True
        else:
            guessed = False


        while guessed == False:
            #anotherGuess = guessAgain()

            #get guess and break out the letters
            guess = getGuess()
            let1 = getGuessLet1(guess)
            let2 = getGuessLet2(guess)
            let3 = getGuessLet3(guess)
            let4 = getGuessLet4(guess)
            let5 = getGuessLet5(guess)

            #incorporate game feedback from guess
            let1FeedDf,let1Feed = let1Feedback(let1, wordleDf)
            let2FeedDf,let2Feed = let2Feedback(let2, let1FeedDf)
            let3FeedDf,let3Feed = let3Feedback(let3, let2FeedDf)
            let4FeedDf,let4Feed = let4Feedback(let4, let3FeedDf)    
            let5FeedDf,let5Feed = let5Feedback(let5, let4FeedDf)

            updatedDf = createFullDf(let5FeedDf)
            updatedDf = calcScore(updatedDf)

            if let1Feed== 'g' and let2Feed== 'g' and let3Feed== 'g' and let4Feed== 'g' and let5Feed == 'g' and updatedDf.shape[0] == 1:
                guessed = True
            elif updatedDf.shape[0]==0:
                guessed = True
                empty = True
            else:
                guessed = False


        if guessed == True and empty!=True:
            print("Congratulations you guessed the word in " + str(numOfGuesses) + " tries")
        else:
            print("No words remaining. Thanks for playing")
    else:
        print('Not a valid answer')



main()
