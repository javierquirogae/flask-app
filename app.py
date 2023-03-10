from boggle import Boggle
from flask import Flask, request, render_template, redirect, session, jsonify

from random import choice
from math import factorial as f
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.debug = False



boggle_game = Boggle()


@app.route("/")
def root():
    """root."""
    session["game"] = boggle_game.make_board()
    return redirect("/game")

@app.route("/game")
def show_game():
    """Game."""
    board = session["game"]
    highscore = session.get("highscore", 0)
    nplays = session.get("nplays", 0)
    return render_template("game.html",board=board,highscore=highscore,nplays=nplays)

@app.route("/guess")
def check_word():
    """Check if guess is in valid."""

    word = request.args["word"]
    board = session["game"]
    response = boggle_game.check_valid_word(board, word.strip())

    return jsonify({'result': response})

@app.route("/post-score", methods=["POST"])
def post_score():
    """Receive score, update nplays, update high score if appropriate."""

    score = request.json["score"]
    highscore = session.get("highscore", 0)
    nplays = session.get("nplays", 0)

    session['nplays'] = nplays + 1
    session['highscore'] = max(score, highscore)

    return jsonify(brokeRecord=score > highscore)

class Boggle():

    def __init__(self):

        self.words = self.read_dict("words.txt")

    def read_dict(self, dict_path):
        """Read and return all words in dictionary."""

        dict_file = open(dict_path)
        words = [w.strip() for w in dict_file]
        dict_file.close()
        return words

    def make_board(self):
        """Make and return a random boggle board."""
        boggle_letters = string.ascii_uppercase + 'AEIOUY'*2 + 'ETAIONSHR'*4
       
        board = []

        for y in range(5):
            row = [choice(boggle_letters) for i in range(5)]
            board.append(row)

        return board


    def is_not_valid(self, word):
        if word.lower()[-1] == 's' and len(word) > 3:
            singular_word = word.lower()[:-1]
            if singular_word in self.words:
                return False
        elif word.lower() in self.words:
            return False
        return True
    

    def check_valid_word(self, board, word):
        """Check if a word is a valid word in the dictionary and/or the boggle board"""
    
        if self.is_not_valid(word) or len(word) < 2:
                result = "not-a-valid-word"
        # We only check the board if we have a valid Boggle word !!
        else:
            if not self.find(board, word.upper()):
                result = "not-found-on-board"
            else:
                result = "ok"

        return result

    def find_from(self, board, word, y, x, seen):
        """Can we find a word on board, starting at x, y?"""

        if x > 4 or y > 4:
            return

        # This is called recursively to find smaller and smaller words
        # until all tries are exhausted or until success.

        # Base case: this isn't the letter we're looking for.

        if board[y][x] != word[0]:
            return False

        # Base case: we've used this letter before in this current path

        if (y, x) in seen:
            return False

        # Base case: we are down to the last letter --- so we win!

        if len(word) == 1:
            return True

        # Otherwise, this letter is good, so note that we've seen it,
        # and try of all of its neighbors for the first letter of the
        # rest of the word
        # This next line is a bit tricky: we want to note that we've seen the
        # letter at this location. However, we only want the child calls of this
        # to get that, and if we used `seen.add(...)` to add it to our set,
        # *all* calls would get that, since the set is passed around. That would
        # mean that once we try a letter in one call, it could never be tried again,
        # even in a totally different path. Therefore, we want to create a *new*
        # seen set that is equal to this set plus the new letter. Being a new
        # object, rather than a mutated shared object, calls that don't descend
        # from us won't have this `y,x` point in their seen.
        #
        # To do this, we use the | (set-union) operator, read this line as
        # "rebind seen to the union of the current seen and the set of point(y,x))."
        #
        # (this could be written with an augmented operator as "seen |= {(y, x)}",
        # in the same way "x = x + 2" can be written as "x += 2", but that would seem
        # harder to understand).

        seen = seen | {(y, x)}

        # adding diagonals

        if y > 0:
            if self.find_from(board, word[1:], y - 1, x, seen):
                return True

        if y < 4:
            if self.find_from(board, word[1:], y + 1, x, seen):
                return True

        if x > 0:
            if self.find_from(board, word[1:], y, x - 1, seen):
                return True

        if x < 4:
            if self.find_from(board, word[1:], y, x + 1, seen):
                return True

        # diagonals
        if y > 0 and x > 0:
            if self.find_from(board, word[1:], y - 1, x - 1, seen):
                return True

        if y < 4 and x < 4:
            if self.find_from(board, word[1:], y + 1, x + 1, seen):
                return True

        if x > 0 and y < 4:
            if self.find_from(board, word[1:], y + 1, x - 1, seen):
                return True

        if x < 4 and y > 0:
            if self.find_from(board, word[1:], y - 1, x + 1, seen):
                return True
        # Couldn't find the next letter, so this path is dead

        return False

    def find(self, board, word):
        """Can word be found in board?"""

        # Find starting letter --- try every spot on board and,
        # win fast, should we find the word at that place.

        for y in range(0, 5):
            for x in range(0, 5):
                if self.find_from(board, word, y, x, seen=set()):
                    return True

        # We've tried every path from every starting square w/o luck.
        # Sad panda.

        return False
