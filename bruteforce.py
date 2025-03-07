import hashlib
import time
from itertools import product
import os
import multiprocessing


"""
Testing
password sha1 	- 5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8
password sha256 - 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8
password md5 	- 5f4dcc3b5aa765d61d8327deb882cf99
P@ssw0rd sha1	- 21bd12dc183f740ee76f27b78eb39c8ad972a757
P@ssword sha256 - b03ddf3ca2e714a6548e7495e2a03f5e824eaac9837cd7f159c67b90fb4b7342
P@ssword md5	- 161ebd7d45089b3446ee4e0d86dbcf92
"""


def getPasswordFromStdIn():
	"""
	Prompts user for a password and hashing algorithm to use

	Returns:
		String, String: Password to hash, Algorithm to use
	"""

	password = input("Enter password to hash: ")
	algo = input("Enter algorithm to use (MD5, SHA1, SHA256): ").lower()

	while algo not in ("sha256", "sha1", "md5"):
		algo = input("Incorrect algorithm entered, please try again: ").lower()

	return password, algo


def hashPasswordWithAlgo(password, algo):
	"""
	Hashes a given password based on the given algorithm

	Args:
		password (String): Password to hash
		algo (String): Algorithm to use

	Returns:
		String: hex value of hash
	"""

	if algo == "md5":
		return hashlib.md5(password.encode()).hexdigest()
	elif algo == "sha1":
		return hashlib.sha1(password.encode()).hexdigest()
	elif algo == "sha256":
		return hashlib.sha256(password.encode()).hexdigest()


def hashPasswordWithoutAlgo(password):
	"""
	Given a password, returns a list of hashes

	Args:
		password (String): Password to hash

	Returns:
		List: List of hash values in hex
	"""

	return [hashlib.md5(password.encode()).hexdigest(),
			hashlib.sha1(password.encode()).hexdigest(),
			hashlib.sha256(password.encode()).hexdigest()]


def determineHashAlgo(password):
	"""
	Given a hash, guesses the algorithm

	Args:
		password (String): Hash to guess

	Returns:
		String: Name of guessed algorithm
	"""

	if len(password) == 32:
		return "md5"
	elif len(password) == 40:
		return "sha1"
	elif len(password) == 64:
		return "sha256"


def crackPassword(passwordHash, algo, wordList, mangle, solution):
	"""
	Attempts to find a hash value that matches the given hash using a word list
	If given the mangle flag, creates variants of each word with random chars, capitalization, etc

	Args:
		passwordHash (String): Hash to match
		algo (String): Hashing algorithm to test with
		wordList (List): List of words to use
		mangle (Bool): Mangles each words
		solution (String): Return variable for the solution (if found)
	"""

	for word in wordList:
		mangledList = [word]

		if type(word) is list or solution.value is not None:
			return

		if mangle and word != "":
			mangledList = mangleList(word)

		for mangledWord in mangledList:
			if type(word) is list or solution.value is not None:
				return
		
			if algo == "md5" and hashlib.md5(mangledWord.encode()).hexdigest() == passwordHash:
				solution.value = mangledWord
				return
				
			if algo == "sha1" and hashlib.sha1(mangledWord.encode()).hexdigest() == passwordHash:
				solution.value = mangledWord
				return
			
			if algo == "sha256" and hashlib.sha256(mangledWord.encode()).hexdigest() == passwordHash:
				solution.value = mangledWord
				return

	
