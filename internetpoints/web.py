from flask import Flask, redirect, render_template
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

from . import config, models


# Setup Flask
app = Flask('internetpoints')


# Setup SQLAlchemy
engine = create_engine(config.DATABASE_URI)
Session = sessionmaker(bind=engine)
if not engine.dialect.has_table(engine.connect(), 'threads'):
    models.Base.metadata.create_all(bind=engine)


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
