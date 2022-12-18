# A parser for reading poker hands
# Scenarios are listed in scenarios.txt. 
# They are in the form "{Scenario Name}; Hands for the scenario to call"
# Hands for the scenario to call are in the form of 3 columns sepearted by colons"
# First column is raise second column is call. Hands can be weighted within each column with a colon and must have a comma followed after them in all situatins.
# Example Training Scenario
# UTG vs MP 3-Bet; 1: AA, AKs, KK, QQ, JJ, 0.5: AKo, KQs, KJs, AJs, TT, A5s, 0.25: ATs, 99; 1: AQs 0.5: AKo, KQs, KJs, AJs, TT, 0.25: 99, TT; 


# We parse each line into a readable dictionary of the form. It looks like this:
#dictionary = {name: scenarioName, raiseHands: Hand: weight, callHands: Hand: weight}

# Takes in a set of ranges and returns an array of each hand aligned with its correpsonding weight
def tokenizeHands(ranges):
    ranges = ranges.split(",")
    curWeightArr = []
    for token in ranges:
        token = token.strip()
        # we have a weight category
        if token[0] == "W":
            # get number
            num = ""
            i = 1
            while token[i] != ":":
                num += token[i]
                i += 1
            # Add hand
            curWeightArr.append((token[i+1:].strip(), float(num)))
        else:
            curWeightArr.append((token.strip(),float(num)))
    return curWeightArr

def parseLine(line):
    ret = {}
    splitLine = line.split(";")
    ret["raise"] = tokenizeHands(splitLine[0])
    # need newline incase of depends
    if splitLine[1] != ' ' and splitLine[1] != ' \n':
        ret["call"] = tokenizeHands(splitLine[1])
    else:
        ret["call"] = []
    return ret

def parseLines(filename):
    try:
        f = open(filename)
    except:
        return "Fail to Open File", False
    line = f.readline()
    try:
        res = parseLine(line)
        line = f.readline()
        if line == "":
            return res, True
        line = line.split(":")
        if line[0] == "Depends":
            try:
                res["Depends"] = parseDepends(line)
                return res, True
            except:
                return "File Depended Format Invalid", False
    except:
        return "File Format Invalid", False

def parseDepends(line):
    line = line[1].split(" ")
    arr = []
    for i in range(len(line)):
        if line[i] != "":
            arr.append(line[i])
    return arr
            
def parseDictionaryToFile(filename, dictionary, dependencyFile=None):
    try:
        raiseArr = dictionary["raise"]
        callArr = dictionary["call"]
        f = open(filename, 'w')
        curWeight = None
        for idx, item in enumerate(raiseArr):
            itemWeight = item[1]
            if curWeight is None or curWeight != itemWeight:
                curWeight = itemWeight
                f.write("W" + str(curWeight) + ": ")
            if idx != len(raiseArr)-1:
                f.write(item[0] + ", ")
            else:
                f.write(item[0] + "; ")
            # no comma for last value
        curWeight = None
        for idx, item in enumerate(callArr):
            itemWeight = item[1]
            if curWeight is None or curWeight != itemWeight:
                curWeight = itemWeight
                f.write("W" + str(curWeight) + ": ")
            if idx != len(callArr)-1:
                f.write(item[0] + ", ")
            else:
                f.write(item[0])
        if dependencyFile is not None:
            res, success = parseLines(dependencyFile)
            if success:
                # Build dependency array
                depArr = []
                for key in res["raise"]:
                    depArr.append(key[0]) 
                if res["call"] is not None:
                    for key in res["call"]:
                        if key not in depArr:
                            depArr.append(key[0])
                f.write("\nDepends: ")
                for key in depArr:
                    f.write(key + " ") 
            else:
                return False
        f.close()
        return True
    except:
        return False
