from flask import Flask, redirect, render_template

import storage


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
    # TODO
    return render_template('index.html')

@app.route('/vote')
def vote():
    """Main view.

    Shows the list of threads that require resolution.
    """
    # TODO
    return render_template('index.html')
