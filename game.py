from wordle import Wordle
from guesser import Guesser
import argparse
import time
import sys
import os

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

class Game:
    def __init__(self):
        self.RESULTS = []  # was the word guessed?
        self.GUESSES = []  # number of guesses per game
        
    def score(self, result, guesses):
        if '-' in result or '+' in result:
            # word was not guessed
            result = False
        else:
            result = True
        self.RESULTS.append(result)
        self.GUESSES.append(guesses)

    def game(self, wordle, guesser):
        endgame = False
        guesses = 0
        result = '+++++'
        while not endgame:
            guess = guesser.get_guess(result)
            guesses += 1
            result, endgame = wordle.check_guess(guess)    
            print(result)
        return result, guesses
    
    def manual_feedback_game(self, guesser):
        """Play a game where the user provides feedback manually"""
        endgame = False
        guesses = 0
        result = '+++++'
        
        print('Welcome to manual feedback mode!')
        print('The guesser will suggest words, and you provide feedback.')
        print('Use these symbols in your feedback:')
        print('- A letter means it\'s in the correct position (green)')
        print('- A - means the letter is in the word but wrong position (yellow)')
        print('- A + means the letter is not in the word (gray)')
        print('Example: "a++++" means only "a" is correct and in position 1')
        print('Enter the word itself to indicate the guess was correct')
        
        while not endgame:
            guess = guesser.get_guess(result)
            print(f"Guesser suggests: {guess}")
            guesses += 1
            
            while True:
                result = input("Enter your feedback (or the word if correct): ").lower().strip()
                
                # Validate feedback format
                if result == guess:
                    print(f'Great! The word was guessed in {guesses} attempts.')
                    endgame = True
                    break
                elif len(result) != 5:
                    print("Please enter exactly 5 characters of feedback")
                    continue
                elif not all(c.isalpha() or c in ['+', '-'] for c in result):
                    print("Invalid feedback format. Use letters, +, or -")
                    continue
                else:
                    break
                    
        return result, guesses
            
def main():
    # set up command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--r', type=int, help='number of rounds to play')
    parser.add_argument('--p', action='store_true', help='whether to print the game or not')
    parser.add_argument('--m', action='store_true', help='play in manual feedback mode')

    # parse command line arguments
    args = parser.parse_args()

    # Create game instance
    game = Game()

    # if --r is set, play the game automatically for r rounds
    if args.r:
        start_time = time.time() # log start time
        
        # set up game
        wordle = Wordle()
        guesser = Guesser('console')
        
        # block print if --p is not set
        if not args.p:
            blockPrint()

        for run in range(args.r):
            # reset game
            guesser.restart_game()
            wordle.restart_game()

            # play the game
            results, guesses = game.game(wordle, guesser)
            print()

            # score the game
            game.score(results, guesses)

        enablePrint()

        # print results if --p is set
        if args.p:            
            print(f"Proportion of words guessed correctly: {game.RESULTS.count(True)/len(game.RESULTS):.2%}")
            print(f"Average number of guesses: {sum(game.GUESSES)/len(game.GUESSES):.4f} ")
            print(f"Total execution time: {time.time() - start_time:.2f} seconds")
        # else print results in csv format
        else:
            print(f"{game.RESULTS.count(True)/len(game.RESULTS):.2%},{sum(game.GUESSES)/len(game.GUESSES):.4f},{time.time() - start_time:.2f}")

    # Manual feedback mode where guesser suggests a guess and user provides feedback
    elif args.m:
        # Set up guesser in console mode (it will make suggestions)
        guesser = Guesser('console')
        
        # Play the game with manual feedback
        game.manual_feedback_game(guesser)
        
    # Original manual mode where user enters guesses
    else:
        # set up game
        guesser = Guesser('manual')
        wordle = Wordle()

        # play the game
        print('Welcome! Let\'s play wordle! ')
        game.game(wordle, guesser)

if __name__ == '__main__':
    main()