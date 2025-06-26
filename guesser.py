from random import choice
import yaml
from rich.console import Console
from collections import Counter, defaultdict
import itertools
import math

class Guesser:
    def __init__(self, manual):
        yaml.SafeLoader.add_constructor('tag:yaml.org,2002:bool', lambda loader, node: loader.construct_scalar(node))
        self.word_list = yaml.load(open('allowed_words.yaml'), Loader=yaml.SafeLoader)
        self.manual = manual
        self.console = Console()
        self.tried = []
        self.current_candidates = self.word_list.copy()

        self.update_freq()
        # self.optimal_first_guess = self.compute_optimal_first_sequence()

    def update_freq(self):
        """Update letter absolute and positional frequencies based on current candidates"""
        self.letter_freqs = Counter("".join(self.current_candidates))
        self.positional_freqs = [Counter(word[i] for word in self.current_candidates) for i in range(5)]

    def compute_word_score(self, word):
        """Calculate frequency-based score for a word"""
        score = 0
        seen = set()
        for i, letter in enumerate(word):
            if letter not in seen:
                score += self.letter_freqs[letter]
                seen.add(letter)
            score += self.positional_freqs[i][letter]
        score *= len(seen) / 5.0
        return score if word not in self.tried else -float('inf')

    def get_pattern(self, guess, word):
        """Get the pattern that would result from a guess against a target word"""
        result = ['+']*5
        counts = Counter(word)
        
        # Check for green matches
        for i, (g, w) in enumerate(zip(guess, word)):
            if g == w:
                result[i] = g
                counts[g] -= 1
        
        # Check for yellow matches
        for i, (g, r) in enumerate(zip(guess, result)):
            if r == '+' and g in counts and counts[g] > 0:
                result[i] = '-'
                counts[g] -= 1
                
        return ''.join(result)

    def compute_entropy(self, guess, candidates):
        """Compute the entropy for a guess"""
        if not candidates:
            return 0
        
        pattern_counts = defaultdict(int)
        total = len(candidates)
        
        for word in candidates:
            pattern = self.get_pattern(guess, word)
            pattern_counts[pattern] += 1
        
        entropy = 0
        for count in pattern_counts.values():
            prob = count / total
            entropy -= prob * math.log2(prob)
            
        return entropy

    def compute_optimal_first_sequence(self):
        """Compute optimal first guess using hybrid approach with letter permutations"""
        # Get the top 10 most frequent letters overall
        top_letters = sorted(self.letter_freqs.items(), key=lambda x: x[1], reverse=True)[:10]
        top_letters = [letter for letter, _ in top_letters]
        
        # For each position, get the top 5 most frequent letters
        for pos_freq in self.positional_freqs:
            pos_top = sorted(pos_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            top_letters.extend([letter for letter, _ in pos_top])
            
        candidate_letters = set(top_letters)
        
        # Get top 10 sequences by frequency score so that we don't compute entropy for each permutation
        sequences_scores = []
        for sequence in itertools.permutations(candidate_letters, 5):
            score = self.compute_word_score(sequence)
            sequences_scores.append((''.join(sequence), score))
        
        top_sequences = sorted(sequences_scores, key=lambda x: x[1], reverse=True)[:10]
        
        # Find sequence with highest entropy among top frequency scorers
        best_sequence = None
        best_entropy = -float('inf')
        
        for sequence, _ in top_sequences:
            entropy = self.compute_entropy(sequence, self.word_list)
            if entropy > best_entropy:
                best_entropy = entropy
                best_sequence = sequence
                
        return best_sequence

    def word_matches(self, word, guess, result):
        """Check if a word matches the pattern from a previous guess"""
        rem = Counter(word)
        for i, (g, r) in enumerate(zip(guess, result)):
            if r == g:
                if word[i] != g:
                    return False
                rem[g] -= 1
        for i, (g, r) in enumerate(zip(guess, result)):
            if r == '-':
                if word[i] == g:
                    return False
                if rem[g] <= 0:
                    return False
                rem[g] -= 1
            elif r == '+':
                if rem[g] > 0:
                    return False
        return True

    def filter_words(self, candidate_words, guess, result):
        """Filter words based on the guess result"""
        new_candidates = [w for w in candidate_words if self.word_matches(w, guess, result)]
        return new_candidates if new_candidates else [self.word_list[0]]
    
    def restart_game(self):
        """Reset the game state"""
        self.tried = []
        self.current_candidates = self.word_list.copy()
        
    def get_guess(self, result):
        """Get the next guess using hybrid approach"""
        if self.manual == 'manual':
            return self.console.input('Your guess:\n')
        
        # Filter candidates based on previous guess
        if result and result not in ["Please enter a five-letter word", "You have already tried that word"] and self.tried:
            last_guess = self.tried[-1]
            self.current_candidates = self.filter_words(self.current_candidates, last_guess, result)

        # Special rule for disambiguating similar words 
        if self.tried and len(self.current_candidates) > 2 and len(self.tried) < 5:
            common_pattern = []
            ambiguous_indices = []
            for i in range(5):
                letters_in_pos = {word[i] for word in self.current_candidates}
                if len(letters_in_pos) == 1:
                    common_pattern.append(next(iter(letters_in_pos)))
                else:
                    common_pattern.append(None)
                    ambiguous_indices.append(i)
            # If there is one missing letter and multiple candidates, make a dummy guess with all the differing letters
            if len(ambiguous_indices) == 1:
                ambiguous_pos = ambiguous_indices[0]
                letters = []
                seen = set()
                for word in self.current_candidates:
                    letter = word[ambiguous_pos]
                    if letter not in seen:
                        letters.append(letter)
                        seen.add(letter)
                #pick a word from the wordlist which contains the largest number of letters in the ambiguous position
                dummy_guess = max(self.word_list, key=lambda x: sum(1 for letter in letters if letter in x))
                self.tried.append(dummy_guess)
                self.console.print(dummy_guess)
                return dummy_guess
            # If there are two missing letters, same strategy and get better results than picking the highest-entropy candidate
            elif len(ambiguous_indices) == 2:
                pos1, pos2 = ambiguous_indices
                #Make a dummy guess with the most common letters in the two ambiguous positions
                letters_pos1 = sorted(set(word[pos1] for word in self.current_candidates))
                letters_pos2 = sorted(set(word[pos2] for word in self.current_candidates))
                all_ambiguous_letters = letters_pos1 + letters_pos2
                letters_to_use = all_ambiguous_letters[:5]
                #find a word from the wordlist which contains the largest number of letters in the ambiguous positions
                dummy_guess = max(self.word_list, key=lambda x: sum(1 for letter in letters_to_use if letter in x))
                self.tried.append(dummy_guess)
                self.console.print(dummy_guess)
                return dummy_guess

        self.update_freq()
        
        # Get top 10 candidates by frequency score
        word_scores = []
        
        for word in self.current_candidates:
            if word not in self.tried:
                score = self.compute_word_score(word)
                word_scores.append((word, score))
        
        top_words = sorted(word_scores, key=lambda x: x[1], reverse=True)[:10]
        
        # Find word with highest entropy among top frequency scorers
        best_entropy = -float('inf')
        guess = top_words[0][0]
        
        for word, _ in top_words:
            entropy = self.compute_entropy(word, self.current_candidates)
            if entropy > best_entropy:
                best_entropy = entropy
                guess = word
        
        self.tried.append(guess)
        self.console.print(guess)
            
        return guess