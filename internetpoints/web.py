from flask import Flask, render_template


app = Flask('internetpoints')


@app.route('/')
def index():
    """Main view.

    Shows the list of threads that require resolution.
    """
    # TODO
    return render_template('index.html')
