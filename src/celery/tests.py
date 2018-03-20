import os
import unittest

from tasks import *


class TestMyCeleryWorker(unittest.TestCase):

    def setUp(self):
        celery.conf.update(CELERY_ALWAYS_EAGER=True)

    def test_query_normal(self):
        formula = 'sin(t^2)'
        period = '1d'
        step = '2h'
        q_res = query.delay({'formula': formula, 'period': period, 'step': step}
                            ).get()
        self.assertEqual(len(q_res['result']), 13)

        # Период больше шага в результате одна точка
        period = '1h'

        q_res = query.delay({'formula': formula, 'period': period, 'step': step}
                            ).get()
        self.assertEqual(len(q_res['result']), 1)

        # 13 единиц в у координатах
        period = '1d'
        formula = '1'
        q_res = query.delay({'formula': formula, 'period': period, 'step': step}
                            ).get()
        y_coords = [i[1] for i in q_res['result']]
        self.assertListEqual(y_coords, [1] * 13)

    def test_query_error(self):
        # Ошибка в формуле

        period = '1d'
        formula = 'sin(q)'
        step = '2h'
        q_res = query.delay({'formula': formula, 'period': period, 'step': step}
                            ).get()
        self.assertEqual(q_res['result'], None)

        formula = 'sin(t^2)'
        period = 'ww333'
        q_res = query.delay({'formula': formula, 'period': period, 'step': step}
                            ).get()
        self.assertEqual(q_res['result'], None)

    def test_gengraph(self):
        formula = 'sin(t^2)'
        period = '1d'
        step = '2h'
        q_res = query.delay({'formula': formula, 'period': period,
                             'step': step, 'graph_id': 42}
                            ).get()
        params = {'db_task_id': q_res['db_task_id'], 'graph_task_id': None, 'stage': 'db'}
        g_res = gengraph.delay(params).get()
        impaths = g_res['result'].split('/')
        # Проверяем что создается файл с корректным именем.
        self.assertEqual(impaths[1], str(q_res['graph_id']))
        self.assertEqual(impaths[2], '{}.png'.format(q_res['db_task_id']))
        self.assertTrue(os.path.exists(g_res['result']))
