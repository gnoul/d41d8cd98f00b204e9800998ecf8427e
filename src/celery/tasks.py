import os
import json
from os import environ as env
# import logging
import requests
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from celery import Celery

# env = os.environ
CELERY_BROKER_URL = env.get('CELERY_BROKER_URL', 'amqp://admin:mypass@rabbit:5672//'),
CELERY_RESULT_BACKEND = env.get('CELERY_RESULT_BACKEND', 'redis://redis:6379')
# Highcharts
HIGHCHART_HOST = env.get('HIGHCHART_HOST', 'charts')
HIGHCHART_PORT = env.get('HIGHCHART_PORT', 8080)
# Postgres
POSTGRES_USER = env.get('POSTGRES_USER', 'pguser1')
POSTGRES_DB = env.get('POSTGRES_DB', 'pddb1')
POSTGRES_PASSWORD = env.get('POSTGRES_PASSWORD', 'ohd7ua2Quu')
POSTGRES_HOST = env.get('POSTGRES_HOST', 'db')
POSTGRES_PORT = env.get('POSTGRES_PORT', 5432)

celery = Celery('tasks',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)


engine = create_engine(
    f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')


def process_query(params):
    try:
        with engine.connect() as con:
            # Умножаем время на 1000 для удобства использования в графиках
            q1 = (r'''SELECT t * 1000 as x, {formula} as y FROM (
                          SELECT extract(epoch from a) as t 
                            FROM generate_series(now() - interval '{period}', now(), '{step}') 
                            as a) as xx;''').format(**params)
            result = con.execute(q1).fetchall()
            result = [tuple(i) for i in result]
        return result
    except SQLAlchemyError:
        pass
    return None


@celery.task(name='service2.dbquery')
def query(params):
    """Generating points in the database"""
    if not params:
        pass
    points = process_query(params)
    params['result'] = points
    params['db_task_id'] = celery.current_task.request.id
    return params


@celery.task(name='service1.callback')
def callback(params, stage=None):
    """Send result to sender by callback_url"""
    url = params.get('callback_url')
    data = {'db_task_id': params.get('db_task_id'),
            'graph_task_id': params.get('graph_task_id'),
            'graph_id': params.get('graph_id'),
            'stage': stage}
    if url:
        requests.post(url, json=data)
    return celery.current_task.request.id, stage


@celery.task(name='service1.gengraph')
def gengraph(params):
    task_id = params.get('db_task_id')
    task = celery.AsyncResult(task_id)
    # while not task.status == 'SUCCESS':
    #     pass
    results = task.result
    points = results.get('result')
    graph_id = results.get('graph_id')
    graph_conf = {"infile": {"title": {"text": "T Chart"},
                             "xAxis": {"type": "datetime"},
                             "series": [{"data": points}]}}
    try:
        resdir = os.path.join('images', str(graph_id))
        imagename = os.path.join(resdir, '{0}.png'.format(task_id))
        if not os.path.exists(resdir):
            os.makedirs(resdir)
        url = f'http://{HIGHCHART_HOST}:{HIGHCHART_PORT}'
        r = requests.post(url,
                          data=json.dumps(graph_conf),
                          headers={'Content-Type': 'application/json'})
        if r.status_code == 200:
            with open(imagename, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
    except requests.RequestException:
        imagename = None
    params['graph_task_id'] = celery.current_task.request.id
    params['graph_id'] = graph_id
    params['result'] = imagename
    return params

