#!/usr/bin/python
def check_word(w, res, lettersIn, lettersOut, lettersCorrect, lettersIncorrect):
    for i, c in enumerate(w):
        r = int(res[i])
        if r == 1:
            if w.count(c) > 1:  # repeated letter; treat it differently
                counter = 0
                for j, k in enumerate(w):
                    if int(res[j]) > 1:
                        counter = counter + 1
                if counter > 0:
                    continue
            else:
                lettersOut.append(c)
                if lettersIn.count(c) > 0:
                    lettersIn.remove(c)
        elif r == 2:
            if c not in lettersIncorrect:
                lettersIncorrect[c] = []
            lettersIncorrect[c].append(i)
        else:  # correct location
            if c not in lettersCorrect:
                lettersCorrect[c] = []
            lettersCorrect[c].append(i)


def eliminateCandidates(candidates, lettersOut, lettersCorrect, lettersIncorrect):
    newCandidates = list()
    for cand in candidates:
        reject_count = 0
        for reject in lettersOut:
            if cand.count(reject) > 0:
                reject_count += 1
        # Support multiple positions per letter (duplicate letters in target)
        for key, positions in lettersCorrect.items():
            min_count = len(positions) + len(lettersIncorrect.get(key, []))
            if cand.count(key) < min_count:
                reject_count += 1
            else:
                for pos in positions:
                    if cand[pos] != key:
                        reject_count += 1
                        break
        for key, positions in lettersIncorrect.items():
            min_count = len(positions) + len(lettersCorrect.get(key, []))
            if cand.count(key) < min_count:
                reject_count += 1
            else:
                for pos in positions:
                    if cand[pos] == key:
                        reject_count += 1
                        break
        if reject_count == 0:
            newCandidates.append(cand)
    return newCandidates


def valid_result(result):
    if (len(result) != 5) or (result.isdigit()) is False:
        return 0
    else:
        for i, c in enumerate(result):
            f = int(c)
            if (f != 1) and (f != 2) and (f != 3):
                return 0
            else:
                continue
        return 1


def valid_word(word):
    if (len(word) != 5) or (word.isalpha() is False):
        return 0
    return 1


def addToCorrectAnswers(word):
    correctFile = open("/Users/serdar/Documents/Software Development/WordleSolver/correctWords.txt", "a")
    correctFile.write(word)
    correctFile.write('\n')
    correctFile.close()


def notPreviouslyUsed(word):
    correctFile = open("/Users/serdar/Documents/Software Development/WordleSolver/correctWords.txt", "r")
    content = correctFile.read()
    contentList = content.split("\n")
    correctFile.close()
    for x in contentList:
        if word == x:
            return 0
        else:
            continue
    return 1
