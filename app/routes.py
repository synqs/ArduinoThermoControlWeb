from app import app
from app.forms import LoginForm, FileForm
from flask import render_template, flash, redirect

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = LoginForm()

    fileform = FileForm()
    if fileform.validate_on_submit():
        print('Test test test')
        f = fileform.file.data
        print(f)
        df = data(f)
        flash('We got the following filename {}'.format(fileform.file.data.filename))
        return redirect('/index')

    lyseout = 'This is some dummy output from lyse.'
    return render_template('index.html', lyseout=lyseout, form=form, fileform=fileform)
