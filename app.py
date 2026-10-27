from flask import Flask, render_template, request, redirect, url_for
import logic
import database

app = Flask(__name__)

@app.route('/')
def index():
    stats = logic.get_dashboard_stats()
    tasks = database.get_all_tasks()
    return render_template('index.html', stats=stats, tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')
    if title:
        logic.add_smart_task(title)
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    database.delete_task(task_id)
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    current_status = request.form.get('status')
    new_status = "done" if current_status == "new" else "new"
    logic.change_task_status(task_id, new_status)
    return redirect(url_for('index'))

if __name__ == '__main__':
    database.setup_database()
    app.run(debug=True)
