from boggle import Boggle
from flask import Flask, request, render_template, redirect, session, jsonify



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
