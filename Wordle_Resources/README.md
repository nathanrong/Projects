## Wordle - Python Project

**Description**

Python code for a quick game of wordle. 

**Required Libraries** 
- pygame-ce
- random (standard library)

To install the third party python library, run: 
    pip install pygame-ce

**Resource Files**

The game uses the following resource files. Ensure they are in the same directory as your script:
- backspace.png (backspace button)
- WordleAcceptableAnswers.py (list of all possible 5-word guesses)
- WordleAnswers.py (list of all potential solutions)
- Helvetica.ttf (typographic font type file)
- Helvetica-Bold.ttf (typographic font type file)

**Gameplay**

Objective: Correctly guess a five letter word using six-attempts. 

  The puzzle uses color as feedback on letter positioning, changing the color of the tiles: 
  - Green indicates a letter is in the correct position
  - Yellow signals the letter is in the word but not in its proper place
  - Gray means the letter is not in the word

Controls: 
- type using your keyboard, or click the printed keyboard, a five letter guess
- press enter to submit your guess
Tips: The quicker you guess, the quicker you guessed!
