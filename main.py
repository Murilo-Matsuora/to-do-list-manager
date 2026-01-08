from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-string'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
bootstrap = Bootstrap5(app)
db.init_app(app)

class Task(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    urgency: Mapped[str] = mapped_column(String(20), nullable=False)

with app.app_context():
    db.create_all()

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description (Optional)')
    urgency = SelectField('Urgency', choices=[
        ('red', 'High'),
        ('yellow', 'Medium'),
        ('green', 'Low')
    ])
    submit = SubmitField('Save Task')

@app.route("/", methods=['GET', 'POST'])
def home():
    form = TaskForm()

    if form.validate_on_submit():
        new_task = Task(
            title=form.title.data,
            description=form.description.data,
            urgency=form.urgency.data
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('home'))
    
    red_tasks = Task.query.filter_by(urgency='red').all()
    yellow_tasks = Task.query.filter_by(urgency='yellow').all()
    green_tasks = Task.query.filter_by(urgency='green').all()
    
    return render_template("index.html", form=form, red_tasks=red_tasks, 
                           yellow_tasks=yellow_tasks, green_tasks=green_tasks)

@app.route("/delete/<id>", methods=['GET'])
def delete(id):
    try:
        task = db.session.get(Task, id)
    except AttributeError:
        return f"Sorry a cafe with id {id} was not found in the database."
    else:
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for('home'))
    
@app.route("/edit/<id>", methods=['GET', 'POST'])
def edit(id):
    form = TaskForm()
    task = db.session.get(Task, id)
    if not task:
        return f"Task with id {id} not found.", 404
    form = TaskForm(obj=task)

    if form.validate_on_submit():
        try:
            task = db.session.get(Task, id)
        except AttributeError:
            return f"Sorry a cafe with id {id} was not found in the database."
        else:
            task.title = form.title.data
            task.description = form.description.data
            task.urgency = form.urgency.data

            db.session.commit()
            return redirect(url_for('home'))
        
    return render_template("edit.html", form=form)
    

if __name__ == "__main__":
    app.run(debug=True)