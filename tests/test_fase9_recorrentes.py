"""Suíte de testes automatizados para a Fase 9 — Módulo de Lançamentos Recorrentes.

Verifica:
1. Listagem de modelos de fixos (GET /api/recorrentes);
2. Cadastro de novos modelos (POST /api/recorrentes) com validações de valor, descrição,
   dia de vencimento (1 a 31), compatibilidade de tipo da categoria e contas ativas;
3. Atualização de parâmetros (PUT /api/recorrentes/<id>);
4. Alternância rápida de status ativo/pausado (PATCH /api/recorrentes/<id>/toggle);
5. Exclusão do modelo (DELETE /api/recorrentes/<id>) com preservação do histórico contábil;
6. Serviço de sincronização autônoma (sincronizar_recorrencias_usuario) com geração de
   lançamentos pendentes, não duplicação e ajuste automático de dias do mês (ex: dia 31 em fev/abr);
7. Gatilho sincronizado integrado à listagem de movimentações (GET /api/lancamentos);
8. Salvaguardas de isolamento por usuário (anti-IDOR) retornando 403 / 404.
"""
from datetime import date
from decimal import Decimal
import unittest

from app import create_app
from app.models import db, Usuario, Conta, Categoria, Lancamento, LancamentoRecorrente
from app.services.recorrentes_service import sincronizar_recorrencias_usuario
from config.config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class RecorrentesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Cria 2 usuários para testes de isolamento anti-IDOR
        self.user1 = Usuario(nome="Glauber Oliveira", email="glauber@teste.com", tema_preferido="dark")
        self.user1.definir_senha("SenhaForte123")
        self.user2 = Usuario(nome="Outro Usuário", email="outro@teste.com", tema_preferido="dark")
        self.user2.definir_senha("SenhaForte123")
        db.session.add_all([self.user1, self.user2])
        db.session.commit()

        # Contas do Usuário 1
        self.conta1 = Conta(usuario_id=self.user1.id, nome="Conta Corrente", saldo_inicial=Decimal("1000.00"), status="ativo")
        self.conta_arquivada = Conta(usuario_id=self.user1.id, nome="Conta Antiga", saldo_inicial=Decimal("0.00"), status="arquivado")
        # Conta do Usuário 2
        self.conta_user2 = Conta(usuario_id=self.user2.id, nome="Conta User 2", saldo_inicial=Decimal("500.00"), status="ativo")

        # Categorias do Usuário 1
        self.cat_moradia = Categoria(usuario_id=self.user1.id, nome="Moradia", tipo="despesa")
        self.cat_salario = Categoria(usuario_id=self.user1.id, nome="Salário", tipo="receita")
        # Categorias do Usuário 2
        self.cat_user2 = Categoria(usuario_id=self.user2.id, nome="Moradia U2", tipo="despesa")

        db.session.add_all([
            self.conta1, self.conta_arquivada, self.conta_user2,
            self.cat_moradia, self.cat_salario, self.cat_user2,
        ])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def autenticar(self, usuario_id):
        with self.client.session_transaction() as sess:
            sess["usuario_id"] = usuario_id
            sess["_csrf_token"] = "csrf-token-valido"

    def test_crud_recorrentes_completo(self):
        """Testa o fluxo completo de listagem, cadastro, edição, toggle e exclusão de fixos."""
        self.autenticar(self.user1.id)
        headers = {"X-CSRFToken": "csrf-token-valido"}

        # 1. Listagem inicial vazia
        res = self.client.get("/api/recorrentes", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["sucesso"])
        self.assertEqual(len(data["dados"]["recorrentes"]), 0)

        # 2. Cadastro de despesa fixa (Aluguel R$ 1.500,00 dia 10)
        res_post = self.client.post(
            "/api/recorrentes",
            json={
                "tipo": "despesa",
                "valor": "1500.00",
                "descricao": "Aluguel Apartamento",
                "categoria_id": self.cat_moradia.id,
                "conta_id": self.conta1.id,
                "forma_pagamento": "PIX",
                "dia_vencimento": 10,
                "ativo": True,
            },
            headers=headers,
        )
        self.assertEqual(res_post.status_code, 201)
        data_post = res_post.get_json()
        self.assertTrue(data_post["sucesso"])
        fixo_id = data_post["dados"]["recorrente"]["id"]
        self.assertEqual(data_post["dados"]["recorrente"]["descricao"], "Aluguel Apartamento")
        self.assertEqual(data_post["dados"]["recorrente"]["valor"], 1500.00)
        self.assertEqual(data_post["dados"]["recorrente"]["dia_vencimento"], 10)
        self.assertTrue(data_post["dados"]["recorrente"]["ativo"])

        # 3. Cadastro de receita fixa (Salário R$ 5.000,00 dia 5)
        res_post2 = self.client.post(
            "/api/recorrentes",
            json={
                "tipo": "receita",
                "valor": 5000.00,
                "descricao": "Salário Mensal",
                "categoria_id": self.cat_salario.id,
                "conta_id": self.conta1.id,
                "forma_pagamento": "Transferência",
                "dia_vencimento": 5,
                "ativo": True,
            },
            headers=headers,
        )
        self.assertEqual(res_post2.status_code, 201)

        # 4. Listagem com 2 fixos ordenados por dia_vencimento (5 antes de 10)
        res_list = self.client.get("/api/recorrentes", headers=headers)
        self.assertEqual(res_list.status_code, 200)
        data_list = res_list.get_json()
        self.assertEqual(data_list["dados"]["total"], 2)
        recs = data_list["dados"]["recorrentes"]
        self.assertEqual(recs[0]["dia_vencimento"], 5)
        self.assertEqual(recs[1]["dia_vencimento"], 10)

        # Filtro por tipo
        res_rec = self.client.get("/api/recorrentes?tipo=receita", headers=headers)
        self.assertEqual(len(res_rec.get_json()["dados"]["recorrentes"]), 1)
        self.assertEqual(res_rec.get_json()["dados"]["recorrentes"][0]["tipo"], "receita")

        # 5. Edição do fixo (PUT)
        res_put = self.client.put(
            f"/api/recorrentes/{fixo_id}",
            json={
                "valor": "1600.00",
                "descricao": "Aluguel com Condomínio",
                "dia_vencimento": 12,
            },
            headers=headers,
        )
        self.assertEqual(res_put.status_code, 200)
        data_put = res_put.get_json()
        self.assertEqual(data_put["dados"]["recorrente"]["valor"], 1600.00)
        self.assertEqual(data_put["dados"]["recorrente"]["descricao"], "Aluguel com Condomínio")
        self.assertEqual(data_put["dados"]["recorrente"]["dia_vencimento"], 12)

        # 6. Toggle ativo <-> pausado
        res_toggle = self.client.patch(f"/api/recorrentes/{fixo_id}/toggle", headers=headers)
        self.assertEqual(res_toggle.status_code, 200)
        self.assertFalse(res_toggle.get_json()["dados"]["recorrente"]["ativo"])

        # Reativa
        res_toggle2 = self.client.patch(f"/api/recorrentes/{fixo_id}/toggle", headers=headers)
        self.assertTrue(res_toggle2.get_json()["dados"]["recorrente"]["ativo"])

        # 7. Exclusão do fixo (DELETE)
        res_del = self.client.delete(f"/api/recorrentes/{fixo_id}", headers=headers)
        self.assertEqual(res_del.status_code, 200)

        # Confirma que foi excluído da lista
        res_check = self.client.get("/api/recorrentes", headers=headers)
        self.assertEqual(res_check.get_json()["dados"]["total"], 1)

    def test_validacoes_cadastro_recorrente(self):
        """Testa todas as regras de validação ao cadastrar um modelo recorrente."""
        self.autenticar(self.user1.id)
        headers = {"X-CSRFToken": "csrf-token-valido"}

        # 1. Tipo inválido
        res = self.client.post("/api/recorrentes", json={"tipo": "invalido", "valor": 100, "descricao": "Teste"}, headers=headers)
        self.assertEqual(res.status_code, 400)

        # 2. Valor negativo ou zero
        res = self.client.post("/api/recorrentes", json={"tipo": "despesa", "valor": 0, "descricao": "Teste", "categoria_id": self.cat_moradia.id, "conta_id": self.conta1.id, "dia_vencimento": 10}, headers=headers)
        self.assertEqual(res.status_code, 400)

        # 3. Dia de vencimento fora de 1..31
        res = self.client.post("/api/recorrentes", json={"tipo": "despesa", "valor": 100, "descricao": "Teste", "categoria_id": self.cat_moradia.id, "conta_id": self.conta1.id, "dia_vencimento": 32}, headers=headers)
        self.assertEqual(res.status_code, 400)
        res = self.client.post("/api/recorrentes", json={"tipo": "despesa", "valor": 100, "descricao": "Teste", "categoria_id": self.cat_moradia.id, "conta_id": self.conta1.id, "dia_vencimento": 0}, headers=headers)
        self.assertEqual(res.status_code, 400)

        # 4. Categoria incompatível com o tipo da movimentação
        res = self.client.post(
            "/api/recorrentes",
            json={
                "tipo": "despesa",
                "valor": 100,
                "descricao": "Tentativa Incompatível",
                "categoria_id": self.cat_salario.id,  # cat_salario é tipo receita!
                "conta_id": self.conta1.id,
                "dia_vencimento": 10,
            },
            headers=headers,
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("incompatível", res.get_json()["erro"].lower())

        # 5. Conta arquivada
        res = self.client.post(
            "/api/recorrentes",
            json={
                "tipo": "despesa",
                "valor": 100,
                "descricao": "Conta Arquivada",
                "categoria_id": self.cat_moradia.id,
                "conta_id": self.conta_arquivada.id,  # arquivada!
                "dia_vencimento": 10,
            },
            headers=headers,
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("arquivada", res.get_json()["erro"].lower())

    def test_isolamento_de_dados_idor(self):
        """Garante que um usuário não consiga acessar, vincular, alterar ou excluir fixos alheios."""
        self.autenticar(self.user1.id)
        headers = {"X-CSRFToken": "csrf-token-valido"}

        # Tentativa de vincular conta de outro usuário
        res_conta_idor = self.client.post(
            "/api/recorrentes",
            json={
                "tipo": "despesa",
                "valor": 100,
                "descricao": "Teste IDOR Conta",
                "categoria_id": self.cat_moradia.id,
                "conta_id": self.conta_user2.id,
                "dia_vencimento": 10,
            },
            headers=headers,
        )
        self.assertEqual(res_conta_idor.status_code, 403)

        # Tentativa de vincular categoria de outro usuário
        res_cat_idor = self.client.post(
            "/api/recorrentes",
            json={
                "tipo": "despesa",
                "valor": 100,
                "descricao": "Teste IDOR Categoria",
                "categoria_id": self.cat_user2.id,
                "conta_id": self.conta1.id,
                "dia_vencimento": 10,
            },
            headers=headers,
        )
        self.assertEqual(res_cat_idor.status_code, 403)

        # Cria fixo para Usuário 2 diretamente no banco
        fixo_user2 = LancamentoRecorrente(
            usuario_id=self.user2.id,
            tipo="despesa",
            valor=Decimal("200.00"),
            descricao="Segredo User 2",
            categoria_id=self.cat_user2.id,
            conta_id=self.conta_user2.id,
            dia_vencimento=15,
            ativo=True,
        )
        db.session.add(fixo_user2)
        db.session.commit()

        # Usuário 1 tenta alterar fixo do Usuário 2 -> 403
        res_put_idor = self.client.put(f"/api/recorrentes/{fixo_user2.id}", json={"valor": 999}, headers=headers)
        self.assertEqual(res_put_idor.status_code, 403)

        # Usuário 1 tenta toggle no fixo do Usuário 2 -> 403
        res_toggle_idor = self.client.patch(f"/api/recorrentes/{fixo_user2.id}/toggle", headers=headers)
        self.assertEqual(res_toggle_idor.status_code, 403)

        # Usuário 1 tenta excluir fixo do Usuário 2 -> 403
        res_del_idor = self.client.delete(f"/api/recorrentes/{fixo_user2.id}", headers=headers)
        self.assertEqual(res_del_idor.status_code, 403)

    def test_sincronizacao_autonoma_e_ajuste_meses_curtos(self):
        """Testa o serviço sincronizar_recorrencias_usuario:
        - Geração de lançamentos pendentes com campos copiados;
        - Ajuste automático de dia de vencimento em meses com menos dias (ex: dia 31 em abril e fevereiro);
        - Não duplicação de lançamentos já gerados.
        """
        # Cria modelo recorrente com dia 31
        modelo_dia_31 = LancamentoRecorrente(
            usuario_id=self.user1.id,
            tipo="despesa",
            valor=Decimal("120.00"),
            descricao="Assinatura Mensal Dia 31",
            categoria_id=self.cat_moradia.id,
            conta_id=self.conta1.id,
            forma_pagamento="Cartão de Crédito",
            dia_vencimento=31,
            ativo=True,
        )
        db.session.add(modelo_dia_31)
        db.session.commit()

        # 1. Sincroniza para Abril de 2026 (mês de 30 dias)
        gerados_abril = sincronizar_recorrencias_usuario(usuario_id=self.user1.id, ano=2026, mes=4)
        self.assertEqual(len(gerados_abril), 1)
        lanc_abril = gerados_abril[0]
        self.assertEqual(lanc_abril.data_vencimento, date(2026, 4, 30))  # Ajustado para 30!
        self.assertEqual(lanc_abril.data_competencia, date(2026, 4, 30))
        self.assertEqual(lanc_abril.status, "pendente")
        self.assertEqual(lanc_abril.recorrente_id, modelo_dia_31.id)

        # 2. Executa novamente para Abril de 2026: NÃO deve duplicar
        gerados_abril_repetido = sincronizar_recorrencias_usuario(usuario_id=self.user1.id, ano=2026, mes=4)
        self.assertEqual(len(gerados_abril_repetido), 0)

        # 3. Sincroniza para Fevereiro de 2026 (ano não bissexto -> 28 dias)
        gerados_fev = sincronizar_recorrencias_usuario(usuario_id=self.user1.id, ano=2026, mes=2)
        self.assertEqual(len(gerados_fev), 1)
        lanc_fev = gerados_fev[0]
        self.assertEqual(lanc_fev.data_vencimento, date(2026, 2, 28))  # Ajustado para 28!

        # 4. Sincroniza para Janeiro de 2026 (31 dias)
        gerados_jan = sincronizar_recorrencias_usuario(usuario_id=self.user1.id, ano=2026, mes=1)
        self.assertEqual(len(gerados_jan), 1)
        self.assertEqual(gerados_jan[0].data_vencimento, date(2026, 1, 31))

        # 5. Se o lançamento for excluído pelo usuário (soft delete), a rotina NÃO deve recriá-lo
        lanc_abril.deleted_at = date(2026, 4, 15)
        db.session.commit()
        gerados_pos_delete = sincronizar_recorrencias_usuario(usuario_id=self.user1.id, ano=2026, mes=4)
        self.assertEqual(len(gerados_pos_delete), 0)

        # 6. Modelo pausado (ativo=False) NÃO gera lançamentos
        modelo_dia_31.ativo = False
        db.session.commit()
        gerados_maio = sincronizar_recorrencias_usuario(usuario_id=self.user1.id, ano=2026, mes=5)
        self.assertEqual(len(gerados_maio), 0)

    def test_sincronizacao_integrada_ao_listar_lancamentos(self):
        """Garante que ao consultar GET /api/lancamentos, a sincronização é acionada de forma transparente."""
        self.autenticar(self.user1.id)
        headers = {"X-CSRFToken": "csrf-token-valido"}

        # Cria modelo ativo para dia 15
        modelo = LancamentoRecorrente(
            usuario_id=self.user1.id,
            tipo="receita",
            valor=Decimal("3500.00"),
            descricao="Salário Fixado",
            categoria_id=self.cat_salario.id,
            conta_id=self.conta1.id,
            forma_pagamento="Transferência",
            dia_vencimento=15,
            ativo=True,
        )
        db.session.add(modelo)
        db.session.commit()

        # Usuário consulta lançamentos de Outubro de 2026
        res = self.client.get("/api/lancamentos?mes=10&ano=2026", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["sucesso"])

        # O lançamento do salário fixo deve constar na listagem automaticamente gerado como pendente
        lancamentos = data["dados"]["lancamentos"]
        self.assertEqual(len(lancamentos), 1)
        self.assertEqual(lancamentos[0]["descricao"], "Salário Fixado")
        self.assertEqual(lancamentos[0]["status"], "pendente")
        self.assertEqual(lancamentos[0]["data_competencia"], "2026-10-15")

    def test_preservacao_de_historico_ao_excluir_modelo(self):
        """Garante que ao excluir um modelo recorrente, os lançamentos gerados no passado permanecem intactos."""
        self.autenticar(self.user1.id)
        headers = {"X-CSRFToken": "csrf-token-valido"}

        # Cria modelo e gera lançamento
        modelo = LancamentoRecorrente(
            usuario_id=self.user1.id,
            tipo="despesa",
            valor=Decimal("50.00"),
            descricao="Internet Fibra",
            categoria_id=self.cat_moradia.id,
            conta_id=self.conta1.id,
            dia_vencimento=20,
            ativo=True,
        )
        db.session.add(modelo)
        db.session.commit()

        gerados = sincronizar_recorrencias_usuario(usuario_id=self.user1.id, ano=2026, mes=3)
        lanc_gerado_id = gerados[0].id

        # Exclui o modelo via endpoint
        res_del = self.client.delete(f"/api/recorrentes/{modelo.id}", headers=headers)
        self.assertEqual(res_del.status_code, 200)

        # Modelo não existe mais
        self.assertIsNone(db.session.get(LancamentoRecorrente, modelo.id))

        # Mas o lançamento continua no banco com recorrente_id = None
        lanc = db.session.get(Lancamento, lanc_gerado_id)
        self.assertIsNotNone(lanc)
        self.assertIsNone(lanc.recorrente_id)
        self.assertEqual(lanc.descricao, "Internet Fibra")


if __name__ == "__main__":
    unittest.main()
