"""Suíte de testes automatizados para a Fase 6 — Módulo de Contas e Carteiras.

Verifica:
1. Listagem de contas com saldo consolidado (GET /api/contas);
2. Criação de nova conta (POST /api/contas) e validação de nome único por usuário;
3. Edição do nome da conta (PUT /api/contas/<id>);
4. Arquivamento e reativação de conta (PATCH);
5. Bloqueio de exclusão quando houver movimentações vinculadas e exclusão quando vazia;
6. Isolamento estrito de dados por usuário (anti-IDOR) retornando 404/403.
"""
import unittest
from decimal import Decimal
from app import create_app
from app.models import db, Usuario, Conta, Categoria, Lancamento, LancamentoRecorrente
from config.config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ContasTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Cria 2 usuários de teste para validar isolamento
        self.user1 = Usuario(nome="Usuário Um", email="user1@teste.com", tema_preferido="dark")
        self.user1.definir_senha("SenhaForte123")
        self.user2 = Usuario(nome="Usuário Dois", email="user2@teste.com", tema_preferido="dark")
        self.user2.definir_senha("SenhaForte123")
        db.session.add_all([self.user1, self.user2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def autenticar(self, usuario_id):
        with self.client.session_transaction() as sess:
            sess["usuario_id"] = usuario_id
            sess["_csrf_token"] = "csrf-token-valido"

    def test_crud_contas_e_isolamento(self):
        self.autenticar(self.user1.id)
        headers = {"X-CSRFToken": "csrf-token-valido"}

        # 1. Criação de conta
        res = self.client.post(
            "/api/contas",
            json={"nome": "Nubank", "saldo_inicial": 150.50},
            headers=headers,
        )
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data["sucesso"])
        conta_id = data["dados"]["conta"]["id"]
        self.assertEqual(data["dados"]["conta"]["nome"], "Nubank")

        # 2. Unicidade de nome para o mesmo usuário
        res_dup = self.client.post(
            "/api/contas",
            json={"nome": "Nubank", "saldo_inicial": 0},
            headers=headers,
        )
        self.assertEqual(res_dup.status_code, 400)

        # 3. Listagem
        res_list = self.client.get("/api/contas")
        self.assertEqual(res_list.status_code, 200)
        data_list = res_list.get_json()
        self.assertEqual(len(data_list["dados"]["contas"]), 1)
        self.assertEqual(data_list["dados"]["saldo_total_ativo"], 150.50)

        # 4. Edição
        res_edit = self.client.put(
            f"/api/contas/{conta_id}",
            json={"nome": "Nubank Principal"},
            headers=headers,
        )
        self.assertEqual(res_edit.status_code, 200)
        self.assertEqual(res_edit.get_json()["dados"]["conta"]["nome"], "Nubank Principal")

        # 5. Arquivamento e Reativação
        res_arq = self.client.patch(f"/api/contas/{conta_id}/arquivar", headers=headers)
        self.assertEqual(res_arq.status_code, 200)
        self.assertEqual(res_arq.get_json()["dados"]["conta"]["status"], "arquivado")

        res_reat = self.client.patch(f"/api/contas/{conta_id}/reativar", headers=headers)
        self.assertEqual(res_reat.status_code, 200)
        self.assertEqual(res_reat.get_json()["dados"]["conta"]["status"], "ativo")

        # 6. Anti-IDOR: Usuário 2 não pode acessar ou manipular conta do Usuário 1
        self.autenticar(self.user2.id)
        res_idor = self.client.put(
            f"/api/contas/{conta_id}",
            json={"nome": "Invasao"},
            headers=headers,
        )
        self.assertEqual(res_idor.status_code, 404)

        # 7. Exclusão de conta vazia permitida
        self.autenticar(self.user1.id)
        res_del = self.client.delete(f"/api/contas/{conta_id}", headers=headers)
        self.assertEqual(res_del.status_code, 200)

        # Verifica que foi excluída
        res_check = self.client.get("/api/contas")
        self.assertEqual(len(res_check.get_json()["dados"]["contas"]), 0)

    def test_exclusao_conta_com_vinculos(self):
        """Testa bloqueio com dados vinculados e opção de exclusão conjunta (FSD/Issue Carteiras)."""
        from datetime import date
        self.autenticar(self.user1.id)
        headers = {"X-CSRFToken": "csrf-token-valido"}

        # Cria categoria de apoio
        cat = Categoria(usuario_id=self.user1.id, nome="Alimentação", tipo="despesa")
        # Cria conta
        conta = Conta(usuario_id=self.user1.id, nome="Carteira Física", saldo_inicial=Decimal("200.00"))
        db.session.add_all([cat, conta])
        db.session.commit()

        # Cria 1 lançamento vinculado à conta
        lanc = Lancamento(
            usuario_id=self.user1.id,
            tipo="despesa",
            valor=Decimal("50.00"),
            data_competencia=date.today(),
            data_vencimento=date.today(),
            descricao="Almoço",
            categoria_id=cat.id,
            conta_id=conta.id,
            forma_pagamento="Dinheiro",
            status="pago",
        )
        # Cria 1 modelo recorrente vinculado à conta
        rec = LancamentoRecorrente(
            usuario_id=self.user1.id,
            tipo="despesa",
            valor=Decimal("30.00"),
            descricao="Assinatura Jornal",
            categoria_id=cat.id,
            conta_id=conta.id,
            dia_vencimento=10,
            ativo=True,
        )
        db.session.add_all([lanc, rec])
        db.session.commit()

        conta_id = conta.id
        lanc_id = lanc.id
        rec_id = rec.id

        # 1. Tentativa de exclusão direta sem flag de vínculos: deve ser bloqueada com dados informativos
        res_tentativa = self.client.delete(f"/api/contas/{conta_id}", headers=headers)
        self.assertEqual(res_tentativa.status_code, 400)
        dados_erro = res_tentativa.get_json()
        self.assertFalse(dados_erro["sucesso"])
        self.assertTrue(dados_erro["tem_vinculos"])
        self.assertEqual(dados_erro["total_lancamentos"], 1)
        self.assertEqual(dados_erro["total_recorrentes"], 1)

        # 2. Exclusão confirmando 'excluir_vinculados=true' via query parameter
        res_del = self.client.delete(f"/api/contas/{conta_id}?excluir_vinculados=true", headers=headers)
        self.assertEqual(res_del.status_code, 200)
        dados_del = res_del.get_json()
        self.assertTrue(dados_del["sucesso"])

        # Confirma que a conta, o lançamento e o recorrente foram excluídos
        self.assertIsNone(db.session.get(Conta, conta_id))
        self.assertIsNone(db.session.get(Lancamento, lanc_id))
        self.assertIsNone(db.session.get(LancamentoRecorrente, rec_id))

        # 3. Teste do endpoint POST /api/contas/<id>/excluir-com-vinculos
        conta2 = Conta(usuario_id=self.user1.id, nome="Conta Secundária", saldo_inicial=Decimal("100.00"))
        db.session.add(conta2)
        db.session.commit()

        conta2_id = conta2.id
        lanc2 = Lancamento(
            usuario_id=self.user1.id,
            tipo="receita",
            valor=Decimal("1000.00"),
            data_competencia=date.today(),
            data_vencimento=date.today(),
            descricao="Freelance",
            categoria_id=cat.id,
            conta_id=conta2.id,
            forma_pagamento="PIX",
            status="pago",
        )
        db.session.add(lanc2)
        db.session.commit()
        lanc2_id = lanc2.id

        res_post = self.client.post(f"/api/contas/{conta2_id}/excluir-com-vinculos", headers=headers)
        self.assertEqual(res_post.status_code, 200)
        self.assertTrue(res_post.get_json()["sucesso"])
        self.assertIsNone(db.session.get(Conta, conta2_id))
        self.assertIsNone(db.session.get(Lancamento, lanc2_id))


if __name__ == "__main__":
    unittest.main()
