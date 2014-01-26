from flask import Flask, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

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


@app.route('/thread/<int:thread_id>')
def thread(thread_id):
    """Shows a thread and allows to vote on it.
    """
    session = Session()
    thread = (session.query(models.Thread)
                     .filter(models.Thread.id == thread_id)).one()
    tasks = (session.query(models.Task)).all()
    return render_template('thread.html', thread=thread, tasks=tasks)


@app.route('/assign_task/<int:thread_id>', methods=['POST'])
def assign_task(thread_id):
    """Assign a new task to a thread.
    """
    session = Session()
    thread = (session.query(models.Thread)
                     .filter(models.Thread.id == thread_id)).one()
    task = (session.query(models.Task)
                     .filter(models.Task.id == request.form['task'])).one()

    try:
        task_assignation = models.TaskAssignation(
                thread=thread,
                task=task)
        session.add(task_assignation)
        session.commit()
    except IntegrityError:
        pass
    return redirect(url_for('thread', thread_id=thread_id))
