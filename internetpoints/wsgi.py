import logging


logging.basicConfig(level=logging.INFO)


from internetpoints.web import app


application = app
