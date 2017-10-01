from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.widgets import TextArea
import os
import random

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('TITLEGEN_SETTINGS', silent=True)
app.secret_key = os.urandom(24);

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
        persist_vote()

    form.title.data = generate_title()
    return render_template('title.html', form=form)

def persist_vote():
    return

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
