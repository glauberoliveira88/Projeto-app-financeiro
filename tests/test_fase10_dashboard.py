"""Suíte de testes automatizados para a Fase 10 — Módulo do Painel Principal (Dashboard).

Conforme docs/FSD.md e docs/DESIGN.md:
- Valida o endpoint GET /api/dashboard/resumo;
- Cálculo do Saldo do Mês: (Receitas Pagas - Despesas Pagas);
- Total de Receitas (pagas e previstas) e Total de Despesas (pagas e previstas);
- Transferências internas entre contas não compõem nem alteram o somatório geral de receitas e despesas;
- Saldo consolidado das contas ativas;
- Agregação do gráfico monocromático de despesas por categoria com percentuais e valores;
- Bloco de alertas com lançamentos pendentes vencidos e a vencer nos próximos 5 dias;
- Quitação rápida de lançamentos em atraso/a vencer (PATCH /api/lancamentos/<id>/pagar);
- Isolamento absoluto de dados por usuário (anti-IDOR);
- Sincronização autônoma de lançamentos recorrentes.
"""
from datetime import date, timedelta
from decimal import Decimal
import unittest

from app import create_app
from app.models import db, Usuario, Conta, Categoria, Lancamento, LancamentoRecorrente
from config.config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class DashboardTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Criação de 2 usuários para validação anti-IDOR
        self.user1 = Usuario(nome="Arthur Silva", email="arthur@teste.com", tema_preferido="dark")
        self.user1.definir_senha("SenhaForte123")
        self.user2 = Usuario(nome="Outro Usuário", email="outro@teste.com", tema_preferido="dark")
        self.user2.definir_senha("SenhaForte123")
        db.session.add_all([self.user1, self.user2])
        db.session.commit()

        # Contas do Usuário 1
        self.conta1 = Conta(usuario_id=self.user1.id, nome="Nubank", saldo_inicial=Decimal("1000.00"), status="ativo")
        self.conta2 = Conta(usuario_id=self.user1.id, nome="Carteira Física", saldo_inicial=Decimal("200.00"), status="ativo")
        self.conta_arquivada = Conta(usuario_id=self.user1.id, nome="Poupança", saldo_inicial=Decimal("50.00"), status="arquivado")

        # Contas do Usuário 2
        self.conta_u2 = Conta(usuario_id=self.user2.id, nome="Conta U2", saldo_inicial=Decimal("500.00"), status="ativo")

        # Categorias do Usuário 1
        self.cat_salario = Categoria(usuario_id=self.user1.id, nome="Salário", tipo="receita")
        self.cat_rendimentos = Categoria(usuario_id=self.user1.id, nome="Rendimentos", tipo="receita")
        self.cat_moradia = Categoria(usuario_id=self.user1.id, nome="Moradia", tipo="despesa")
        self.cat_alimentacao = Categoria(usuario_id=self.user1.id, nome="Alimentação", tipo="despesa")
        self.cat_transporte = Categoria(usuario_id=self.user1.id, nome="Transporte", tipo="despesa")

        # Categorias do Usuário 2
        self.cat_moradia_u2 = Categoria(usuario_id=self.user2.id, nome="Moradia U2", tipo="despesa")

        db.session.add_all([
            self.conta1, self.conta2, self.conta_arquivada, self.conta_u2,
            self.cat_salario, self.cat_rendimentos, self.cat_moradia,
            self.cat_alimentacao, self.cat_transporte, self.cat_moradia_u2
        ])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def autenticar(self, email="arthur@teste.com", senha="SenhaForte123"):
        return self.client.post("/api/auth/login", json={"email": email, "senha": senha})

    def test_dashboard_metricas_calculo_e_transferencias(self):
        """Valida que saldo do mês considera apenas pagos e transferências não inflam receitas/despesas."""
        self.autenticar()
        hoje = date.today()

        # Receita paga: 5000.00
        l_rec_paga = Lancamento(
            usuario_id=self.user1.id,
            tipo="receita",
            valor=Decimal("5000.00"),
            data_competencia=hoje,
            data_vencimento=hoje,
            descricao="Salário Mensal",
            categoria_id=self.cat_salario.id,
            conta_id=self.conta1.id,
            forma_pagamento="PIX",
            status="pago",
        )
        # Receita pendente: 1000.00 (deve somar no total_receitas, mas NÃO no saldo_mes)
        l_rec_pendente = Lancamento(
            usuario_id=self.user1.id,
            tipo="receita",
            valor=Decimal("1000.00"),
            data_competencia=hoje,
            data_vencimento=hoje + timedelta(days=2),
            descricao="Freelance a receber",
            categoria_id=self.cat_rendimentos.id,
            conta_id=self.conta1.id,
            forma_pagamento="PIX",
            status="pendente",
        )
        # Despesa paga: 1500.00
        l_desp_paga = Lancamento(
            usuario_id=self.user1.id,
            tipo="despesa",
            valor=Decimal("1500.00"),
            data_competencia=hoje,
            data_vencimento=hoje,
            descricao="Aluguel",
            categoria_id=self.cat_moradia.id,
            conta_id=self.conta1.id,
            forma_pagamento="Boleto",
            status="pago",
        )
        # Despesa pendente: 500.00 (deve somar no total_despesas, mas NÃO no saldo_mes)
        l_desp_pendente = Lancamento(
            usuario_id=self.user1.id,
            tipo="despesa",
            valor=Decimal("500.00"),
            data_competencia=hoje,
            data_vencimento=hoje + timedelta(days=3),
            descricao="Supermercado previsto",
            categoria_id=self.cat_alimentacao.id,
            conta_id=self.conta1.id,
            forma_pagamento="Cartão de Crédito",
            status="pendente",
        )
        # Transferência entre contas: 300.00 (NÃO deve inflar total_receitas nem total_despesas)
        l_transf = Lancamento(
            usuario_id=self.user1.id,
            tipo="transferencia",
            valor=Decimal("300.00"),
            data_competencia=hoje,
            data_vencimento=hoje,
            descricao="Transferência para Carteira",
            categoria_id=None,
            conta_id=self.conta1.id,
            conta_destino_id=self.conta2.id,
            forma_pagamento="Transferência",
            status="pago",
        )
        # Lançamento soft-deletado (NÃO deve aparecer nem compor nada)
        l_deletado = Lancamento(
            usuario_id=self.user1.id,
            tipo="despesa",
            valor=Decimal("9999.00"),
            data_competencia=hoje,
            data_vencimento=hoje,
            descricao="Despesa cancelada",
            categoria_id=self.cat_moradia.id,
            conta_id=self.conta1.id,
            forma_pagamento="PIX",
            status="pago",
            deleted_at=hoje,
        )

        db.session.add_all([l_rec_paga, l_rec_pendente, l_desp_paga, l_desp_pendente, l_transf, l_deletado])
        db.session.commit()

        # Requisição ao endpoint do dashboard
        res = self.client.get(f"/api/dashboard/resumo?mes={hoje.month}&ano={hoje.year}")
        self.assertEqual(res.status_code, 200)
        dados = res.get_json()["dados"]

        metricas = dados["metricas"]
        # Total de receitas = 5000 + 1000 = 6000.00
        self.assertEqual(metricas["total_receitas"], 6000.00)
        self.assertEqual(metricas["total_receitas_pagas"], 5000.00)

        # Total de despesas = 1500 + 500 = 2000.00
        self.assertEqual(metricas["total_despesas"], 2000.00)
        self.assertEqual(metricas["total_despesas_pagas"], 1500.00)

        # Saldo líquido do mês = Receitas Pagas (5000) - Despesas Pagas (1500) = 3500.00
        self.assertEqual(metricas["saldo_mes"], 3500.00)

        # Saldo consolidado das contas ativas:
        # Conta 1: Saldo Inicial 1000 + Rec 5000 - Desp 1500 - Transf Saída 300 = 4200.00
        # Conta 2: Saldo Inicial 200 + Transf Entrada 300 = 500.00
        # Total contas ativas = 4200 + 500 = 4700.00 (Conta arquivada não entra)
        self.assertEqual(metricas["saldo_total_contas"], 4700.00)

    def test_dashboard_grafico_monocromatico_categorias(self):
        """Valida que o gráfico de despesas por categoria agrupa corretamente com porcentagens."""
        self.autenticar()
        hoje = date.today()

        # Moradia: 1500.00 (75%)
        l1 = Lancamento(
            usuario_id=self.user1.id,
            tipo="despesa",
            valor=Decimal("1500.00"),
            data_competencia=hoje,
            data_vencimento=hoje,
            descricao="Aluguel",
            categoria_id=self.cat_moradia.id,
            conta_id=self.conta1.id,
            status="pago",
        )
        # Transporte: 500.00 (25%)
        l2 = Lancamento(
            usuario_id=self.user1.id,
            tipo="despesa",
            valor=Decimal("500.00"),
            data_competencia=hoje,
            data_vencimento=hoje,
            descricao="Combustível",
            categoria_id=self.cat_transporte.id,
            conta_id=self.conta1.id,
            status="pago",
        )
        db.session.add_all([l1, l2])
        db.session.commit()

        res = self.client.get(f"/api/dashboard/resumo?mes={hoje.month}&ano={hoje.year}")
        self.assertEqual(res.status_code, 200)
        grafico = res.get_json()["dados"]["grafico_despesas_categoria"]

        self.assertEqual(len(grafico), 2)
        # Maior fatia vem primeiro
        self.assertEqual(grafico[0]["nome"], "Moradia")
        self.assertEqual(grafico[0]["total"], 1500.00)
        self.assertEqual(grafico[0]["porcentagem"], 75.0)

        self.assertEqual(grafico[1]["nome"], "Transporte")
        self.assertEqual(grafico[1]["total"], 500.00)
        self.assertEqual(grafico[1]["porcentagem"], 25.0)

    def test_dashboard_bloco_alertas_vencidos_e_a_vencer(self):
        """Valida a separação entre contas vencidas e contas que vencem nos próximos 5 dias."""
        self.autenticar()
        hoje = date.today()

        # 1. Despesa vencida há 2 dias (pendente)
        d_vencida = Lancamento(
            usuario_id=self.user1.id,
            tipo="despesa",
            valor=Decimal("120.00"),
            data_competencia=hoje,
            data_vencimento=hoje - timedelta(days=2),
            descricao="Conta de Luz Vencida",
            categoria_id=self.cat_moradia.id,
            conta_id=self.conta1.id,
            status="pendente",
        )
        # 2. Despesa a vencer daqui a 3 dias (pendente)
        d_a_vencer = Lancamento(
            usuario_id=self.user1.id,
            tipo="despesa",
            valor=Decimal("80.00"),
            data_competencia=hoje,
            data_vencimento=hoje + timedelta(days=3),
            descricao="Internet Próxima",
            categoria_id=self.cat_moradia.id,
            conta_id=self.conta1.id,
            status="pendente",
        )
        # 3. Despesa a vencer distante (daqui a 15 dias - não deve entrar no bloco de alerta)
        d_distante = Lancamento(
            usuario_id=self.user1.id,
            tipo="despesa",
            valor=Decimal("300.00"),
            data_competencia=hoje,
            data_vencimento=hoje + timedelta(days=15),
            descricao="Fatura Distante",
            categoria_id=self.cat_moradia.id,
            conta_id=self.conta1.id,
            status="pendente",
        )
        # 4. Despesa já paga (não deve constar em alertas)
        d_paga = Lancamento(
            usuario_id=self.user1.id,
            tipo="despesa",
            valor=Decimal("50.00"),
            data_competencia=hoje,
            data_vencimento=hoje - timedelta(days=5),
            descricao="Conta Paga",
            categoria_id=self.cat_moradia.id,
            conta_id=self.conta1.id,
            status="pago",
        )

        db.session.add_all([d_vencida, d_a_vencer, d_distante, d_paga])
        db.session.commit()

        res = self.client.get(f"/api/dashboard/resumo?mes={hoje.month}&ano={hoje.year}")
        self.assertEqual(res.status_code, 200)
        alertas = res.get_json()["dados"]["alertas"]

        self.assertEqual(len(alertas["vencidos"]), 1)
        self.assertEqual(alertas["vencidos"][0]["descricao"], "Conta de Luz Vencida")
        self.assertEqual(alertas["vencidos"][0]["situacao"], "vencido")

        self.assertEqual(len(alertas["a_vencer"]), 1)
        self.assertEqual(alertas["a_vencer"][0]["descricao"], "Internet Próxima")
        self.assertEqual(alertas["a_vencer"][0]["situacao"], "a_vencer")

        self.assertEqual(alertas["total_alertas"], 2)

    def test_dashboard_quitacao_rapida_de_alerta(self):
        """Valida que o endpoint PATCH /api/lancamentos/<id>/pagar quita a pendência e limpa o alerta."""
        self.autenticar()
        hoje = date.today()

        d_vencida = Lancamento(
            usuario_id=self.user1.id,
            tipo="despesa",
            valor=Decimal("150.00"),
            data_competencia=hoje,
            data_vencimento=hoje - timedelta(days=1),
            descricao="Água Atrasada",
            categoria_id=self.cat_moradia.id,
            conta_id=self.conta1.id,
            status="pendente",
        )
        db.session.add(d_vencida)
        db.session.commit()

        # Quitação rápida usando o endpoint já existente de lançamentos
        res_pagar = self.client.patch(f"/api/lancamentos/{d_vencida.id}/pagar")
        self.assertEqual(res_pagar.status_code, 200)
        self.assertEqual(res_pagar.get_json()["dados"]["novo_status"], "pago")

        # Verifica se o alerta sumiu no dashboard
        res_dash = self.client.get(f"/api/dashboard/resumo?mes={hoje.month}&ano={hoje.year}")
        self.assertEqual(res_dash.status_code, 200)
        alertas = res_dash.get_json()["dados"]["alertas"]
        self.assertEqual(len(alertas["vencidos"]), 0)

    def test_dashboard_isolamento_absoluto_anti_idor(self):
        """Garante que dados do Usuário 2 nunca vazam para o Usuário 1."""
        hoje = date.today()

        # Despesa do Usuário 2
        l_u2 = Lancamento(
            usuario_id=self.user2.id,
            tipo="despesa",
            valor=Decimal("9999.00"),
            data_competencia=hoje,
            data_vencimento=hoje,
            descricao="Segredo User 2",
            categoria_id=self.cat_moradia_u2.id,
            conta_id=self.conta_u2.id,
            status="pago",
        )
        db.session.add(l_u2)
        db.session.commit()

        # Usuário 1 loga e acessa o dashboard
        self.autenticar(email="arthur@teste.com", senha="SenhaForte123")
        res = self.client.get(f"/api/dashboard/resumo?mes={hoje.month}&ano={hoje.year}")
        self.assertEqual(res.status_code, 200)
        dados = res.get_json()["dados"]

        self.assertEqual(dados["metricas"]["total_despesas"], 0.0)
        self.assertEqual(len(dados["grafico_despesas_categoria"]), 0)

    def test_dashboard_dispara_sincronizacao_de_recorrentes(self):
        """Valida que a consulta do dashboard aciona a geração autônoma de fixos recorrentes."""
        self.autenticar()
        hoje = date.today()

        # Cadastra modelo de fixo ativo para o Usuário 1
        modelo_fixo = LancamentoRecorrente(
            usuario_id=self.user1.id,
            tipo="despesa",
            valor=Decimal("250.00"),
            descricao="Assinatura Mensal",
            categoria_id=self.cat_moradia.id,
            conta_id=self.conta1.id,
            forma_pagamento="PIX",
            dia_vencimento=10,
            ativo=True,
        )
        db.session.add(modelo_fixo)
        db.session.commit()

        # Antes do GET no dashboard, não há lançamentos gerados
        qtd_antes = Lancamento.query.filter_by(usuario_id=self.user1.id).count()
        self.assertEqual(qtd_antes, 0)

        # GET no dashboard dispara sincronização transparente
        res = self.client.get(f"/api/dashboard/resumo?mes={hoje.month}&ano={hoje.year}")
        self.assertEqual(res.status_code, 200)

        # Agora deve existir 1 lançamento pendente gerado a partir do fixo
        lanc_gerado = Lancamento.query.filter_by(usuario_id=self.user1.id, recorrente_id=modelo_fixo.id).first()
        self.assertIsNotNone(lanc_gerado)
        self.assertEqual(lanc_gerado.descricao, "Assinatura Mensal")
        self.assertEqual(lanc_gerado.status, "pendente")
        self.assertEqual(float(lanc_gerado.valor), 250.0)


if __name__ == "__main__":
    unittest.main()
