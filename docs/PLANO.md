# Plano de Construção — FinançasSimples

Este documento define as fases incrementais para a construção completa do sistema **FinançasSimples**, em estrita conformidade com a especificação funcional (`docs/FSD.md`) e com o guia de diretrizes visuais (`docs/DESIGN.md`).

---

## Visão Geral das Fases

* **Fase 1:** Infraestrutura e Base do Projeto *(Concluída nesta etapa de preparação)*
* **Fase 2:** Banco de Dados, Schema e Migrations Versionadas
* **Fase 3:** Camada de Modelos (ORM) e Mecanismo de Logs Estruturados
* **Fase 4:** Autenticação, Sessão, Google OAuth e Proteção de Rotas
* **Fase 5:** Shell Base da Interface (Design Obsidian, CSS, Meta CSRF e Casca React)
* **Fase 6:** Módulo de Contas e Carteiras
* **Fase 7:** Módulo de Categorias e Orçamentos (Provisionamento Canônico e Reatribuição em Lote)
* **Fase 8:** Módulo de Lançamentos (Receitas, Despesas, Transferências e Soft Delete)
* **Fase 9:** Módulo de Lançamentos Recorrentes (Automação de Fixos e Sincronização)
* **Fase 10:** Módulo do Painel Principal (Dashboard, Gráficos Monocromáticos e Alertas)
* **Fase 11:** Módulo de Configurações, Perfil e Alternância de Tema (Claro / Escuro)
* **Fase 12:** Revisão de Segurança, Testes Locais, Validação Final e Preparação para Deploy

---

## Fase 1 — Infraestrutura e Base do Projeto

* **Objetivo:** Estabelecer a estrutura inicial de diretórios, arquivos de inicialização, dependências, arquivos de configuração em código Python, proteções de servidor e arquivos vivos de acompanhamento.
* **Checklist de tarefas:**
  - [x] Criar estrutura de pastas do projeto (`app/`, `config/`, `database/`, `logs/`, etc.);
  - [x] Definir dependências no `requirements.txt` (Flask, Flask-SQLAlchemy, PyMySQL, Werkzeug, Flask-Mail, google-auth, etc.);
  - [x] Criar arquivo de configuração em código Python `config/config.py` e modelo `config/config.example.py` (proibido o uso de `.env`);
  - [x] Criar Application Factory base em `app/__init__.py`;
  - [x] Criar pontos de entrada da aplicação: `run.py` (desenvolvimento local) e `wsgi.py` (produção PythonAnywhere);
  - [x] Criar regras de proteção para servidores Apache via `.htaccess` (bloqueando arquivos `.py`, `.sql`, `.log` e pastas sensíveis);
  - [x] Criar pasta de contingência de logs (`logs/`) com arquivo inicial `logs/error.log` e `.gitkeep`;
  - [x] Criar script estrutural do executor de migrações `database/migrate.py`;
  - [x] Copiar insumos de tempo de execução identificados em `docs/INSUMOS.md` (`logo_tema_escuro.png` e `logo_tema_claro.png`) para `app/static/img/`;
  - [x] Configurar `.gitignore` para ignorar ambientes virtuais, caches e arquivos de log;
  - [x] Criar arquivos vivos `docs/STATUS.md` e `docs/ERROS.md`;
  - [x] Criar arquivo de contexto `AGENTS.md` com caminhos estritamente relativos.
* **Critérios de pronto:** Estrutura criada e verificável, sem erros de sintaxe, arquivos de entrada funcionais e arquivos vivos atualizados.
* **Arquivos e pastas alterados:** Raiz do projeto, `app/`, `config/`, `database/`, `logs/`, `docs/`.
* **Dependências:** Nenhuma.

---

## Fase 2 — Banco de Dados, Schema e Migrations Versionadas

