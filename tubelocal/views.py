from tubelocal import app, render_template


@app.route('/')
def index():
    return render_template('home.html.j2')
