from  WordleSolverDefs import *

#receive score from user:
# 1 indicates the letter in that position does not exist in the word.
# 2 indicates the letter in that position exists in the word, but it is in the wrong position.
# 3 indicates the letter in that position exists in the word, and it is in the right position.

letters_in = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') # al letters in at first
letters_out = list() # empty list
letters_correct = dict()  # letter -> list of correct positions (0-indexed)
letters_incorrect = dict()  # letter -> list of wrong positions (0-indexed)
count_letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
candidates = list()
previousAnswers = list()
letter_counts = dict()
solved = False

my_file = open("/Users/serdar/Documents/Software Development/WordleSolver/allwords.txt", "r")
content = my_file.read()
content_list = content.split("\n")
my_file.close()
five_letter_words = []
for x in content_list:
  if len(x) == 5:
      five_letter_words.append(x)

for cl in count_letters:
    letter_counts.update({cl: 0})
for l in five_letter_words:
    for c in l:
        count = letter_counts.get(c)
        letter_counts.update({c: count + 1})
word_frequency_dict = dict()
for w in five_letter_words:
    x = 0
    for c in w:
        x += letter_counts.get(c)
        # punish words where a letter appears more than once
        if w.count(c)>1:
            x -= letter_counts.get(c)/2
    word_frequency_dict.update({w:x})
sortedWordFrequencyTupleList = sorted(word_frequency_dict.items(), key=lambda x: x[1], reverse=True)

for tup in sortedWordFrequencyTupleList:
    if notPreviouslyUsed(tup[0]):
        candidates.append(tup[0])
    else:
        previousAnswers.append(tup[0])

while not solved:
    newWord = result = ''
    while not(valid_word(newWord)):
        newWord = input("Select and enter new word: ").upper()
    while not(valid_result(result)):
        result = input("Enter result from Wordle: ")
    check_word(newWord, result, letters_in, letters_out, letters_correct, letters_incorrect)
    if result == '33333':
        print('Solved!')
        if notPreviouslyUsed(newWord):
            addToCorrectAnswers(newWord)
        solved = True
    else:
        candidates = eliminateCandidates(candidates, letters_out, letters_correct, letters_incorrect)
        previousAnswers = eliminateCandidates(previousAnswers, letters_out, letters_correct, letters_incorrect)
        print(str(len(candidates)) + ' five letter words remaining')
        print('Candidates:')
        print(candidates)
        print('Suitable Previous Answers:')
        print(previousAnswers)