* **Objetivo:** Implementar o mecanismo de migrações versionadas via CLI (`database/migrate.py`) e criar o schema relacional inicial no MySQL com todas as tabelas, foreign keys, constraints únicas e índices de otimização descritos no FSD.
* **Checklist de tarefas:**
  - [ ] Implementar conexão robusta com MySQL em `database/migrate.py` utilizando credenciais de `config/config.py`;
  - [ ] Criar migration `001_create_initial_tables.sql` com as tabelas:
    - `usuarios` (com constraints `uk_usuarios_email` e `uk_usuarios_google_id`);
    - `contas` (com constraint `uk_contas_usuario_nome` e FK para `usuarios`);
    - `categorias` (com constraint `uk_categorias_usuario_nome_tipo` e FK para `usuarios`);
    - `lancamentos_recorrentes` (com FKs para `usuarios`, `categorias` e `contas`);
    - `lancamentos` (com FKs para `usuarios`, `categorias`, `contas`, `conta_destino_id` e `recorrentes`, além de `deleted_at`);
    - `logs_erros` (com FK opcional para `usuarios`);
    - `logs_seguranca` (com FK opcional para `usuarios`);
    - `migrations_controle` (para controle de histórico de migrações aplicadas);
  - [ ] Criar migration `002_create_indexes.sql` com todos os 8 índices de desempenho definidos na Seção 11.2 do FSD;
  - [ ] Testar a execução idempotente de `python database/migrate.py` no terminal.
* **Critérios de pronto:** Script de migração executa com sucesso no MySQL, cria todas as tabelas e índices previstos, registra a execução em `migrations_controle` e não duplica execuções subsequentes.
* **Arquivos e pastas alterados:** `database/migrate.py`, `database/migrations/`.
* **Dependências:** Fase 1 concluída e serviço MySQL em execução.

---

## Fase 3 — Camada de Modelos (ORM) e Mecanismo de Logs Estruturados

* **Objetivo:** Construir as classes de modelo SQLAlchemy que representam as tabelas do banco de dados, encapsulam regras de persistência por usuário e implementar o sistema de logging com contingência automática em arquivo.
* **Checklist de tarefas:**
  - [ ] Configurar extensão Flask-SQLAlchemy na Application Factory (`app/__init__.py`);
  - [ ] Implementar `app/models/usuario.py` (métodos de senha, propriedades de autenticação);
  - [ ] Implementar `app/models/conta.py` (métodos de consulta de saldo e filtros de status ativo/arquivado);
  - [ ] Implementar `app/models/categoria.py` (validações de unicidade por tipo e regras de teto);
  - [ ] Implementar `app/models/lancamento.py` (regras de datas, tipos de movimentação e filtro padrão `deleted_at IS NULL`);
  - [ ] Implementar `app/models/lancamento_recorrente.py` (campos de ciclo mensal e flag ativo);
  - [ ] Implementar `app/models/log_erro.py` e `app/models/log_seguranca.py`;
  - [ ] Configurar mecanismo global de tratamento de exceções no Flask com fallback para `logs/error.log` em caso de falha de banco.
* **Critérios de pronto:** Modelos devidamente mapeados com relacionamentos bidirecionais e tratamento de erros com contingência em arquivo validado.
* **Arquivos e pastas alterados:** `app/models/`, `app/__init__.py`.
* **Dependências:** Fase 2 concluída.

---

## Fase 4 — Autenticação, Sessão, Google OAuth e Proteção de Rotas

* **Objetivo:** Implementar o fluxo completo de autenticação híbrida (e-mail/senha e Google OAuth), emissão de cookies de sessão seguros, recuperação de senha com fallback SMTP e controle de acesso estrito com `@login_required`.
* **Checklist de tarefas:**
  - [ ] Configurar Flask-Login ou gerenciamento seguro de sessões com cookies HTTP-only, SameSite=Lax;
  - [ ] Implementar `app/controllers/auth_controller.py`:
    - Rota `POST /api/auth/cadastro` com validação de senha (mínimo 8 caracteres), unicidade de e-mail e provisionamento automático da lista canônica de 10 categorias padrão e da carteira inicial padrão (*"Carteira"* com saldo R$ 0,00);
    - Rota `POST /api/auth/login` com verificação de hash forte (`werkzeug.security`) e proteção contra força bruta (bloqueio após 5 tentativas por 15 minutos e registro em `logs_seguranca`);
    - Rota `POST /api/auth/logout` para destruição de sessão;
    - Rota `POST /api/auth/recuperar-senha` (geração de token de 60 min, despacho por SMTP ou fallback para log/console em desenvolvimento local);
    - Rota `POST /api/auth/redefinir-senha` para validação de token e atualização de senha;
    - Rotas de fluxo Google OAuth 2.0 (`GET /api/auth/google` e `GET /api/auth/google/callback`) com provisionamento automático no primeiro acesso;
    - Rota `GET /api/auth/sessao` para verificação de usuário ativo;
  - [ ] Implementar decorador `@login_required` com retorno JSON 401 para API e redirecionamento para web;
  - [ ] Assegurar bloqueio de IDOR e isolamento absoluto por `usuario_id`.
