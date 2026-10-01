# Estado Atual do Projeto — FinançasSimples

* **Última atualização:** 2026-10-01 (Conclusão da Fase 9: Módulo de Lançamentos Recorrentes com automação de fixos, sincronização transparente e interface React)
* **Fase atual:** Fase 9 concluída — Módulo de Lançamentos Recorrentes
* **Próximo passo recomendado:** Iniciar a Fase 10 (Módulo do Painel Principal - Dashboard, Gráficos Monocromáticos e Alertas)



---

## Status Geral por Fase

| Fase | Descrição | Status |
| :---: | :--- | :---: |
| **Fase 1** | Infraestrutura e Base do Projeto | **Concluída** |
| **Fase 2** | Banco de Dados, Schema e Migrations Versionadas | **Concluída** |
| **Fase 3** | Camada de Modelos (ORM) e Mecanismo de Logs Estruturados | **Concluída** |
| **Fase 4** | Autenticação, Sessão, Google OAuth e Proteção de Rotas | **Concluída** |
| **Fase 5** | Shell Base da Interface (Design Obsidian, CSS, Meta CSRF e Casca React) | **Concluída** |
| **Fase 6** | Módulo de Contas e Carteiras | **Concluída** |
| **Fase 7** | Módulo de Categorias e Orçamentos (Provisionamento Canônico e Reatribuição) | **Concluída** |
| **Fase 8** | Módulo de Lançamentos (Receitas, Despesas, Transferências e Soft Delete) | **Concluída** |
| **Fase 9** | Módulo de Lançamentos Recorrentes (Automação de Fixos e Sincronização) | **Concluída** |
| **Fase 10** | Módulo do Painel Principal (Dashboard, Gráficos e Alertas) | Pendente |
| **Fase 11** | Módulo de Configurações, Perfil e Alternância de Tema | Pendente |
| **Fase 12** | Revisão de Segurança, Testes Locais e Preparação para Deploy | Pendente |



---

## Checklist Detalhado por Fase

### Fase 1 — Infraestrutura e Base do Projeto
- [x] Estrutura de pastas do projeto criada (`app/`, `app/controllers/`, `app/models/`, `app/templates/`, `app/static/`, `config/`, `database/`, `logs/`);
- [x] Arquivo de dependências `requirements.txt` estruturado com as bibliotecas definidas no FSD;
- [x] Arquivos de configuração em código Python criados (`config/config.py` e `config/config.example.py`), sem uso de `.env`;
- [x] Application Factory base criada em `app/__init__.py`;
- [x] Pontos de entrada criados: `run.py` (desenvolvimento local) e `wsgi.py` (produção PythonAnywhere);
- [x] Proteção de arquivos sensíveis via `.htaccess` para servidores Apache;
- [x] Pasta de contingência de logs criada (`logs/`) com `.gitkeep` e arquivo `logs/error.log`;
- [x] Estrutura do executor de migrações preparada em `database/migrate.py` e pasta `database/migrations/`;
- [x] Insumos visuais copiados para a pasta pública de execução (`app/static/img/logo_tema_escuro.png` e `app/static/img/logo_tema_claro.png`);
- [x] Arquivo `.gitignore` configurado;
- [x] Arquivo de contexto `AGENTS.md` criado com caminhos estritamente relativos;
- [x] Arquivos vivos `docs/PLANO.md`, `docs/STATUS.md` e `docs/ERROS.md` criados.

---

### Fase 2 — Banco de Dados, Schema e Migrations Versionadas
- [x] Implementar conexão robusta com MySQL em `database/migrate.py` usando credenciais de `config/config.py`;
- [x] Criar migration `001_create_initial_tables.sql` com as 8 tabelas do FSD (`usuarios`, `contas`, `categorias`, `lancamentos_recorrentes`, `lancamentos`, `logs_erros`, `logs_seguranca`, `migrations_controle`);
- [x] Criar migration `002_create_indexes.sql` com todos os índices de desempenho previstos no FSD;
- [x] Validar execução idempotente de migração via CLI local (`python database/migrate.py`).

---

