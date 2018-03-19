from flask import request, jsonify

from worker import celery
from app import app


@app.route('/', methods=['POST'])
def index():
    data = request.json
    if data:
        task_ids = []
        callback = celery.signature('service1.callback', kwargs={'stage': 'db'})
        for graph in data:
            task = celery.send_task('service2.dbquery', args=[graph], link=callback)
            task_ids.append(task.id)
        return jsonify(task_ids)
