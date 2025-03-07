import bruteforce

def main():
    print("Starting")
    wordlist = "wordlists/fasttrack.txt"
    passwordHash = input("Enter the hash to break: ")

    algo = bruteforce.determineHashAlgo(passwordHash)
    
    print(bruteforce.startCrackWithCPU(passwordHash, algo, wordlist, True))
            

if (__name__ == "__main__"):
    main()
