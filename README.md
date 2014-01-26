internetpoints
==============

Introduction
------------

internetpoints is a web application & cron job that can be used to give "internet points" to users according to their contributions on a mailing-list. This is inspired by the reputation system of [Stack Overflow](http://stackoverflow.com/).

The idea here is to motivate people to solve problem by making them compete for rewards, that are worth different amount of points.

How it works
------------

The software has several parts:
* a getter that downloads emails, organize them in threads and puts them in a database;
* a "voting" interface that allows trusted users to choose, for each thread, which poster gets what kind of award;
* a score summary that displays the score of each mailing-list member (and other statistics).

It is written in [Python 2.7](http://python.org/) and uses [Flask](http://flask.pocoo.org/) (web framework), [SQLAlchemy](http://www.sqlalchemy.org/) (database toolkit) and the standard [email](http://docs.python.org/library/email) and [poplib](http://docs.python.org/library/poplib) modules to get messages from a POP3 server.

Installation
------------

Clone this repository and copy the file `config.py.example` to `config.py`, then edit it as needed. Use cron to run the `internetpoints.getter` module periodically, e.g.:

    python -m internetpoints.getter

Then configure your web server to serve the WSGI application `internetpoints.wsgi:application`. For testing/development purposes, you can use [Twisted](http://twistedmatrix.com/)'s twistd tool to run it from a terminal:

    twistd web --wsgi internetpoints.wsgi.application
