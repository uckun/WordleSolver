#!/usr/bin/python
def check_word(w, res, lettersIn, lettersOut, lettersCorrect, lettersIncorrect,
               letterMinCounts=None):
    for i, c in enumerate(w):
        r = int(res[i])
        if r == 1:
            if w.count(c) > 1:  # repeated letter; treat it differently
                counter = 0
                for j, k in enumerate(w):
                    if k == c and int(res[j]) > 1:  # only count same letter
                        counter = counter + 1
                if counter > 0:
                    continue
            lettersOut.append(c)
            if lettersIn.count(c) > 0:
                lettersIn.remove(c)
        elif r == 2:
            if c not in lettersIncorrect:
                lettersIncorrect[c] = []
            if i not in lettersIncorrect[c]:
                lettersIncorrect[c].append(i)
        else:  # correct location
            if c not in lettersCorrect:
                lettersCorrect[c] = []
            if i not in lettersCorrect[c]:
                lettersCorrect[c].append(i)

    # Update per-letter minimum counts.
    # Two yellow results for the same letter from *different* guesses both refer
    # to the same letter in the answer; only a SINGLE guess with N non-gray
    # occurrences of a letter proves the answer contains at least N of it.
    # We therefore track the maximum non-gray count across all guesses.
    if letterMinCounts is not None:
        for c in set(w):
            non_gray = sum(1 for j, k in enumerate(w) if k == c and int(res[j]) > 1)
            letterMinCounts[c] = max(letterMinCounts.get(c, 0), non_gray)


def eliminateCandidates(candidates, lettersOut, lettersCorrect, lettersIncorrect,
                        letterMinCounts=None):
    newCandidates = list()
    for cand in candidates:
        reject_count = 0
        for reject in lettersOut:
            if cand.count(reject) > 0:
                reject_count += 1
        # Support multiple positions per letter (duplicate letters in target)
        for key, positions in lettersCorrect.items():
            lmc_val = letterMinCounts.get(key) if letterMinCounts is not None else None
            if lmc_val is not None:
                # Use cross-guess-safe min count: max of confirmed green positions
                # vs the best non-gray count we ever saw in a single guess.
                min_count = max(len(positions), lmc_val)
            else:
                min_count = len(positions) + len(lettersIncorrect.get(key, []))
            if cand.count(key) < min_count:
                reject_count += 1
            else:
                for pos in positions:
                    if cand[pos] != key:
                        reject_count += 1
                        break
        for key, positions in lettersIncorrect.items():
            lmc_val = letterMinCounts.get(key) if letterMinCounts is not None else None
            if lmc_val is not None:
                green_count = len(lettersCorrect.get(key, []))
                min_count = max(green_count, lmc_val)
            else:
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