* **Critérios de pronto:** Cadastro, login tradicional, login Google, recuperação e proteção de endpoints autenticados operando perfeitamente.
* **Arquivos e pastas alterados:** `app/controllers/auth_controller.py`, `app/__init__.py`, `config/config.py`.
* **Dependências:** Fase 3 concluída.

---

## Fase 5 — Shell Base da Interface (Design Obsidian, CSS, Meta CSRF e Casca React)

* **Objetivo:** Construir o template base da aplicação e a estrutura de estilos CSS de alto contraste baseada no `docs/DESIGN.md` (Obsidian), integrando a casca React e o cliente HTTP padronizado com token CSRF.
* **Checklist de tarefas:**
  - [ ] Criar template `app/templates/index.html` com injeção da meta tag `<meta name="csrf-token" content="{{ csrf_token() }}">`, links para fontes Geist e montagem da `div#root`;
  - [ ] Implementar `app/static/css/style.css` com todas as diretrizes do `docs/DESIGN.md`:
    - Fundo near-black (`#09090b`), superfícies zinc (`#0c0c0f` a `#27272a`), bordas finas `1px solid #27272a`;
    - Primário violeta suave (`#a78bfa`), esmeralda (`#34d399`) para sucessos, vermelho (`#ef4444`) para erros;
    - Tipografia Geist com letter-spacing refinado;
    - Modificador para tema claro invertido mantendo acentos funcionais;
  - [ ] Fornecer scripts locais de React e ReactDOM em `app/static/js/vendor/` sem dependência de build Node.js;
  - [ ] Criar cliente HTTP padronizado (`api.js` ou helper em `app.js`) que lê o CSRF token e anexa `X-CSRFToken` em requisições `POST`, `PUT`, `PATCH`, `DELETE`;
  - [ ] Estruturar roteamento frontend e telas públicas de Login, Cadastro e Recuperação de Senha.
* **Critérios de pronto:** Telas de autenticação renderizadas com visual Obsidian de alto contraste, alternância de tema funcional e submissões com token CSRF funcionando.
* **Arquivos e pastas alterados:** `app/templates/index.html`, `app/static/css/style.css`, `app/static/js/`.
* **Dependências:** Fase 4 concluída.

---

## Fase 6 — Módulo de Contas e Carteiras

* **Objetivo:** Implementar a gestão completa de contas e carteiras financeiras com cálculo de saldos em tempo real, proteção contra exclusão com histórico e fluxo de arquivamento.
* **Checklist de tarefas:**
  - [ ] Criar `app/controllers/contas_controller.py`:
    - `GET /api/contas` (listagem de contas do usuário logado com saldo em tempo real calculado por fórmula contábil);
    - `POST /api/contas` (criação com validação de unicidade de nome e saldo inicial);
    - `PUT /api/contas/<id>` (edição de nome da conta);
    - `PATCH /api/contas/<id>/arquivar` e `PATCH /api/contas/<id>/reativar`;
    - `DELETE /api/contas/<id>` (bloqueada se houver movimentações vinculadas ativas ou soft-deletadas; permitida apenas sem histórico);
  - [ ] Construir componentes de interface React para Contas (grade de cartões, exibição de saldo total consolidado, badges ativa/arquivada e modal de criação/edição).
* **Critérios de pronto:** Cadastro, edição, arquivamento, reativação e exclusão protegida de contas funcionando com recálculo imediato de saldos.
* **Arquivos e pastas alterados:** `app/controllers/contas_controller.py`, `app/static/js/`.
* **Dependências:** Fase 5 concluída.

---

## Fase 7 — Módulo de Categorias e Orçamentos