def startCrackWithCPU(passwordHash, algo, file, mangle):
	"""
	Brute forces a given hash with a wordlist with multi-threading
	If given the mangle flag, it calls a function to 'mangle' the list

	Args:
		passwordHash (String): Hash to match
		algo (String): Algorithm to use
		file (String): File containing word list
		mangle (Bool): Flag to mangle each word

	Returns
		String: Returns found word or None type
	"""

	tic = time.perf_counter()
	try:
		with open(file, "r") as wordListFile:
			wordList = wordListFile.read().splitlines()
	except Exception:
		print(Exception)
		print("Error reading file")
		return None
	
	# w/ multiprocessing
	manager = multiprocessing.Manager()
	solution = manager.Value('str', None)

	numThreads = multiprocessing.cpu_count() - 2

	seperatedList = list(divideList(wordList, numThreads))

	# Create threads
	threads = []
	for i in range(numThreads):
		thread = multiprocessing.Process(target=crackPassword, args=(passwordHash, algo, seperatedList[i], mangle, solution))
		threads.append(thread)
		thread.start()
	for thread in threads:
		thread.join()
	
	toc = time.perf_counter()
	print(f"{toc - tic:0.4f} seconds")

	return solution.value


def divideList(list, num):
	"""
	Divides a list into num sublists

	Args:
		list (List): List to subdivide
		num (Int): Number of chunks

	Yields:
		List: List containing subdivided list, each of size Size
	"""

	for i in range(num):
		yield list[i::num]


def mangleList(masterWord):
	"""
	Given a word, generates a list of variants that are 'mangled.' 
	Base cases are all lowercase, all uppercase, first letter capitalized, and word reversed.
	These are sent into leet converters , ex 'e' to '3'.
	These are sent into common pattern appenders and prependers

	Args:
		masterWord (String): Word to mangle

	Returns:
		List: String list of mangled words
	"""
	
	wordList = []

	wordList = [masterWord, masterWord.upper()] 				# whole word uppercase
	wordList.append(masterWord.lower())							# whole word lowercase
	wordList.append(masterWord[::-1])							# reverse word

	temp = masterWord[0].upper()								# first letter uppercase
	for i in range(1, len(masterWord)):
		temp += masterWord[i]
	wordList.append(temp)

	wordList = list(set(wordList))								# remove duplicates

	for _ in range(2):											# 2 loops of symbols and numbers, so they can combine
		temp = []
		for x in wordList:
			temp.extend(generateLeetVariants(x))
			temp.extend(generateSymbolVariants(x))
		wordList.extend(temp)

	wordList = list(set(wordList))

	temp1 = wordList
	temp2 = []
	for x in temp1:
		temp2.extend((f"{x}1", f"{x}123", f"{x}abc", f"{x}!")) 	# Append common patterns
		temp2.extend((f"1{x}", f"123{x}", f"abc{x}", f"!{x}")) 	# Prepend common patterns
	wordList.extend(temp2)
	
	if len(wordList) < 220:										# prevent creates lists > 50000, takes too long
		for x in temp1:
			for i in range(1970, 2023):
				temp2.append(x + str(i))
				temp2.append(str(i) + x)
		wordList.extend(temp2)

	wordList = list(set(wordList))

	return wordList


def generateLeetVariants(word):
	"""
	Generates leet variants of a word

	Args:
		word (String): original word

	Returns:
		List: String list of word variants
	"""

	replace = {'a': '4', 'b': '8', 'e': '3', 'g': '6', 'i': '1', 'o': '0', 's': '5', 't': '7', 'z': '2'}

	possibles = []
	for l in word:
		ll = replace.get(l, l)
		possibles.append( (l,) if ll == l else (l, ll) )
	
	return [ ''.join(t) for t in product(*possibles) ]


def generateSymbolVariants(word):
	"""
	Generates symbol variants of a word (ex pass can become pa$$)

	Args:
		word (String): original word

	Returns:
		List: String list of symbol variants
	"""

	replace = {'a': '@', 's': '$'}

	possibles = []
	for l in word:
		ll = replace.get(l, l)
		possibles.append( (l,) if ll == l else (l, ll) )
	
	return [ ''.join(t) for t in product(*possibles) ]


def getWordLists():	
	files = os.listdir(os.getcwd()+'/wordlists/')
	files = [f for f in files if os.path.isfile(os.getcwd() +'/wordlists/'+f)] 	#Filtering only the files.
	files = [f for f in files if f.endswith(".txt")] 							#Filtering only the txt.

	return files
