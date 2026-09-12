"""Testes automatizados da Fase 3 — Camada de Modelos (ORM) e Mecanismo de Logs Estruturados.

Valida os modelos SQLAlchemy, relacionamentos, fórmulas contábeis de saldo,
orçamentos por categoria, regras de soft delete, recorrências e mecanismo de logs com contingência.
"""
import unittest
import os
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal
from app import create_app
from app.models import (
    db,
    Usuario,
    Conta,
    Categoria,
    Lancamento,
    LancamentoRecorrente,
    LogErro,
    LogSeguranca,
)
from app.services.logger_service import registrar_erro, registrar_seguranca


class TestFase3ModelsELogs(unittest.TestCase):
    """Suíte de testes para a Fase 3."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    def setUp(self):
        """Limpa dados de testes anteriores para garantir isolamento."""
        self.limpar_dados_teste()

    def tearDown(self):
        """Limpa dados gerados após cada teste."""
        db.session.remove()
        self.limpar_dados_teste()

    def limpar_dados_teste(self):
        """Remove registros com e-mails de teste."""
        try:
            usuarios_teste = Usuario.query.filter(
                Usuario.email.like("%@teste.com")
            ).all()
            for u in usuarios_teste:
                # Remove logs associados
                LogErro.query.filter_by(usuario_id=u.id).delete()
                LogSeguranca.query.filter_by(usuario_id=u.id).delete()
                # Deleta usuário (cascateia contas, categorias, lançamentos)
                db.session.delete(u)
            db.session.commit()
        except Exception:
            db.session.rollback()

    def test_01_usuario_senha_e_token(self):
        """Testa regras do modelo Usuario (hashing, senha curta, tokens de recuperação)."""
        user = Usuario(nome="Carlos Silva", email="carlos@teste.com")
        
        # Teste de validação de tamanho mínimo de senha (mínimo 8 caracteres)
        with self.assertRaises(ValueError):
            user.definir_senha("curta")

        user.definir_senha("SenhaForte123")
        db.session.add(user)
        db.session.commit()

        self.assertIsNotNone(user.id)
        self.assertIsNotNone(user.senha_hash)
        self.assertNotEqual(user.senha_hash, "SenhaForte123")
        self.assertTrue(user.verificar_senha("SenhaForte123"))
        self.assertFalse(user.verificar_senha("SenhaErrada123"))

        # Teste de geração e validação de token de recuperação
        token = user.gerar_token_recuperacao(horas_validade=2)
        db.session.commit()

        self.assertTrue(user.validar_token_recuperacao(token))
        self.assertFalse(user.validar_token_recuperacao("token_falso"))

        # Teste de token expirado
        user.token_recuperacao_expira = datetime.now(timezone.utc) - timedelta(minutes=1)
        self.assertFalse(user.validar_token_recuperacao(token))

        # Teste de limpeza do token
        user.limpar_token_recuperacao()
        self.assertIsNone(user.token_recuperacao)
        self.assertIsNone(user.token_recuperacao_expira)

        # Teste de to_dict
        d = user.to_dict()
        self.assertEqual(d["email"], "carlos@teste.com")
        self.assertNotIn("senha_hash", d)
        self.assertNotIn("token_recuperacao", d)

    def test_02_conta_e_calculo_saldo_contabil(self):
        """Testa o cálculo do saldo contábil em tempo real de uma conta (FSD Seção 6.5)."""
        user = Usuario(nome="Ana Lima", email="ana@teste.com")
        user.definir_senha("senha12345")
        db.session.add(user)
        db.session.commit()

        conta_principal = Conta(usuario_id=user.id, nome="Banco Principal", saldo_inicial=Decimal("1000.00"))
        conta_reserva = Conta(usuario_id=user.id, nome="Reserva", saldo_inicial=Decimal("500.00"))
        db.session.add_all([conta_principal, conta_reserva])
        db.session.commit()

        # Saldo inicial verificado
        self.assertEqual(conta_principal.calcular_saldo_atual(), Decimal("1000.00"))
        self.assertEqual(conta_reserva.calcular_saldo_atual(), Decimal("500.00"))

        cat_salario = Categoria(usuario_id=user.id, nome="Salário", tipo="receita")
        cat_mercado = Categoria(usuario_id=user.id, nome="Mercado", tipo="despesa")
        db.session.add_all([cat_salario, cat_mercado])
        db.session.commit()

        hoje = date.today()

        # 1. Receita paga: +3000.00 no Banco Principal
        r1 = Lancamento(
            usuario_id=user.id,
            conta_id=conta_principal.id,
            categoria_id=cat_salario.id,
            tipo="receita",
            valor=Decimal("3000.00"),
            data_competencia=hoje,
            data_vencimento=hoje,
            descricao="Salário mensal",
            status="pago",
        )
        # 2. Despesa paga: -500.00 no Banco Principal
        d1 = Lancamento(
            usuario_id=user.id,
            conta_id=conta_principal.id,
            categoria_id=cat_mercado.id,
            tipo="despesa",
            valor=Decimal("500.00"),
            data_competencia=hoje,
            data_vencimento=hoje,
            descricao="Supermercado",
            status="pago",
        )
        # 3. Despesa pendente (NÃO deve impactar o saldo realizado): 200.00
        d_pendente = Lancamento(
            usuario_id=user.id,
            conta_id=conta_principal.id,
            categoria_id=cat_mercado.id,
            tipo="despesa",
            valor=Decimal("200.00"),
            data_competencia=hoje,
            data_vencimento=hoje + timedelta(days=3),
            descricao="Conta de Luz",
            status="pendente",
        )
        # 4. Transferência de Banco Principal para Reserva: 800.00
        t1 = Lancamento(
            usuario_id=user.id,
            conta_id=conta_principal.id,
            conta_destino_id=conta_reserva.id,
            tipo="transferencia",
            valor=Decimal("800.00"),
            data_competencia=hoje,
            data_vencimento=hoje,
            descricao="Poupar para reserva",
            status="pago",
        )

        db.session.add_all([r1, d1, d_pendente, t1])
        db.session.commit()

        # Cálculo esperado Banco Principal:
        # 1000.00 (inicial) + 3000.00 (receita) - 500.00 (despesa) - 800.00 (transf enviada) = 2700.00
        self.assertEqual(conta_principal.calcular_saldo_atual(), Decimal("2700.00"))

        # Cálculo esperado Reserva:
        # 500.00 (inicial) + 800.00 (transf recebida) = 1300.00
        self.assertEqual(conta_reserva.calcular_saldo_atual(), Decimal("1300.00"))

        # Teste de verificação de movimentações vinculadas
        self.assertTrue(conta_principal.tem_movimentacoes())
        self.assertTrue(conta_reserva.tem_movimentacoes())

        # Teste de Soft Delete: se excluirmos a despesa d1 (500.00), o saldo deve recalculado automaticamente
        d1.soft_delete()
        db.session.commit()
        # Novo saldo Banco Principal: 1000 + 3000 - 800 = 3200.00
        self.assertEqual(conta_principal.calcular_saldo_atual(), Decimal("3200.00"))

    def test_03_categoria_consumo_e_teto(self):
        """Testa regras de Categoria, cálculo de consumo mensal e percentual de teto."""
        user = Usuario(nome="Bruno Dias", email="bruno@teste.com")
        user.definir_senha("senha12345")
        db.session.add(user)
        db.session.commit()

        cat = Categoria(
            usuario_id=user.id,
            nome="Alimentação",
            tipo="despesa",
            teto_orcamento=Decimal("1000.00"),
        )
        conta = Conta(usuario_id=user.id, nome="Carteira", saldo_inicial=Decimal("200.00"))
        db.session.add_all([cat, conta])
        db.session.commit()

        ano_atual = date.today().year
        mes_atual = date.today().month

        # Inicialmente consumo é 0
        self.assertEqual(cat.consumo_mes(ano_atual, mes_atual), Decimal("0.00"))
        self.assertEqual(cat.porcentagem_consumo(ano_atual, mes_atual), 0.0)

        # Adiciona despesa de 600.00
        l1 = Lancamento(
            usuario_id=user.id,
            conta_id=conta.id,
            categoria_id=cat.id,
            tipo="despesa",
            valor=Decimal("600.00"),
            data_competencia=date(ano_atual, mes_atual, 10),
            data_vencimento=date(ano_atual, mes_atual, 10),
            descricao="Restaurantes",
            status="pago",
        )
        db.session.add(l1)
        db.session.commit()

        self.assertEqual(cat.consumo_mes(ano_atual, mes_atual), Decimal("600.00"))
        self.assertEqual(cat.porcentagem_consumo(ano_atual, mes_atual), 60.0)

        # Serialização com inclusão de consumo
        d = cat.to_dict(ano=ano_atual, mes=mes_atual, incluir_consumo=True)
        self.assertEqual(d["consumo_mes"], 600.0)
        self.assertEqual(d["porcentagem_consumo"], 60.0)
        self.assertFalse(d["teto_excedido"])

        # Adiciona mais 500.00 (total 1100.00 > teto 1000.00)
        l2 = Lancamento(
            usuario_id=user.id,
            conta_id=conta.id,
            categoria_id=cat.id,
            tipo="despesa",
            valor=Decimal("500.00"),
            data_competencia=date(ano_atual, mes_atual, 15),
            data_vencimento=date(ano_atual, mes_atual, 15),
            descricao="Lanches",
            status="pago",
        )
        db.session.add(l2)
        db.session.commit()

        d2 = cat.to_dict(ano=ano_atual, mes=mes_atual, incluir_consumo=True)
        self.assertEqual(d2["consumo_mes"], 1100.0)
        self.assertEqual(d2["porcentagem_consumo"], 110.0)
        self.assertTrue(d2["teto_excedido"])

    def test_04_lancamento_recorrente_ajuste_datas(self):
        """Testa o ajuste automático de dia de vencimento em meses mais curtos (FSD Seção 6.4)."""
        user = Usuario(nome="Lucas Moura", email="lucas@teste.com")
        user.definir_senha("senha12345")
        db.session.add(user)
        db.session.commit()

        conta = Conta(usuario_id=user.id, nome="Conta Teste", saldo_inicial=Decimal("0.00"))
        cat = Categoria(usuario_id=user.id, nome="Assinaturas", tipo="despesa")
        db.session.add_all([conta, cat])
        db.session.commit()

        # Recorrência configurada para o dia 31
        rec = LancamentoRecorrente(
            usuario_id=user.id,
            conta_id=conta.id,
            categoria_id=cat.id,
            tipo="despesa",
            valor=Decimal("50.00"),
            descricao="Streaming",
            dia_vencimento=31,
            ativo=True,
        )
        db.session.add(rec)
        db.session.commit()

        # Em janeiro (31 dias): deve ser dia 31
        self.assertEqual(rec.obter_data_vencimento_para_mes(2026, 1), date(2026, 1, 31))
        # Em abril (30 dias): deve ajustar para dia 30
        self.assertEqual(rec.obter_data_vencimento_para_mes(2026, 4), date(2026, 4, 30))
        # Em fevereiro de ano não bissexto (2026): deve ajustar para dia 28
        self.assertEqual(rec.obter_data_vencimento_para_mes(2026, 2), date(2026, 2, 28))
        # Em fevereiro de ano bissexto (2028): deve ajustar para dia 29
        self.assertEqual(rec.obter_data_vencimento_para_mes(2028, 2), date(2028, 2, 29))

    def test_05_lancamento_alertas_vencimento(self):
        """Testa os métodos de alerta de vencimento em Lancamento."""
        hoje = date.today()
        user = Usuario(nome="Marcos", email="marcos@teste.com")
        user.definir_senha("senha12345")
        db.session.add(user)
        db.session.commit()

        conta = Conta(usuario_id=user.id, nome="Carteira", saldo_inicial=Decimal("0.00"))
        cat = Categoria(usuario_id=user.id, nome="Diversos", tipo="despesa")
        db.session.add_all([conta, cat])
        db.session.commit()

        # 1. Lançamento vencido há 2 dias
        vencido = Lancamento(
            usuario_id=user.id,
            conta_id=conta.id,
            categoria_id=cat.id,
            tipo="despesa",
            valor=Decimal("100.00"),
            data_competencia=hoje - timedelta(days=2),
            data_vencimento=hoje - timedelta(days=2),
            descricao="Boleto Atrasado",
            status="pendente",
        )
        # 2. Lançamento que vence em 3 dias (dentro do alerta de 5 dias)
        proximo = Lancamento(
            usuario_id=user.id,
            conta_id=conta.id,
            categoria_id=cat.id,
            tipo="despesa",
            valor=Decimal("80.00"),
            data_competencia=hoje,
            data_vencimento=hoje + timedelta(days=3),
            descricao="Conta próxima",
            status="pendente",
        )
        # 3. Lançamento distante (vence em 20 dias)
        distante = Lancamento(
            usuario_id=user.id,
            conta_id=conta.id,
            categoria_id=cat.id,
            tipo="despesa",
            valor=Decimal("90.00"),
            data_competencia=hoje,
            data_vencimento=hoje + timedelta(days=20),
            descricao="Conta futura",
            status="pendente",
        )
        # 4. Lançamento já pago
        pago = Lancamento(
            usuario_id=user.id,
            conta_id=conta.id,
            categoria_id=cat.id,
            tipo="despesa",
            valor=Decimal("120.00"),
            data_competencia=hoje - timedelta(days=5),
            data_vencimento=hoje - timedelta(days=5),
            descricao="Conta quitada",
            status="pago",
        )

        db.session.add_all([vencido, proximo, distante, pago])
        db.session.commit()

        self.assertTrue(vencido.esta_vencido(hoje))
        self.assertFalse(vencido.esta_proximo_vencimento(5, hoje))

        self.assertFalse(proximo.esta_vencido(hoje))
        self.assertTrue(proximo.esta_proximo_vencimento(5, hoje))

        self.assertFalse(distante.esta_vencido(hoje))
        self.assertFalse(distante.esta_proximo_vencimento(5, hoje))

        self.assertFalse(pago.esta_vencido(hoje))
        self.assertFalse(pago.esta_proximo_vencimento(5, hoje))

    def test_06_logs_estruturados_e_contingencia(self):
        """Testa a gravação de logs de erro e segurança estruturados no MySQL e contingência."""
        user = Usuario(nome="Renata", email="renata@teste.com")
        user.definir_senha("senha12345")
        db.session.add(user)
        db.session.commit()

        # 1. Gravação com sucesso no MySQL via serviço
        sucesso_erro = registrar_erro(
            nivel="ERROR",
            mensagem="Simulação de erro operacional de teste",
            rota="POST /api/teste",
            stack_trace="Traceback teste...",
            usuario_id=user.id,
            ip="127.0.0.1",
        )
        self.assertTrue(sucesso_erro)

        log_gravado = LogErro.query.filter_by(usuario_id=user.id).first()
        self.assertIsNotNone(log_gravado)
        self.assertEqual(log_gravado.nivel, "ERROR")
        self.assertIn("Simulação de erro operacional", log_gravado.mensagem)

        # 2. Gravação de evento de segurança
        sucesso_seg = registrar_seguranca(
            evento="LOGIN_INVALIDO",
            ip="127.0.0.1",
            usuario_id=user.id,
            detalhes="Tentativa incorreta de login",
        )
        self.assertTrue(sucesso_seg)

        seg_gravado = LogSeguranca.query.filter_by(usuario_id=user.id).first()
        self.assertIsNotNone(seg_gravado)
        self.assertEqual(seg_gravado.evento, "LOGIN_INVALIDO")

        # 3. Teste do manipulador de erro 500 via Flask test_client
        client = self.app.test_client()

        # Criamos uma rota temporária para simular um erro 500
        @self.app.route("/api/teste-erro-500")
        def rota_com_falha():
            raise RuntimeError("Erro não tratado forçado para teste!")

        res = client.get("/api/teste-erro-500")
        self.assertEqual(res.status_code, 500)
        dados = res.get_json()
        self.assertFalse(dados["sucesso"])
        self.assertIn("Ocorreu um erro interno ao processar sua solicitação", dados["erro"])
        # Garante que não expõe detalhes técnicos de código para o usuário
        self.assertNotIn("RuntimeError", dados["erro"])

    def test_07_contingencia_em_arquivo_quando_mysql_falha(self):
        """Testa o acionamento automático da contingência em logs/error.log se o MySQL falhar (FSD 19.1)."""
        from unittest.mock import patch

        log_file_path = self.app.config.get("LOG_FILE_PATH")

        # Simula indisponibilidade ou falha do MySQL ao tentar gravar no LogErro
        with patch.object(LogErro, "registrar", side_effect=Exception("MySQL Connection Lost 2006")):
            resultado = registrar_erro(
                nivel="CRITICAL",
                mensagem="Falha crítica simulada para testar contingência de log",
                rota="GET /api/dashboard",
                stack_trace="Traceback simulado...",
                ip="192.168.1.100",
            )
            # Deve retornar False indicando que o MySQL falhou e contingência foi acionada
            self.assertFalse(resultado)

        # Valida que o arquivo logs/error.log recebeu o registro de contingência
        self.assertTrue(os.path.exists(log_file_path))
        with open(log_file_path, "r", encoding="utf-8") as f:
            conteudo_log = f.read()
        self.assertIn("[CONTINGÊNCIA DE LOG]", conteudo_log)
        self.assertIn("Falha crítica simulada para testar contingência de log", conteudo_log)


if __name__ == "__main__":
    unittest.main()