* **Objetivo:** Implementar o gerenciamento de categorias de receita e despesa, definição de tetos de gastos mensais e o fluxo transacional de reatribuição em lote ao excluir categorias com histórico.
* **Checklist de tarefas:**
  - [ ] Criar `app/controllers/categorias_controller.py`:
    - `GET /api/categorias` (listagem agrupada por tipo, com consumo orçamentário do mês);
    - `POST /api/categorias` (criação com validação de unicidade por usuário e tipo);
    - `PUT /api/categorias/<id>` (edição de nome e teto orçamentário opcional);
    - `PATCH /api/categorias/<id>/arquivar`;
    - `DELETE /api/categorias/<id>` (exclusão direta apenas se contagem de lançamentos for zero);
    - `POST /api/categorias/<id>/reatribuir-excluir` (transação atômica que transfere lançamentos ativos, soft-deletados e modelos recorrentes para a nova categoria antes de excluir a antiga);
  - [ ] Construir componentes de interface React para Categorias (seções de Despesas e Receitas, barras de progresso do teto com alerta > 100% e modal de reatribuição em lote).
* **Critérios de pronto:** Categorias manipuláveis, integridade referencial protegida contra violações de FK e modal de reatribuição operando atomicamente.
* **Arquivos e pastas alterados:** `app/controllers/categorias_controller.py`, `app/static/js/`.
* **Dependências:** Fase 5 e Fase 6 concluídas.

---

## Fase 8 — Módulo de Lançamentos

* **Objetivo:** Implementar o gerenciamento completo de movimentações financeiras (receitas, despesas e transferências entre contas próprias), filtros avançados, busca em tempo real e soft delete.
* **Checklist de tarefas:**
  - [ ] Criar `app/controllers/lancamentos_controller.py`:
    - `GET /api/lancamentos` (filtros por mês/ano, conta, categoria, tipo, status e termo de busca textual);
    - `POST /api/lancamentos` (criação de receita ou despesa validando posse de conta/categoria e datas);
    - `POST /api/lancamentos/transferencia` (criação de transferência entre contas próprias com validação de contas distintas, `data_vencimento = data_competencia` e `status = pago`);
    - `PUT /api/lancamentos/<id>` (edição de campos e ajuste de saldos);
    - `PATCH /api/lancamentos/<id>/pagar` (alternância rápida entre status pendente e pago);
    - `DELETE /api/lancamentos/<id>` (exclusão lógica preenchendo `deleted_at` e revertendo saldo se status era pago);
  - [ ] Construir componentes de interface React para Lançamentos (tabela/cards responsivos, badges de status, modal com abas [Despesa | Receita | Transferência] e busca em tempo real).
* **Critérios de pronto:** CRUD de lançamentos completo, transferências isoladas sem inflar indicadores gerais, soft delete operacional e recálculo dinâmico de saldos.
* **Arquivos e pastas alterados:** `app/controllers/lancamentos_controller.py`, `app/static/js/`.
* **Dependências:** Fase 6 e Fase 7 concluídas.

---

## Fase 9 — Módulo de Lançamentos Recorrentes

* **Objetivo:** Implementar os modelos de movimentações fixas mensais e a rotina transparente de geração automática de lançamentos na virada do ciclo, sincronizada entre Dashboard e listagem.
* **Checklist de tarefas:**
  - [ ] Criar `app/controllers/recorrentes_controller.py`:
    - `GET /api/recorrentes` (listagem de modelos fixos ativos e inativos);
    - `POST /api/recorrentes` (cadastro de modelo informando dia do vencimento 1 a 31);
    - `PUT /api/recorrentes/<id>` (edição dos parâmetros do modelo);
    - `PATCH /api/recorrentes/<id>/toggle` (ativação/desativação rápida);
    - `DELETE /api/recorrentes/<id>` (exclusão do modelo sem apagar lançamentos passados);
  - [ ] Implementar serviço de sincronização automática de recorrências:
    - Executado de forma transparente ao consultar `GET /api/dashboard/resumo` e `GET /api/lancamentos`;
    - Gera lançamentos pendentes para modelos ativos que ainda não foram gerados no mês corrente;
    - Trata meses com menos dias (ajusta dia 31 para último dia válido do mês);
  - [ ] Construir componentes de interface React para Fixos (lista de modelos, toggle de ativo/inativo e modal de cadastro).
* **Critérios de pronto:** Modelos recorrentes cadastráveis e geração automática de lançamentos operando de forma autônoma e sincronizada.
* **Arquivos e pastas alterados:** `app/controllers/recorrentes_controller.py`, `app/services/` ou `app/models/`, `app/static/js/`.
* **Dependências:** Fase 8 concluída.

