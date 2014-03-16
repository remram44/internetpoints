from flask import Flask, redirect, render_template, request, Response, url_for
import functools
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

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
    # The email addresses participating in this thread but not yet associated
    # to a Poster
    registerable_senders = [msg.from_
                            for msg in thread.messages
                            if not msg.poster_email]
    return render_template('thread.html',
                           thread=thread, tasks=tasks, posters=posters,
                           registerable_senders=registerable_senders)


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


@app.route('/add_email', methods=['POST'])
@requires_auth
def add_email():
    """Create a new Poster or add an address to an existing Poster.
    """
    session = Session()
    email = request.form['email']
    # Look up a Poster with that email
    poster_email = (session.query(models.PosterEmail)
                           .options(
                               joinedload(models.PosterEmail.poster))
                           .filter(models.PosterEmail.address == email))
    try:
        poster_email = poster_email.one()
    except NoResultFound:
        pass
    else:
        return redirect(url_for(
                'edit_poster', poster=poster_email.poster.id,
                error="This email is already associated to a poster"))

    # If we got poster the info to create a new poster
    if 'name' in request.form and 'poster_id' not in request.form:
        new_poster = models.Poster(name=request.form['name'])
        session.add(new_poster)
        new_email = models.PosterEmail(address=email, poster=new_poster)
        session.add(new_email)
        session.commit()
        return redirect(url_for('edit_poster', poster_id=new_poster.id,
                                msg='Poster created'))
    elif 'name' not in request.form and 'poster_id' in request.form:
        poster_id = int(request.form['poster_id'])
        poster = (session.query(models.Poster)
                         .filter(models.Poster.id == poster_id)).one()
        new_email = models.PosterEmail(address=email, poster=poster)
        session.add(new_email)
        session.commit()
        return redirect(url_for('edit_poster', poster_id=poster.id))
    # If both are set, something is going on, just display the forms again

    # Renders the form that will allow to choose an existing Poster or to
    # create a new one
    # In both cases, redirect here
    all_posters = session.query(models.Poster).all()
    return render_template('add_email.html', email=email,
                           posters=all_posters)


@app.route('/edit_poster/<int:poster_id>')
@requires_auth
def edit_poster(poster_id):
    return Response("TODO", content_type='text/plain')
