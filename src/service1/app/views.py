import requests
import psycopg2
from datetime import datetime
from flask import request, render_template, send_from_directory, redirect, url_for, jsonify

from app import app, db
from app.worker import celery
from app.models import Graphs
from app.forms import GraphForm


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        graphs = Graphs.query.all()
        return render_template('index.html', graphs=graphs)
    return redirect(url_for('index'))


@app.route('/graph/<graph_id>', methods=['GET'])
def showgraph(graph_id=None):
    graph = Graphs.query.get(graph_id)
    return render_template('graph.html', graph=graph)


@app.route('/graph_form', methods=['GET', 'POST'])
def graph_form():
    form = GraphForm()
    if form.validate_on_submit():
        try:
            formula = form.data.get('formula')
            period = form.data.get('period')
            step = form.data.get('step')
            graph = Graphs(formula=formula, period=period, step=step, status='Graph created')
            db.session.add(graph)
            db.session.commit()
            params = [{'formula': formula,
                       'period': period,
                       'step': step,
                       'graph_id': graph.id,
                       'callback_url': 'http://service1:5000/task_result'
                       }]
            requests.post('http://service2:5000', json=params)
            return redirect(url_for('graph', graph_id=graph.id))
        except psycopg2.Error as e:
            app.logger.warning('Service1 graph form db error.{}'.format(e))
        except requests.RequestException as e:
            app.logger.warning('Service1 graph form request error.{}'.format(e))
        return redirect(url_for('graph', graph_id=0))
    return render_template('graph_form.html',
                           title='Add graph',
                           form=form)


@app.route('/batchtask', methods=['POST'])
def batchtask():
    data = request.json
    params = []
    for graph_id in map(int, data):
        graph = Graphs.query.get(graph_id)
        graph.status = 'Start updating'
        graph.image = None
        db.session.add(graph)
        db.session.commit()  # !!!!
        params.append({'formula': graph.formula,
                       'period': graph.period,
                       'step': graph.step,
                       'graph_id': graph.id,
                       'callback_url': 'http://service1:5000/task_result'
                       })
    requests.post('http://service2:5000', json=params)
    return jsonify(data)


@app.route('/task_result', methods=['POST'])
def get_result():
    status = ''
    params = request.json
    stage = params.get('stage')
    if stage == 'db':
        task_id = params.get('db_task_id')
        taskres = celery.AsyncResult(task_id)
        if taskres.status == 'SUCCESS':
            if 'result' in taskres.result and taskres.result['result']:
                params['callback_url'] = 'http://service1:5000/task_result'
                callback = celery.signature('service1.callback', kwargs={'stage': 'graph'})
                celery.send_task('service1.gengraph', args=[params], link=callback)
                status = 'Generated {} points'.format(len(taskres.result['result']))
            else:
                status = 'Generated 0 points. Check formula, period or step'
        else:
            status = 'Error in points generation. Check formula, period or step'
        graph_id = params.get('graph_id')
        graph = Graphs.query.get(graph_id)
        if graph:
            graph.status = status
            db.session.add(graph)
            db.session.commit()
    elif stage == 'graph':
        task_id = params.get('graph_task_id')
        graph_id = params.get('graph_id')
        # graph_id = taskres.result.get('graph_id')
        taskres = celery.AsyncResult(task_id)
        graph = Graphs.query.get(graph_id)
        if taskres.status == 'SUCCESS':
            if 'result' in taskres.result:
                impath = taskres.result.get('result')
                if graph:
                    graph.image = impath
                    graph.updated = datetime.now()
                    graph.status = 'Ok'
            else:
                graph.status = 'Image generation success, but file not found'
        else:
            graph.status = 'Image generation unsuccessful'
        db.session.add(graph)
        db.session.commit()
        print()
    if status:
        app.logger.info('Task result status: {}'.format(status))
    return jsonify(True)


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


@app.route('/images/<path:path>')
def send_image(path):
    return send_from_directory('images', path)