### Fase 3 — Camada de Modelos (ORM) e Mecanismo de Logs Estruturados
- [x] Configurar extensão Flask-SQLAlchemy na App Factory (`app/__init__.py`);
- [x] Implementar models em `app/models/` (`usuario.py`, `conta.py`, `categoria.py`, `lancamento.py`, `lancamento_recorrente.py`, `log_erro.py`, `log_seguranca.py`);
- [x] Implementar capturador global de erros com gravação primária em `logs_erros` e contingência automática em `logs/error.log`;
- [x] Criar suíte de testes automatizados com 100% de aprovação (`tests/test_fase3_models_logs.py`).

---

### Fase 4 — Autenticação, Sessão, Google OAuth e Proteção de Rotas
- [x] Configurar gerenciamento de sessão seguro via cookies HTTP-only, SameSite=Lax e tempo persistente;
- [x] Implementar endpoints `/api/auth/*` no `auth_controller.py` (cadastro com provisionamento canônico das 10 categorias e da carteira inicial padrão "Carteira", login tradicional com hash forte, logout com destruição de sessão, recuperação de senha com fallback de console/log, redefinição com token de 60 min, consulta de sessão ativa e defesa contra força bruta com 5 falhas em 15 min bloqueando por 15 min via `logs_seguranca`);
- [x] Implementar integração Google OAuth 2.0 (rotas `/api/auth/google` e `/api/auth/google/callback` com provisionamento atômico no primeiro acesso e tratamento de cancelamento);
- [x] Implementar decorador `@login_required` com retorno JSON 401 para requisições de API e redirecionamento web, além da função de salvaguarda `validar_posse` contra IDOR;
- [x] Criar suíte de testes automatizados completa com 100% de aprovação (`tests/test_fase4_auth.py`).

---

### Fase 5 — Shell Base da Interface (Design Obsidian, CSS, Meta CSRF e Casca React)
- [x] Criar `app/templates/index.html` com injeção do token CSRF (`<meta name="csrf-token" content="{{ csrf_token() }}">`) e montagem do React (`div#root`);
- [x] Implementar `app/static/css/style.css` fiel ao `docs/DESIGN.md`: paleta zinc profunda (`#09090b`, `#0c0c0f`, `#18181b`, `#27272a`), acentos em violeta suave (`#a78bfa`), verde esmeralda (`#34d399`), vermelho de erro (`#ef4444`), tipografia Geist e estilos completos para tema claro invertido;
- [x] Disponibilizar scripts locais de React, ReactDOM e Babel Standalone em `app/static/js/vendor/` sem necessidade de runtime ou build via Node.js/npm;
- [x] Implementar cliente HTTP padronizado (`app/static/js/api.js`) com leitura da meta tag e envio transparente do cabeçalho `X-CSRFToken` em requisições de mutação (`POST`, `PUT`, `PATCH`, `DELETE`);
- [x] Construir a aplicação React inicial (`app/static/js/app.js`) com componentes completos de Login, Cadastro, Recuperação de Senha, Redefinição de Senha, Shell Autenticado inicial e alternador de tema com sincronização dinâmica das logotipos (`logo_tema_escuro.png` e `logo_tema_claro.png`);
- [x] Calibrar dimensionamento e respiro da logomarca: 25% a 30% da viewheight (`26vh`) nas telas de autenticação e proporcional com respiro interno e centralização na barra lateral (`.sidebar`) de 260px;
- [x] Criar suíte de testes automatizados com 100% de aprovação (`tests/test_fase5_interface.py`).


---

### Fase 6 — Módulo de Contas e Carteiras
- [x] Implementar `app/controllers/contas_controller.py` com endpoints `/api/contas/*` (listagem, criação, edição, arquivamento, reativação e exclusão);
- [x] Implementar cálculo de saldo contábil em tempo real conforme fórmula do FSD;
- [x] Implementar regras de arquivamento, reativação e bloqueio de exclusão física se houver movimentações vinculadas (ativas ou soft-deletadas);
- [x] Construir componentes React de gestão de contas (`TelaContas`, `Modal`, cards com badges e saldo consolidado);
- [x] Implementar suíte de testes unitários automatizados com 100% de aprovação (`tests/test_fase6_contas.py`).

