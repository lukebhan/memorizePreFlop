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
    # Raise section can be empty (file starts with ';') when a chart has only
    # calls and/or all-ins, so guard it like the call and all-in sections.
    if splitLine[0].strip() != '':
        ret["raise"] = tokenizeHands(splitLine[0])
    else:
        ret["raise"] = []
    # need newline incase of depends
    if len(splitLine) > 1 and splitLine[1].strip() != '':
        ret["call"] = tokenizeHands(splitLine[1])
    else:
        ret["call"] = []
    # All-In section is optional so older two-section files still parse
    if len(splitLine) > 2 and splitLine[2].strip() != '':
        ret["allin"] = tokenizeHands(splitLine[2])
    else:
        ret["allin"] = []
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
            
def writeSection(f, arr, trailing):
    curWeight = None
    for idx, item in enumerate(arr):
        itemWeight = item[1]
        if curWeight is None or curWeight != itemWeight:
            curWeight = itemWeight
            f.write("W" + str(curWeight) + ": ")
        if idx != len(arr)-1:
            f.write(item[0] + ", ")
        else:
            # no comma for last value
            f.write(item[0])
    f.write(trailing)

def parseDictionaryToFile(filename, dictionary, dependencyFile=None):
    try:
        raiseArr = dictionary["raise"]
        callArr = dictionary["call"]
        allinArr = dictionary.get("allin", [])
        f = open(filename, 'w')
        # Sections are separated by ';' -> raise; call; allin
        writeSection(f, raiseArr, "; ")
        writeSection(f, callArr, "; ")
        writeSection(f, allinArr, "")
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
                for key in res.get("allin", []):
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
