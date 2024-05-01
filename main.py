#!/usr/bin/env python3
import sys
from download_utils import get_pronunciation

if __name__ == '__main__':
    if len(sys.argv) == 2:
        word_inp = sys.argv[1]
        get_pronunciation(word_inp)
    elif len(sys.argv) > 2:
        print("Wrong number of arguments!")
        sys.exit(1)

    while True:
        word_inp = input("Enter word to search for: ")
        get_pronunciation(word_inp)