---

### Fase 7 — Módulo de Categorias e Orçamentos
- [x] Implementar `app/controllers/categorias_controller.py` com endpoints `/api/categorias/*` (listagem, criação, edição, arquivamento, reativação, exclusão e reatribuição atômica);
- [x] Implementar cálculo de consumo orçamentário em tempo real para categorias de despesas com teto;
- [x] Implementar modal e fluxo atômico de reatribuição em lote ao tentar excluir categorias com histórico (migrando lançamentos ativos, soft-deletados e fixos recorrentes);
- [x] Construir componentes React (`TelaCategorias`, abas Despesas/Receitas, badges, barras de progresso orçamentário com alerta visual e modal de reatribuição);
- [x] Criar suíte de testes unitários e de integração automatizados com 100% de aprovação (`tests/test_fase7_categorias.py`).

---

### Fase 8 — Módulo de Lançamentos
- [x] Implementar `app/controllers/lancamentos_controller.py` com endpoints `/api/lancamentos/*` (listagem, filtros combinados, criação, transferência, edição, alternância de status e soft delete);
- [x] Implementar operações de receitas, despesas e transferências entre contas (com validações de isolamento por `usuario_id`, preenchimento automático de vencimento/status em transferências e alerta de saldo insuficiente);
- [x] Implementar exclusão lógica via soft delete (`deleted_at`) e recálculo dinâmico de saldos contábeis;
- [x] Construir componentes React de listagem, navegação de período mensal, filtros rápidos, busca instantânea, badges de status e formulário modal com abas [Despesa | Receita | Transferência] e stepper de R$ 1,00;
- [x] Criar suíte de testes unitários e de integração automatizados com 100% de aprovação (`tests/test_fase8_lancamentos.py`).

---

### Fase 9 — Módulo de Lançamentos Recorrentes
- [x] Implementar `app/controllers/recorrentes_controller.py` com endpoints `/api/recorrentes/*` (listagem, cadastro, edição, toggle ativo/pausado, exclusão e sincronização);
- [x] Implementar serviço transparente de verificação e geração de lançamentos de virada de mês (`app/services/recorrentes_service.py`), integrado ao `GET /api/lancamentos`;
- [x] Tratar ajuste automático de dia de vencimento em meses mais curtos (dia 31 ajustado para último dia válido do mês);
- [x] Construir componentes React para gerenciamento de fixos (`TelaRecorrentes`, cards Obsidian, resumo com total de despesas e receitas fixas, modal com abas, stepper monetário de R$ 1,00 e modal de exclusão);
- [x] Criar suíte de testes unitários e de integração automatizados com 100% de aprovação (`tests/test_fase9_recorrentes.py`).

---

### Fase 10 — Módulo do Painel Principal (Dashboard)
- [ ] Implementar `app/controllers/dashboard_controller.py` com consolidação de métricas mensais;
- [ ] Construir componentes React do Dashboard (cards de saldo, gráfico monocromático de despesas e bloco de alertas com botão rápido de quitação);
- [ ] Adicionar navegação histórica livre entre períodos mensais.

---

### Fase 11 — Módulo de Configurações, Perfil e Alternância de Tema
- [ ] Implementar `app/controllers/configuracoes_controller.py`;
- [ ] Implementar alternância de tema no frontend e persistência no banco e `localStorage`;
- [ ] Sincronizar alternância das imagens dos logotipos (`logo_tema_escuro.png` e `logo_tema_claro.png`).

---

### Fase 12 — Revisão de Segurança, Testes Locais e Preparação para Deploy
- [ ] Executar testes de isolamento de dados (prevenção contra IDOR / HTTP 403);
- [ ] Testar bloqueio de força bruta de login;
- [ ] Validar contingência de logs desconectando o MySQL temporariamente;
- [ ] Validar conformidade de todos os 25 critérios de aceitação do FSD;
- [ ] Documentar procedimento de deploy no PythonAnywhere.
