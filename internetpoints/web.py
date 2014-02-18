from flask import Flask, redirect, render_template, request, Response, url_for
import functools
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from internetpoints import config, models
from internetpoints.storage import Session


# Setup Flask
app = Flask('internetpoints')


def check_auth():
    auth = request.authorization
    return auth is not None and auth.password == config.PASSWORD


def authenticate():
    return Response("Please login to vote",
                    401,
                    {'WWW-Authenticate': 'Basic realm="internetpoints"'})


def requires_auth(func):
    @functools.wraps(func)
    def decorated(*args, **kwargs):
        if not check_auth():
            return authenticate()
        else:
            return func(*args, **kwargs)
    return decorated


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
@requires_auth
def vote():
    """Main view.

    Shows the list of threads that require resolution.
    """
    session = Session()
    threads = (session.query(models.Thread)
                      .options(
                          joinedload(models.Thread.task_assignations)
                              .joinedload(models.TaskAssignation.task),
                          joinedload(models.Thread.messages))
                      .order_by(models.Thread.last_msg.desc())
                      .limit(50)).all()
    return render_template('vote.html', threads=threads)


@app.route('/thread/<int:thread_id>')
@requires_auth
def thread(thread_id):
    """Shows a thread and allows to vote on it.
    """
    session = Session()
    thread = (session.query(models.Thread)
                     .options(
                         joinedload(models.Thread.messages)
                             .joinedload(models.Message.poster_email)
                             .joinedload(models.PosterEmail.poster),
                         joinedload(models.Thread.task_assignations))
                     .filter(models.Thread.id == thread_id)).one()
    tasks = (session.query(models.Task)).all()
    posters = set(msg.poster_email.poster
                  for msg in thread.messages
                  if msg.poster_email is not None)
    return render_template('thread.html',
                           thread=thread, tasks=tasks, posters=posters)


@app.route('/assign_task/<int:thread_id>', methods=['POST'])
@requires_auth
def assign_task(thread_id):
    """Assign a new task to a thread.
    """
    session = Session()
    thread = (session.query(models.Thread)
                     .filter(models.Thread.id == thread_id)).one()
    task = (session.query(models.Task)
                     .filter(models.Task.id == request.form['task'])).one()
    poster_req = (session.query(models.Poster)
                         .filter(models.Poster.id == request.form['poster']))
    poster = poster_req.one()
    # Note that, although the Poster definitely exists, here we don't check
    # that he took part in the thread

    try:
        # Assign task
        task_assignation = models.TaskAssignation(
                thread=thread,
                task=task,
                poster=poster)
        session.add(task_assignation)
        # Update Poster's score
        poster_req.update({
                models.Poster.score: models.Poster.score + task.reward})
        session.commit()
    except IntegrityError:
        pass
    return redirect(url_for('thread', thread_id=thread_id))
