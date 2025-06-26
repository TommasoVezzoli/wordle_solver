# Wordle Solver

An intelligent Wordle solver that uses algorithms combining frequency analysis and information theory to efficiently guess Wordle words. The solver achieves high success rates through a hybrid approach of letter frequency scoring and entropy maximization.

## Features

- **Intelligent AI Guesser**: Uses frequency analysis and entropy calculations to make optimal guesses
- **Multiple Game Modes**: Play manually, run multiple automated simulations, or provide manual feedback
- **Performance Analytics**: Track success rates, average guesses, and execution time
- **Batch Testing**: Run multiple games automatically to evaluate solver performance
- **Advanced Word Filtering**: Sophisticated logic for narrowing down possibilities based on feedback

## Algorithm Overview

The solver uses a hybrid approach that combines:

1. **Frequency Analysis**: Scores words based on letter frequency and positional frequency
2. **Entropy Maximization**: Selects guesses that provide maximum information gain
3. **Smart Disambiguation**: Special logic for efficiently distinguishing between similar words
4. **Dynamic Candidate Filtering**: Continuously narrows the word list based on feedback patterns

## Installation

1. Clone this repository:
```bash
git clone https://github.com/TommasoVezzoli/wordle_solver.git
```

2. Install required dependencies:
```bash
pip install pyyaml rich
```

3. Ensure you have the word list file (`allowed_words.yaml`) in the project directory. This should correspond to the official list of words from the original Wordle game by NY Times.

## Usage

### Basic Usage

Run the solver in different modes:

```bash
# Manual mode - you enter guesses for a word picked at random
python game.py

# Manual feedback mode - AI suggests, you provide feedback
python game.py --m

# Automated solving - run 100 games automatically
python game.py --r 100

# Automated with verbose output
python game.py --r 100 --p
```

### Command Line Options

- `--r N`: Run N automated games and show performance statistics
- `--p`: Print verbose output during games (use with `--r`)
- `--m`: Manual feedback mode where the AI suggests words and you provide feedback

### Game Modes Explained

#### 1. Manual Mode (Default)
```bash
python game.py
```
You enter guesses and the game provides feedback. Good for playing Wordle yourself.

#### 2. Manual Feedback Mode
```bash
python game.py --m
```
The AI suggests guesses and you provide feedback based on the actual Wordle game:
- Use letters for correct positions (green)
- Use `-` for wrong positions (yellow) 
- Use `+` for letters not in the word (gray)
- Enter the word itself if the guess was correct

Example feedback: `a++-+` means 'a' is correct in position 1, letters 2&3 are in wrong positions, and letters 4&5 aren't in the word.

#### 3. Automated Mode
```bash
python game.py --r 1000 --p
```
Runs the solver automatically against randomly selected words to evaluate performance.

## File Structure

```
wordle_solver/
├── game.py              # Main game controller and CLI
├── guesser.py           # AI solver implementation
├── wordle.py            # Wordle game logic
├── allowed_words.yaml   # Word list (2,315 words)
└── README.md           # This file
```

### Key Components

- **`Game`**: Manages game flow and statistics collection
- **`Guesser`**: The AI solver with frequency analysis and entropy calculations
- **`Wordle`**: Implements standard Wordle rules and feedback generation

## Algorithm Details

### Word Scoring
Words are scored based on:
- Absolute letter frequency in remaining candidates
- Positional letter frequency 
- Unique letter bonus
- Penalty for previously tried words

### Entropy Calculation
For each candidate guess, the solver:
1. Simulates all possible feedback patterns
2. Calculates information gained from each pattern
3. Selects the guess with maximum expected information gain

### Smart Disambiguation
When few candidates remain, the solver:
- Identifies positions where candidates differ
- Makes strategic "dummy" guesses to eliminate multiple possibilities
- Optimally distinguishes between similar words

## Example Output

```bash
$ python game.py --r 100 --p

arose
++a++
later
++te-
chime
chime

Proportion of words guessed correctly: 94.00%
Average number of guesses: 4.1500
Total execution time: 12.34 seconds
```

## Dependencies

- Python 3.6+
- PyYAML (`pip install pyyaml`)
- Rich (`pip install rich`) - for console formatting

## Contributing

Contributions are welcome! Areas for improvement:
- Alternative starting word strategies
- Enhanced disambiguation algorithms
- Performance optimizations
- Additional game modes
- More User-friendly interface
