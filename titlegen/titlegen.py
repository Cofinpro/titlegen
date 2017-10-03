import os
import random
import logging
import psycopg2
import csv
import io

from flask import Flask, Response, g, render_template, stream_with_context
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.widgets import TextArea
from datetime import datetime
from psycopg2.pool import ThreadedConnectionPool
from urllib.parse import urlparse
from contextlib import contextmanager

# Bootstrap and configure the application
app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    SECRET_KEY=os.urandom(24),
))
app.config.from_envvar('TITLEGEN_SETTINGS', silent=True)

# Postgres connection pool
db_config = []
# Read config from Amazon RDS Config
if 'RDS_HOSTNAME' in os.environ:
    db_config = {
            'database': os.environ['RDS_DB_NAME'],
            'user': os.environ['RDS_USERNAME'],
            'password': os.environ['RDS_PASSWORD'],
            'host': os.environ['RDS_HOSTNAME'],
            'port': os.environ['RDS_PORT'],
    }
else:
    url = urlparse(os.environ.get('DATABASE_URL'))
    db_config = {
            'database': url.path[1:],
            'user': url.username,
            'password': url.password,
            'host': url.hostname,
            'port': url.port,
    }

pool = ThreadedConnectionPool(1, 5, **db_config)

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
        with get_db_cursor() as cursor:
            cursor.execute('select * from votes')
            results = cursor.fetchmany();
            while results:
                for row in results:
                    yield ';'.join(str(item) for item in row) + '\n';
                results = cursor.fetchmany()

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

    with get_db_cursor(True) as cursor:
        cursor.execute('insert into votes (title, is_cool, insert_timestamp) values (%s,%s,%s)',
            (title, cool, datetime.now()))

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

@contextmanager
def get_db():
    try:
        connection = pool.getconn()
        yield connection
    finally:
        pool.putconn(connection)

@contextmanager
def get_db_cursor(commit=False):
    with get_db() as connection:
        cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            cursor.close()

@app.cli.command('initdb')
@app.before_first_request
def init_db():
    log.info('Initializing database');
    with app.open_resource('schema.sql', mode='r') as f:
        with get_db_cursor(True) as cursor:
            cursor.execute(f.read())

