import math
import sys

dataset = [["IBM", "0691197987", "contact@ibm.com", "www.ibm.com"],
    ["Heroku", "4519080374", "feedback@heroku.com", "signup.heroku.com"],
    ["Dockers", "3072134041", "contact@dockers.com", "www.dockers.com"],
    ["ANSYS", "1374023052", "", "www.ansys.com"],
    ["ANSYS, Inc.", "1374023052", "contact@ansys.com", "www.ansys.com"],
    ["The New York Times", "1848312818", "nytnews@nytimes.com", "www.nytimes.com"],
    ["The Gaurdian", "5139764161", "us-hr@gaurdian.com", "www.thegaurdian.com"],
    ["International Business Machines", "0691197987", "contact@ibm.com", "www.ibmserver.com"],
    ["Docker", "6356809766", "contact@docker.com", "www.docker.com"],
    ["The Huffington Post", "6230388160", "scoop@huffingtonpost.com", "www.huffingtonpost.com"],
    ["AMD", "7079013926", "corporate.query@amd.com", "www.amd.com"],
    ["NVIDIA", "1830157005", "info@nvidia.com", "www.nvidia.com"],
    ["Amazon", "8711666456", "ship-confirm@amazon.com", "www.amazon.com"]]

def getWords(database):
    allWords = []
    for record in database:
        for field in record:
            newWords = splitByNonAlphaNumeric(field)
            # print newWords
            allWords = allWords + newWords

    frequencyDict = getFrequencyFromWords(allWords)
    return frequencyDict

def getFrequencyFromWords(words):
    frequencyDict = dict()
    for word in words:
        if word in frequencyDict:
            frequencyDict[word] = frequencyDict[word] + 1
        else:
            frequencyDict[word] = 1

    return frequencyDict

#source: https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python 
def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

# weight the distance between two strings by how common their shared words are. Less common shared words lower the
# computed distance between two words, making them appear more related.
def getWeightedLevDistance(foo, bar, words):
    wordsInFoo = splitByNonAlphaNumeric(foo)
    wordsInBar = splitByNonAlphaNumeric(bar)
    sharedWords = list(set(wordsInFoo) & set(wordsInBar))
    valueInSharedWords = sum((1.0/words[value]) for value in sharedWords) # the more frequenct a word, the less it will be worth.
    #print valueInSharedWords
    return levenshtein(foo, bar) - valueInSharedWords

def computeAverageDistancePerField(database):
    wordsAndFrequencies = getWords(database)
    allComparisons = []
    for i in range(0, len(database) - 1):
        allComparisons = allComparisons + list((zip(database[i], x) for x in database[i:]))

    levDistances = []
    for comparison in allComparisons:
        levDistances.append(averageDistancePerFieldHelper(comparison, wordsAndFrequencies))
    
    averageDistance = [sum(x)/len(levDistances) for x in zip(*levDistances)]
    return averageDistance
        
def averageDistancePerFieldHelper(zippedList, wordsAndFrequencies):
    return [getWeightedLevDistance(*valuePair, words=wordsAndFrequencies) for valuePair in zippedList]

def splitByNonAlphaNumeric(word): # will produce something like ["www", "ansys", com"] from "WWW.ANSYS.COM". http://stackoverflow.com/questions/9246589/split-string-without-non-characters
    return ''.join(character if character.isalnum() else " " for character in word).lower().split()

def getMostSimilarToIndividualRecord(record, listOfOtherRecords, wordFrequencies, averageDistance):
    allComparisons = [zip(record, other) for other in listOfOtherRecords]
    levDistances = []
    results = dict()
    for comparison in allComparisons:
        comparisonDistance = averageDistancePerFieldHelper(comparison, wordFrequencies) 
        #print "for " + str(comparison) + "distance is" + str(comparisonDistance)
        levDistances.append(comparisonDistance)
        results[str(comparisonDistance)] = [otherRecord for (rec, otherRecord) in comparison]
    #for levDist in levDistances:
        # print "For " + str(levDist) +  " weight average is " + str(math.floor(weightClosenessByAverage(levDist, averageDistance)*100))
    return [results[str(value)] for value in (sorted(levDistances, key=lambda x: int(math.floor((weightClosenessByAverage(x, averageDistance))*100))))]

def weightClosenessByAverage(comparison, averageComparison):
    overallWeight = 0
    for field in zip(comparison, averageComparison):
        value1, value2 = field
        differenceFromAverage = value1*abs(1.0/(100.0 if (value2-value1) == 0 else (value2 - value1)))
        # print str(value1) + " " + str(value2) + " " + str(value1 - value2) + " " + str(differenceFromAverage)
        overallWeight = overallWeight + differenceFromAverage

    return overallWeight

def main():
    wordFrequencies = getWords(dataset)
    averageDistance = computeAverageDistancePerField(dataset)
    #print averageDistance
    while True:
        print "Items in dataset are:"
        for i in range(0, len(dataset)-1):
            print str(i) +": " + str(dataset[i])
        print "Select a value by its index to see the records in order of how fuzzily close they are to it."
        sys.stdout.flush()
        x = int(input())
        for record in getMostSimilarToIndividualRecord(dataset[x], dataset, wordFrequencies, averageDistance):
            print record
        print ""

if __name__ == "__main__":
    main()
