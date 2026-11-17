"""Testes locais dos cinco serviços de integração com Inven!RA."""
import unittest
from fastapi.testclient import TestClient
from app import app


class TestarEcoRota(unittest.TestCase):
    def setUp(self):
        self.cliente = TestClient(app)

    def test_pagina_configuracao(self):
        resposta = self.cliente.get('/config')
        self.assertEqual(resposta.status_code, 200)
        for campo in ('tema', 'instrucoes', 'categorias', 'minimo_observacoes'):
            self.assertIn(f'name="{campo}"', resposta.text)

    def test_parametros(self):
        dados = self.cliente.get('/params').json()
        self.assertEqual([p['name'] for p in dados],
                         ['tema', 'instrucoes', 'categorias', 'minimo_observacoes'])

    def test_deploy_post(self):
        resposta = self.cliente.post('/deploy', json={'activityID': 'instancia-001'})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.headers['content-type'].split(';')[0], 'text/plain')
        self.assertTrue(resposta.text.endswith('/atividade/instancia-001'))

    def test_deploy_get(self):
        resposta = self.cliente.get('/deploy?activityID=instancia-001')
        self.assertEqual(resposta.status_code, 200)

    def test_deploy_invalido(self):
        self.assertEqual(self.cliente.post('/deploy', json={}).status_code, 400)

    def test_lista_analiticas(self):
        dados = self.cliente.get('/analytics-list').json()
        self.assertEqual(len(dados['quantAnalytics']), 3)
        self.assertEqual(len(dados['qualAnalytics']), 1)

    def test_analiticas_post(self):
        resposta = self.cliente.post('/analytics', json={'activityID': 'instancia-001'})
        self.assertEqual(resposta.status_code, 200)
        dados = resposta.json()
        self.assertEqual(dados[0]['inveniraStdID'], '1001')
        self.assertEqual(dados[0]['quantAnalytics'][0]['value'], 4)

    def test_analiticas_sem_id(self):
        self.assertEqual(self.cliente.post('/analytics', json={}).status_code, 400)

    def test_registo(self):
        dados = self.cliente.get('/registo').json()
        self.assertEqual(dados['name'], 'EcoRota - Observação Ambiental')
        self.assertEqual(len(dados), 6)
        self.assertTrue(dados['config_url'].endswith('/config'))

    def test_sexto_servico_ainda_ausente(self):
        self.assertEqual(self.cliente.get('/atividade/instancia-001').status_code, 404)


if __name__ == '__main__':
    unittest.main()
