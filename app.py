from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

###  CONFIG  ####
#################
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)

###  MODELS  ####
#################


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Task %r>" % self.id

###  ROUTES/CONTROLLERS  ####
#############################

# Root GET + POST


@app.route("/", methods=["POST", "GET"])
def index():
    # If post method comes through, assignt the request body portion with ID 'content' to local variable task_content
    if request.method == "POST":
        task_content = request.form["content"]
        # Instantiate a new object of type Todo (modeled above).
        # Set the new_task object of Todo type's field 'content' to incoming request content
        new_task = Todo(content=task_content)
        # Now push the new object/content to db in try/except block
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
            # redirect to root route upon db commit
        except:
            return "There was an issue adding your task to database"
    else:
        # create local variable to hold query of database for all entries ordered by date created
        tasks = Todo.query.order_by(Todo.date_created).all()
        # return/pass that db query.all to the template
        return render_template("index.html", tasks=tasks)

# Delete route POST
# Pass in unique pk id from todo table


@app.route("/delete/<int:id>")
# define a delete function for this route. pass in the todo-id coming off the route url
def delete(id):
    # create local variable to hold actual db entry of task to be deleted
    # after querying db (Todo table like all here) for it. If not found: 404
    task_to_delete = Todo.query.get_or_404(id)
    # try/except block to handle deletion & re-render / redirect to root
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect("/")
    except:
        return "Error: Todo either not found or already deleted"


# Update Route POST (Probably, technically should be PUT)
# Again pass in unique ID of todo to be updated

@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    # create local variable to hold Todo table task object we're updating
    task_to_update = Todo.query.get_or_404(id)
    if request.method == "POST":
        # IF a request comes in on the POST part of this route (If user clicks Update from Update Form)
        # Then take the content submitted on that update form (input text) and
        # set it equal to the Content field of the Todo-table object
        # we queried for and set above (task_to_update).
        task_to_update.content = request.form["content"]

        try:
            # No need to add since we're setting/assigning the content field of the Todo object/entry directly
            # Just commit new object to db. This does a liiiitle magic because we don't have to specify
            # the object being commited.. It must just keep track on its own
            db.session.commit()
            return redirect("/")
        except:
            return "Error Updating database todo task"
    else:
        return render_template("update.html", task=task_to_update)


if __name__ == "__main__":
    app.run(debug=True)
