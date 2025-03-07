import bruteforce

def main():
    print("Starting")
    wordlist = "wordlists/fasttrack.txt"
    # passwordHash = bruteforce.hashPasswordWithAlgo(password, algo)
    passwordHash = input("Enter the hash to break: ")
    mangle = True

    algo = bruteforce.determineHashAlgo(passwordHash)
    
# Hashes
    # hash = input("Input hash to use: ")

# input pass + algo
    # password, algo = bruteforce.getPasswordFromStdIn()
    # passwordHash = bruteforce.hashPasswordWithAlgo(password, algo)

# input wordlist    
    # wordlist = "wordlists/" + input("Input the filename of the word list to use: ")

    # print(bruteforce.startCrack(passwordHash, algo, wordlist, mangle))

    # print("cuda", bruteforce.get_cuda_cores())

    for _ in range(1):
        print(bruteforce.startCrackWithCPU(passwordHash, algo, wordlist, True))
    # bruteforce.mangleList("testtest")
    # bruteforce.mangleList("database")
            

if (__name__ == "__main__"):
    main()
