import os
import random
import logging
import sqlite3
import csv
import io

from flask import Flask, Response, g, render_template, stream_with_context
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.widgets import TextArea
from datetime import datetime

# Bootstrap and configure the application
app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'titlegen.db'),
    SECRET_KEY=os.urandom(24),
    USERNAME='admin',
    PASSWORD='default',
))
app.config.from_envvar('TITLEGEN_SETTINGS', silent=True)

# Configure logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

tech = [
        'Solutions',
        'Software',
        'BPM',
        'Frontend',
        'Integration',
        'Application',
        'Frontend',
        'UX/UI',
        'Test',
        'Enterprise',
        'JavaEE',
        'EE4J',
        '.NET',
        'Full-Stack',
        ]

titles = [
        'Architect',
        'Expert',
        'Engineer',
        'Developer',
        'Designer',
        ]

spice = [
        'Expert',
        'Lead',
        'Senior',
        'Distinguished',
        ]

@app.route('/', methods=['get', 'post'])
def show_form():
    form = TitleForm()
    if (form.validate_on_submit()):
        persist_vote(form)

    form.title.data = generate_title()
    return render_template('title.html', form=form)

@app.route('/results')
def download_results():
    def generate_csv():
        cursor = get_db().cursor()
        for row in cursor.execute('select * from votes'):
            yield ';'.join(str(item) for item in row) + '\n';

    return Response(
            stream_with_context(generate_csv()),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=results.csv'})

def persist_vote(form):
    title = form['title'].data
    cool = None
    log.debug("Got vote for '%s'", title)
    if (form['is_cool'].data):
        log.info("%s is cool", title)
        cool = True
    elif (form['not_cool'].data):
        log.info("%s sucks", title)
        cool = False
    else:
        return;

    db = get_db()
    db.execute('insert into votes (title, is_cool, insert_timestamp) values (?,?,?)',
        [title, cool, datetime.now()])
    db.commit()

def generate_title():
    technology = random.choice(tech)
    title = random.choice(titles)
    
    job_title = "{}-{}".format(technology, title)

    if random.random() < 0.5:
        # we are not done yet - let's spice things up!
        job_title = "{} {}".format(random.choice(spice), job_title)

    return job_title

class TitleForm(FlaskForm):
    title = TextAreaField('title', widget=TextArea())
    is_cool = SubmitField(label='Klar')
    not_cool = SubmitField(label='Niemals!')

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.cli.command('initdb')
@app.before_first_request
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    log.info('Initializing database');
    db.commit()

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

