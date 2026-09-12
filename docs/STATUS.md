# Estado Atual do Projeto — FinançasSimples

* **Última atualização:** 2026-09-12 (Conclusão da Fase 2 — Banco de Dados, Schema e Migrations Versionadas)
* **Fase atual:** Fase 2 concluída — Banco de Dados, Schema e Migrations Versionadas
* **Próximo passo recomendado:** Iniciar a Fase 3 (Camada de Modelos (ORM) e Mecanismo de Logs Estruturados)

---

## Status Geral por Fase

| Fase | Descrição | Status |
| :---: | :--- | :---: |
| **Fase 1** | Infraestrutura e Base do Projeto | **Concluída** |
| **Fase 2** | Banco de Dados, Schema e Migrations Versionadas | **Concluída** |
| **Fase 3** | Camada de Modelos (ORM) e Mecanismo de Logs Estruturados | Pendente |
| **Fase 4** | Autenticação, Sessão, Google OAuth e Proteção de Rotas | Pendente |
| **Fase 5** | Shell Base da Interface (Design Obsidian, CSS, Meta CSRF e Casca React) | Pendente |
| **Fase 6** | Módulo de Contas e Carteiras | Pendente |
| **Fase 7** | Módulo de Categorias e Orçamentos (Provisionamento Canônico e Reatribuição) | Pendente |
| **Fase 8** | Módulo de Lançamentos (Receitas, Despesas, Transferências e Soft Delete) | Pendente |
| **Fase 9** | Módulo de Lançamentos Recorrentes (Automação de Fixos e Sincronização) | Pendente |
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
- [ ] Configurar extensão Flask-SQLAlchemy na App Factory;
- [ ] Implementar models em `app/models/` (`usuario.py`, `conta.py`, `categoria.py`, `lancamento.py`, `lancamento_recorrente.py`, `log_erro.py`, `log_seguranca.py`);
- [ ] Implementar capturador global de erros com gravação em `logs_erros` e contingência em `logs/error.log`.

---

### Fase 4 — Autenticação, Sessão, Google OAuth e Proteção de Rotas
- [ ] Configurar gerenciamento de sessão seguro via cookies HTTP-only;
- [ ] Implementar endpoints `/api/auth/*` no `auth_controller.py` (cadastro, login, logout, recuperação de senha com fallback SMTP/console, sessão);
- [ ] Implementar integração Google OAuth 2.0;
- [ ] Implementar decorador `@login_required` e isolamento estrito por `usuario_id`.

---

### Fase 5 — Shell Base da Interface (Design Obsidian, CSS, Meta CSRF e Casca React)
- [ ] Criar `app/templates/index.html` com injeção do token CSRF e montagem do React;
- [ ] Implementar `app/static/css/style.css` com paleta zinc, violeta suave (`#a78bfa`), verde esmeralda (`#34d399`), vermelho (`#ef4444`) e tipografia Geist;
- [ ] Disponibilizar scripts do React e ReactDOM em `app/static/js/vendor/`;
- [ ] Criar cliente HTTP padronizado enviando cabeçalho `X-CSRFToken` nas mutações de estado;
- [ ] Renderizar telas de Login, Cadastro e Recuperação de Senha.

---

### Fase 6 — Módulo de Contas e Carteiras
- [ ] Implementar `app/controllers/contas_controller.py` com endpoints `/api/contas/*`;
- [ ] Implementar cálculo de saldo contábil em tempo real;
- [ ] Implementar regras de arquivamento, reativação e bloqueio de exclusão física se houver movimentações;
- [ ] Construir componentes React de gestão de contas.

---

### Fase 7 — Módulo de Categorias e Orçamentos
- [ ] Implementar `app/controllers/categorias_controller.py` com endpoints `/api/categorias/*`;
- [ ] Implementar provisionamento canônico das 10 categorias padrão para novos usuários;
- [ ] Implementar modal e fluxo atômico de reatribuição em lote ao excluir categorias com histórico;
- [ ] Construir componentes React com barras de consumo orçamentário.

---

### Fase 8 — Módulo de Lançamentos
- [ ] Implementar `app/controllers/lancamentos_controller.py` com endpoints `/api/lancamentos/*`;
- [ ] Implementar operações de receitas, despesas e transferências entre contas;
- [ ] Implementar exclusão lógica via soft delete (`deleted_at`) e recálculo dinâmico de saldos;
- [ ] Construir componentes React de listagem, busca instantânea e formulário modal.

---

### Fase 9 — Módulo de Lançamentos Recorrentes
- [ ] Implementar `app/controllers/recorrentes_controller.py` com endpoints `/api/recorrentes/*`;
- [ ] Implementar serviço transparente de verificação e geração de lançamentos de virada de mês (sincronizado com Dashboard e Lançamentos);
- [ ] Tratar ajuste automático de dia de vencimento em meses mais curtos;
- [ ] Construir componentes React para gerenciamento de fixos.

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