---

## Fase 10 — Módulo do Painel Principal (Dashboard)

* **Objetivo:** Consolidar os indicadores em tempo real, implementar o gráfico monocromático de despesas por categoria e o bloco de alertas visuais para contas a vencer e vencidas.
* **Checklist de tarefas:**
  - [ ] Criar `app/controllers/dashboard_controller.py`:
    - `GET /api/dashboard/resumo` (parâmetros de mês e ano; cálculo de saldo líquido, total de receitas, total de despesas, agregação por categoria e lista de alertas de vencimento);
  - [ ] Construir componentes de interface React para Dashboard:
    - Barra de navegação de períodos mensais (com setas de avançar/voltar e seletor rápido);
    - Cartões de indicadores (Saldo Líquido com cor verde/vermelha funcional, Receitas e Despesas);
    - Gráfico de barras simples, elegante e monocromático em tons de violeta e zinc;
    - Bloco de alertas com destaque vermelho (`#ef4444`) para atrasos e botão rápido "Marcar como Pago";
    - Botão flutuante "+ Novo Lançamento" com atalho direto ao modal;
    - Skeleton loaders e estados vazios amigáveis.
* **Critérios de pronto:** Dashboard renderiza métricas em milissegundos, recalcula instantaneamente ao alternar meses e dispara automação de recorrências.
* **Arquivos e pastas alterados:** `app/controllers/dashboard_controller.py`, `app/static/js/`.
* **Dependências:** Fase 8 e Fase 9 concluídas.

---

## Fase 11 — Módulo de Configurações, Perfil e Alternância de Tema

* **Objetivo:** Disponibilizar visualização de perfil do usuário e alternador instantâneo entre temas de alto contraste (*High-Contrast Dark* oficial e tema claro correspondente), sincronizando o logotipo dinamicamente.
* **Checklist de tarefas:**
  - [ ] Criar `app/controllers/configuracoes_controller.py`:
    - `GET /api/usuario/perfil` (exibição de nome e e-mail);
    - `PATCH /api/usuario/tema` (persistência da preferência `dark` ou `light` na tabela `usuarios`);
  - [ ] Implementar alternância de tema no frontend com persistência simultânea em `localStorage` e no banco;
  - [ ] Alternar dinamicamente a imagem do logotipo: `logo_tema_escuro.png` (tema escuro) e `logo_tema_claro.png` (tema claro);
  - [ ] Validar conformidade de contraste conforme o `docs/DESIGN.md`.
* **Critérios de pronto:** Tema alternável fluidamente sem quebra de contraste, persistido entre recarregamentos e dispositivos.
* **Arquivos e pastas alterados:** `app/controllers/configuracoes_controller.py`, `app/static/js/`, `app/static/css/style.css`.
* **Dependências:** Fase 5 e Fase 10 concluídas.

---

## Fase 12 — Revisão de Segurança, Testes Locais, Validação Final e Preparação para Deploy

* **Objetivo:** Executar a bateria de testes de validação funcional contra os critérios de aceitação do FSD, conferir as salvaguardas de segurança e consolidar as instruções de deploy no PythonAnywhere.
* **Checklist de tarefas:**
  - [ ] Testar isolamento rigoroso por `usuario_id` em todas as rotas (prevenção contra IDOR / HTTP 403);
  - [ ] Testar bloqueio de força bruta de login com verificação do registro em `logs_seguranca`;
  - [ ] Testar contingência de logs desconectando o MySQL e verificando escrita em `logs/error.log`;
  - [ ] Testar proteção CSRF com requisições mutadoras sem token (deve retornar HTTP 400);
  - [ ] Validar que nenhum item fora de escopo (uploads, conexões bancárias automáticas, moedas estrangeiras, exportações externas) foi adicionado;
  - [ ] Validar responsividade mobile e tablet;
  - [ ] Conferir script `wsgi.py` e documentar passos de deploy no PythonAnywhere;
  - [ ] Validar todos os 25 critérios de aceitação do `docs/FSD.md`.
* **Critérios de pronto:** Todos os testes aprovados, critérios de aceitação 100% cumpridos, sem falhas de segurança e sistema pronto para produção.
* **Arquivos e pastas alterados:** Todos os componentes do projeto e documentação.
* **Dependências:** Fases 1 a 11 concluídas.
