import math

# (1) variables practice

length = 12
width = 17

# try printing these out yourself and modifying the variables
area = 12 * 17
area = length * width
# print(area)

########################################################################

# (2) functions practice

def calculate_area(length, width):
    return length * width

def triangle_area(base, height):
    return 0.5 * base * height

# try using these functions yourself in the shell with various values

########################################################################

# (3) modules practice

print(2 * math.pi)
print(math.floor(56.4), math.ceil(56.4))
print(math.sqrt(math.log(244)))
print(math.log(2, 256)) # by default, math.log uses base "e"

########################################################################

# (4) string practice

s = 'keviniscool'

for letter in s:
    print(letter)

for letter in s:
    # search print() in the python docs for more details
    print(letter, ', ', end='')

for letter in s:
    # search print() in the python docs for more details
    print(letter + ',', end='')

########################################################################

# (5) string methods practice

s = 'abcdefgh'

s.endswith('h')
s.isdigit()
s.replace('l', '1')
s.zfill(6)
s.islower()
s.strip('0')

########################################################################

# (6) string functions practice

def longer(s1, s2):
    return max(len(s1), len(s2))

def earlier(s1, s2):
    # the min() function will return the string that comes earlier
    return min(s1, s2)

def count_letter(s, letter):
    count = 0
    for c in s:
        if c == letter:
            count += 1
    return count

# alternate (the "pythonic" way of doing it)
def count_letter2(s, letter):
    return len([x for x in s if x == 'letter'])

def remove_digits(s):
    # solution not using isdigit()
    digits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    res = ''
    for letter in s:
        if letter not in digits:
            res += letter
    return res

def repeat_character(s, letter):
    count = count_letter(s, letter)
    return c * count

def where(s, c):
    count = 0
    for char in s:
        if char == c:
            return count
        count += 1
    return -1   

########################################################################

# (7) lists practice

fruits = ['apple' ,'banana', 'orange', 'cherry', 'grape', 'onion']

print(fruits[2:5])
# careful: printing only fruits[0] will not produce a list!
print([fruits[0]])
print(fruits[3:])
print([fruits[-1]])

fruits.remove('onion')
print(["Mr. Stark"] + ["I don't feel so well"])

numbers = [2, 4, 99, 0, -3.5, 86.9, -101]
numbers.sort()
numbers.reverse()

def every_third(L):
    newL = []
    for i in range(0,len(L),3):
        newL.append(L[i])
    return newL

print(every_third(fruits))
        

def every_ith(L,i):
    newL = []
    for j in range(0,len(L),i):
        newL.append(L[j])
    return newL

print(every_ith(fruits, 2))

########################################################################

# (8) while loops practice

def display_list(L):
    i = 0
    while i < len(L):
        print(L[i])
        i += 1
        
def display_list_even(L):
    i = 0
    while i < len(L):
        if i % 2 == 0:
            print(L[i])
        i += 1
        
def display_list_reverse(L):
    i = len(L) - 1
    while i >= 0:
        print(L[i])
        i -= 1
        
def sum_elements(L):
    i = 0; sum = 0
    while i < len(L) and sum <= 100:
        sum += L[i]
        i += 1
    return sum

def duplicates(L):
    i = 0
    while i+1 < len(L):
        if L[i] == L[i+1]:
            return True
        i += 1
    return False

########################################################################

# (9) nested lists practice

avengers = [["peter parker", "spiderman", True, 22], 
            ["tony stark", "ironman", False, 53], 
            ["stephen strange", "doctor strange", True, 42], 
            ["steve rogers", "captain america", False, 37], 
            ["bruce banner", "the hulk", False, 51], 
            ["peter quill", "starlord", True, 39]]

for avenger in avengers:
    print(avenger)

for avenger in avengers:
    print(avenger[0])

for avenger in avengers:
    if avenger[2]:
        print(avenger)

total = 0
for avenger in avengers:
    total += avenger[3]
print(total)

def nested_lengths(L):
    lens = []
    for l in L:
        lens.append(len(l))
    return lens

########################################################################

# (10) file basics practice

def display_lines(r):
    '''Display the lines of the file/webpage (with leading and trailing
    whitespace removed) from open reader r.'''
    for line in r:
        print(line.strip())

def display_lines_with_text(r, text):
    '''Display the lines of the file/webpage (with leading and trailing
    whitespace removed) from open reader r that contain the str text.'''
    for line in r:
        if text in line:
            print(line.strip())

def copy_file(r):
    '''Write the lines of open reader r to the file copy.txt.'''
    with open('copy.txt', 'a') as f:
        for line in r:
            f.write(line)
    
# tests
if __name__ == '__main__':

    data_file = open('data.txt')
    display_lines(data_file)
    data_file.close()

    data_file = open('data.txt')
    display_lines_with_text(data_file, 'ene')
    data_file.close()

    data_file = open('data.txt')
    copy_file(data_file)
    data_file.close()