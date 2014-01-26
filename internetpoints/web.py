from flask import Flask, redirect, render_template

from . import models
from .storage import Session


# Setup Flask
app = Flask('internetpoints')


@app.route('/')
def index():
    """Landing page.

    Redirects to scores.
    """
    return redirect('/scores', 301)


@app.route('/scores')
def scores():
    """Scores.

    Display a list of contributors with their current number of points.
    """
    session = Session()
    posters = (session.query(models.Poster)
                      .order_by(models.Poster.score.desc())).all()
    return render_template('scores.html', posters=posters)

@app.route('/vote')
def vote():
    """Main view.

    Shows the list of threads that require resolution.
    """
    session = Session()
    threads = (session.query(models.Thread)
                      .order_by(models.Thread.last_msg.desc())
                      .limit(50)).all()
    return render_template('vote.html', threads=threads)
