from flask import Flask, render_template, request, redirect
from datetime import datetime
import json
import os

app = Flask(__name__)
DATA_FILE = "data.json"

# Load tasks from file
def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

# Save tasks to file
def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

@app.route("/", methods=["GET", "POST"])
def index():
    tasks = load_tasks()

    if request.method == "POST":
        task = request.form["task"]
        due = request.form["due"]
        category = request.form["category"]
        tasks.append({
            "task": task,
            "due": due if due else None,
            "category": category,
            "completed": False
        })
        save_tasks(tasks)
        return redirect("/")

    # Handle filtering
    filter_option = request.args.get("filter", "all")
    if filter_option == "completed":
        filtered = [t for t in tasks if t.get("completed", False)]
    elif filter_option == "pending":
        filtered = [t for t in tasks if not t.get("completed", False)]
    else:
        filtered = tasks

    # Stats
    total = len(tasks)
    completed = len([t for t in tasks if t.get("completed", False)])
    pending = total - completed

    return render_template("index.html",
                           tasks=filtered,
                           total=total,
                           completed=completed,
                           pending=pending,
                           selected=filter_option,
                           current_date=datetime.now().strftime("%A, %d %B %Y"))

@app.route("/complete/<int:index>")
def complete(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        tasks[index]["completed"] = not tasks[index].get("completed", False)
        save_tasks(tasks)
    return redirect("/")

@app.route("/delete/<int:index>")
def delete(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        tasks.pop(index)
        save_tasks(tasks)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
