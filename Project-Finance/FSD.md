# DOCUMENTO DE ESPECIFICAÇÃO FUNCIONAL (FSD)

## 1. Visão Geral

* **Nome do sistema:** FinançasSimples.
* **Objetivo principal:** Proporcionar controle financeiro pessoal simplificado, visual e ágil para o acompanhamento de receitas, despesas, carteiras e transferências, ajudando a organizar a vida financeira de forma prática sem termos contábeis complexos.
* **Resumo do funcionamento:** O sistema atua como um painel unificado que oferece indicadores mensais de saldo, receitas e despesas, gráfico de despesas por categoria, alertas de vencimento e tetos de orçamento, além de gestão completa de lançamentos avulsos e recorrentes, múltiplas carteiras e transferências internas.
* **Público usuário:** Pessoas físicas com uso estritamente individual por painel exclusivo.
* **Contexto de uso:** Aplicação web totalmente responsiva para computadores e dispositivos móveis, com suporte a temas claro e escuro, utilizada diariamente.
* **Observações relevantes para implementação:** Foco em usabilidade mobile, clareza de estados (pago/pendente), isolamento absoluto de dados por usuário e conformidade visual estrita com o guia de design *High-Contrast Dark*.

## 2. Documentos do Projeto para Implementação

* `docs/FSD.md`
* `docs/DESIGN.md`

*(Nota: Este FSD consolida integralmente todas as decisões técnicas e funcionais necessárias para a implementação, tornando desnecessária a consulta a documentos externos de PRD ou decisões técnicas).*

## 3. Stack Definida

* **Linguagem de programação:** Python (Flask no backend) e JavaScript/React (no frontend).
* **Banco de dados:** MySQL.
* **Tecnologias de interface:** HTML, CSS, JavaScript e React, seguindo o guia visual *High-Contrast Dark* (superfícies near-black `#09090b`, primário soft violet `#a78bfa`, escala de cinzas baseada em zinc, separação por bordas `1px solid #27272a`).
* **Bibliotecas ou frameworks:** Flask, Flask-Login (ou gerenciamento de sessão customizado para autenticação), SQLAlchemy (ou driver MySQL compatível), React (integrado via CDN ou build assets).
* **Dependências importantes:** Conector MySQL (`PyMySQL` ou `mysql-connector-python`), biblioteca de criptografia de senha (`bcrypt` ou `werkzeug.security`).
* **Padrão arquitetural:** MVC (Model-View-Controller) adaptado para Python/Flask e React.
* **Restrições técnicas:** Uso exclusivo de Real brasileiro (R$), ausência de anexos/uploads na primeira versão, ausência de exportação de arquivos externos.
* **Observações sobre uso local de bibliotecas:** Bibliotecas de frontend (como React e estilos) podem ser referenciadas via assets locais ou CDNs confiáveis conforme o padrão da stack.

## 4. Ambientes do Projeto

* **Desenvolvimento local:** Ambiente virtual Python (`venv`), servidor Flask embutido (`flask run` ou script de execução local) e banco de dados MySQL rodando via XAMPP.
* **Testes ou homologação:** Ausente nesta primeira versão (validação diretamente em ambiente local antes do deploy).
* **Produção:** Hospedagem em ambiente compatível com Python / Flask, estruturado para deploy em **PythonAnywhere**.
* **Observações sobre deploy:** O processo de publicação e configuração do WSGI no PythonAnywhere será abordado em etapa específica pós-desenvolvimento.

## 5. Arquitetura do Sistema

* **Referência principal de diretórios:** `[Diretório do Projeto - Repositório]`
* *(Explicação: Este diretório representa a pasta do projeto versionada no repositório. Em servidores locais como XAMPP, pode ficar em `htdocs/financas-simples/`; em hospedagens como PythonAnywhere, fica na estrutura de diretórios privada/pública da aplicação).*


* **Aplicação do padrão MVC:**
* **Models:** Responsáveis pela persistência de dados, mapeamento relacional e regras de negócio vinculadas aos dados, comunicando-se diretamente com o MySQL. Localizados na pasta `app/models/`.
* **Controllers (Rotas / Blueprints):** Responsáveis por receber as requisições HTTP do usuário, acionar os models ou serviços de negócio, processar regras e retornar as respostas em JSON ou renderizar views. Localizados na pasta `app/controllers/` ou `app/routes/`.
* **Views:** Responsáveis pela interface de usuário reativa construída em React e templates HTML base, estruturadas para consumir os dados fornecidos pelo backend. Localizadas na pasta `app/views/` ou `app/static/` / `app/templates/`.


* **Organização de arquivos auxiliares, configurações e assets:**
* Configurações globais e de conexão em arquivo de código puro (`config/config.py`).
* Arquivos estáticos (CSS, JS, imagens) em `app/static/`.
* Migrations de banco de dados em `database/migrations/`.
* Logs em `logs/`.


* **Sugestão de Estrutura de Diretórios:**
```text
[Diretório do Projeto - Repositório]/
├── app/
│   ├── __init__.py
│   ├── controllers/      # Controladores / Rotas Flask
│   ├── models/           # Modelos de dados / ORM
│   ├── views/            # Templates HTML / Componentes React
│   └── static/           # Assets (CSS, JS, imagens)
├── config/
│   └── config.py         # Arquivo de configuração em código (sem .env)
├── database/
│   └── migrations/       # Scripts versionados de migração do banco de dados
├── logs/                 # Armazenamento de logs em arquivo (protegido)
├── requirements.txt      # Dependências Python
└── wsgi.py               # Arquivo de entrada para o servidor de produção / WSGI

```


* **Proteção de pastas internas:** Pastas como `config/`, `app/`, `database/` e `logs/` não devem ser acessadas diretamente pelo navegador. A aplicação centraliza o fluxo de entrada (ex: `wsgi.py` ou arquivo principal do Flask) e protege diretórios sensíveis através de configurações do servidor web (como regras em `.htaccess` em ambientes Apache, configurações de WSGI ou restrições nativas do Flask/PythonAnywhere).

## 6. Escopo Funcional da Primeira Versão

* **Módulo de Autenticação e Acesso:**
* *Objetivo:* Permitir cadastro, login e recuperação de acesso de forma segura.
* *Ações:* Login por e-mail/senha, cadastro de nova conta, recuperação de senha via link por e-mail, login rápido via Google OAuth.


* **Painel Principal (Dashboard):**
* *Objetivo:* Oferecer visão macro e imediata da saúde financeira do período.
* *Ações:* Exibição de saldo líquido do mês, total de receitas, total de despesas, gráfico de barras monocromático de despesas por categoria, e bloco de destaque de vencimentos próximos ou atrasados.


* **Módulo de Lançamentos:**
* *Objetivo:* Gerenciar todas as entradas, saídas e transferências financeiras.
* *Ações:* Cadastrar, editar e excluir movimentações (receitas, despesas, transferências entre contas próprias); filtrar por período (mês/ano), conta e status (pago/pendente); buscar por texto.


* **Módulo de Lançamentos Recorrentes:**
* *Objetivo:* Automatizar o registro de despesas e receitas fixas mensais.
* *Ações:* Configuração de itens recorrentes que são gerados automaticamente pelo sistema no início de cada novo ciclo mensal.


* **Módulo de Contas / Carteiras:**
* *Objetivo:* Controlar o saldo em diferentes locais de armazenamento (conta corrente, dinheiro, cartão).
* *Ações:* Cadastrar contas com saldo inicial, visualizar saldos atuais, arquivar contas em desuso preservando o histórico.


* **Módulo de Categorias e Orçamentos:**
* *Objetivo:* Classificar movimentações e controlar tetos de gastos.
* *Ações:* Criar, editar, excluir ou arquivar categorias (receita/despesa); definir teto de orçamento mensal opcional; reatribuir registros em lote ou bloquear exclusão em caso de histórico vinculado; emitir alertas visuais de estouro de orçamento.


* **Configurações Visuais:**
* *Objetivo:* Garantir conforto visual e personalização básica.
* *Ações:* Alternância manual entre tema claro e escuro com persistência da preferência do usuário.



## 7. Fora de Escopo

* Anexo de arquivos, fotos de recibos, comprovantes ou notas fiscais (PDF/imagens).
* Importação automática de extratos bancários (arquivos OFX ou Open Finance).
* Gestão de investimentos (renda fixa, ações, criptomoedas).
* Divisão de contas em grupo ou viagens compartilhadas.
* Exportação de relatórios em arquivos externos (CSV, Excel ou PDF).
* Suporte a múltiplas moedas (operação restrita exclusivamente ao Real brasileiro - R$).
* Perfis múltiplos ou contas compartilhadas no mesmo painel (uso estritamente individual).

## 8. Perfis de Usuário e Permissões

* **Usuário Pessoal:**
* *Descrição:* Pessoa física que gerencia o próprio orçamento e deseja praticidade no controle de finanças diárias.
* *Permissões:* Acesso total e exclusivo ao seu próprio painel de dados financeiros (contas, categorias, lançamentos, configurações).
* *Restrições e Ações Bloqueadas:* Impossibilidade absoluta de acessar dados de outros usuários ou modificar configurações globais do sistema.
* *Matriz de Acesso:* Isolamento estrito por ID de usuário em todas as consultas e operações do banco de dados.



## 9. Recursos Estruturais do Sistema

* **Autenticação:**
* *Objetivo:* Garantir acesso seguro e restrito.
* *Comportamento:* Suporte a e-mail/senha com hash seguro (bcrypt/Werkzeug) e integração OAuth com a conta Google.


* **RBAC (Controle de Acesso Baseado em Papéis / Isolamento):**
* *Objetivo:* Proteger a privacidade dos dados financeiros.
* *Comportamento:* Validação em backend de que qualquer requisição afeta apenas registros pertencentes ao usuário autenticado na sessão.


* **Auditoria:**
* *Objetivo:* Rastreabilidade básica de criação e modificação de registros.
* *Comportamento:* Campos de controle temporal (`created_at`, `updated_at`) em entidades principais.


* **Soft Delete:**
* *Objetivo:* Preservar integridade histórica sem exclusão destrutiva direta.
* *Comportamento:* Inativação lógica (`deleted_at` ou campo booleano `ativo`/`arquivado`) em cadastros de contas, categorias e lançamentos.


* **Log de Erros:**
* *Objetivo:* Diagnóstico centralizado de falhas na aplicação Flask.
* *Comportamento:* Registro de exceções em banco de dados e mecanismo de contingência em arquivo quando o banco estiver indisponível.


* **Configurações Globais:**
* *Objetivo:* Gestão de preferências de perfil e tema visual.
* *Comportamento:* Armazenamento das preferências do usuário e parâmetros técnicos de sistema em arquivo de código dedicado.



## 10. Entidades do Sistema

* **Usuários:**
* *Finalidade:* Autenticação e isolamento do painel financeiro.
* *Informações:* ID, nome, e-mail, senha_hash, provedor_auth (local/google), created_at, updated_at.


* **Contas / Carteiras:**
* *Finalidade:* Representar locais de armazenamento de saldo (conta corrente, dinheiro, etc.).
* *Informações:* ID, usuario_id, nome, saldo_inicial, status (ativo/arquivado), created_at, updated_at.


* **Categorias:**
* *Finalidade:* Classificar receitas e despesas e definir tetos de orçamento.
* *Informações:* ID, usuario_id, nome, tipo (receita/despesa), teto_orcamento, status (ativo/arquivado), created_at, updated_at.


* **Lançamentos (Movimentações):**
* *Finalidade:* Registrar entradas, saídas e transferências financeiras.
* *Informações:* ID, usuario_id, tipo (receita/despesa/transferencia), valor, data_competencia, data_vencimento, descricao, categoria_id, conta_id, conta_destino_id (para transferências), forma_pagamento, status (pago/pendente), observacao, recorrente_id, created_at, updated_at, deleted_at.


* **Lançamentos Recorrentes (Modelos):**
* *Finalidade:* Automatizar a geração de despesas e receitas fixas mensais.
* *Informações:* ID, usuario_id, tipo, valor, descricao, categoria_id, conta_id, dia_vencimento, ativo, created_at, updated_at.



## 11. Modelo de Dados Proposto

* **Tabelas e Estrutura Relacional (MySQL):**
* `usuarios`: `id` (PK, INT, Auto Increment), `nome` (VARCHAR), `email` (VARCHAR, Unique), `senha_hash` (VARCHAR, Nullable para Google), `google_id` (VARCHAR, Nullable), `created_at`, `updated_at`.
* `contas`: `id` (PK, INT), `usuario_id` (FK para `usuarios`), `nome` (VARCHAR), `saldo_inicial` (DECIMAL(12,2)), `status` (ENUM('ativo', 'arquivado')), `created_at`, `updated_at`.
* `categorias`: `id` (PK, INT), `usuario_id` (FK para `usuarios`), `nome` (VARCHAR), `tipo` (ENUM('receita', 'despesa')), `teto_orcamento` (DECIMAL(12,2), Nullable), `status` (ENUM('ativo', 'arquivado')), `created_at`, `updated_at`.
* `lancamentos_recorrentes`: `id` (PK, INT), `usuario_id` (FK para `usuarios`), `tipo` (ENUM('receita', 'despesa')), `valor` (DECIMAL(12,2)), `descricao` (VARCHAR), `categoria_id` (FK para `categorias`), `conta_id` (FK para `contas`), `dia_vencimento` (INT), `ativo` (BOOLEAN), `created_at`, `updated_at`.
* `lancamentos`: `id` (PK, INT), `usuario_id` (FK para `usuarios`), `tipo` (ENUM('receita', 'despesa', 'transferencia')), `valor` (DECIMAL(12,2)), `data_competencia` (DATE), `data_vencimento` (DATE), `descricao` (VARCHAR), `categoria_id` (FK para `categorias`, Nullable em transferência), `conta_id` (FK para `contas`), `conta_destino_id` (FK para `contas`, Nullable), `forma_pagamento` (VARCHAR), `status` (ENUM('pago', 'pendente')), `observacao` (TEXT, Nullable), `recorrente_id` (FK para `lancamentos_recorrentes`, Nullable), `created_at`, `updated_at`, `deleted_at` (DATETIME, Nullable).
* `logs_erros`: `id` (PK, INT), `usuario_id` (FK, Nullable), `nivel` (VARCHAR), `mensagem` (TEXT), `stack_trace` (TEXT, Nullable), `created_at`.


* **Índices de Desempenho:**
* Índice composto em `lancamentos (`usuario_id`, `data_competencia`)` para otimizar filtros de período no dashboard.
* Índice em `lancamentos (`usuario_id`, `conta_id`)` e `lancamentos (`usuario_id`, `categoria_id`)`.
* Índice em `lancamentos (`usuario_id`, `status`, `data_vencimento`)` para alertas de vencimento.


* **Estratégia de Migrations:**
* O projeto utilizará uma arquitetura de migrations versionadas (compatível com Flask-Migrate / Alembic ou scripts SQL versionados) localizadas na pasta `database/migrations/`.
* As migrations criam e atualizam tabelas, campos, chaves estrangeiras, constraints e índices de forma controlada, evitando intervenção manual no phpMyAdmin.
* Um mecanismo de controle (tabela `alembic_version` ou controle interno de scripts executados) evitará a execução duplicada.
* A pasta de migrations estará protegida contra acesso direto via navegador. A execução das migrations ocorrerá exclusivamente via linha de comando no ambiente de desenvolvimento ou procedimento administrativo restrito.



## 12. Módulos e Telas

* **Tela de Login / Cadastro (`/login`, `/cadastro`):**
* *Objetivo:* Autenticação e registro de novos usuários.
* *Elementos:* Formulários de e-mail/senha, botão de login com Google, link de recuperação de senha, mensagens de feedback de erro/sucesso.


* **Dashboard / Painel Principal (`/dashboard`):**
* *Objetivo:* Visão consolidada do mês.
* *Elementos:* Seletor de mês/ano, cartões de indicadores (Saldo Líquido, Receitas Totais, Despesas Totais), gráfico de despesas por categoria, bloco de alertas de contas vencidas ou próximas do vencimento.


* **Módulo de Lançamentos (`/lancamentos`):**
* *Objetivo:* Gestão detalhada de movimentações.
* *Elementos:* Tabela/lista de lançamentos com status diferenciado (pago/pendente), filtros por período, conta e status, barra de busca textual, botão de "Novo Lançamento" (abre modal/formulário para avulso e transferência).


* **Módulo de Contas (`/contas`):**
* *Objetivo:* Gerenciar carteiras e saldos iniciais.
* *Elementos:* Listagem de contas com saldos calculados, botão de nova conta, opção de arquivar conta.


* **Módulo de Categorias e Orçamentos (`/categorias`):**
* *Objetivo:* Organizar categorias e tetos de gastos.
* *Elementos:* Listagem de categorias agrupadas por tipo (receita/despesa), definição de teto mensal, modal de reatribuição em lote caso haja tentativa de exclusão com histórico vinculado.


* **Configurações Visuais e Perfil (`/configuracoes`):**
* *Objetivo:* Ajustes de preferência de tema (claro/escuro).
* *Elementos:* Botão de alternância de tema em conformidade com o guia visual *High-Contrast Dark*.



## 13. Fluxos Funcionais

* **Fluxo de Registro de Nova Movimentação:**
1. Usuário acessa o Dashboard ou a listagem de Lançamentos e clica em "Adicionar Lançamento".
2. Sistema exibe o formulário.
3. Usuário preenche tipo, valor, data, descrição, categoria, conta e status.
4. Sistema valida o preenchimento dos campos obrigatórios no backend.
5. Sistema grava o lançamento e atualiza em tempo real o saldo da conta e os indicadores do dashboard.


* **Fluxo de Transferência entre Contas:**
1. Usuário seleciona a opção de transferência.
2. Informa valor, data, conta de origem e conta de destino.
3. Sistema valida se a conta de origem possui saldo suficiente ou se a operação é permitida.
4. Sistema desconta o valor da conta de origem e adiciona na conta de destino, preservando o total de receitas e despesas do período.


* **Fluxo de Geração Automática de Recorrentes:**
1. Na virada do mês, uma rotina interna acionada no primeiro acesso do usuário ou via script verifica os modelos de lançamentos recorrentes ativos.
2. O sistema gera automaticamente os lançamentos correspondentes ao novo ciclo com status pendente e data de vencimento prevista.



## 14. Validações e Regras de Negócio

* **Isolamento de Transferências:** Transferências alteram estritamente o saldo individual das carteiras envolvidas, sem impactar o somatório geral de receitas e despesas do mês.
* **Integridade e Exclusão:** O sistema bloqueia a exclusão definitiva de contas ou categorias com lançamentos vinculados, exigindo o arquivamento ou a realocação em lote dos registros para outra categoria.
* **Monitoramento de Orçamento:** O sistema compara o total gasto em uma categoria com o teto definido e exibe alerta visual caso o limite seja ultrapassado.
* **Destaque de Atrasos:** Lançamentos com status pendente e data de vencimento anterior à data atual recebem destaque visual automático (alerta de atraso).
* **Formatação Monetária:** Todos os valores monetários seguem estritamente o padrão do Real brasileiro (R$).

## 15. Autenticação e Sessão

* **Tipo de Autenticação:** Híbrida (E-mail/senha com hash seguro via Werkzeug/Bcrypt e Google OAuth).
* **Fluxo de Login e Sessão:** Gerenciado por Flask-Login ou sessões seguras baseadas em cookies HTTP-only. A sessão permanece ativa até o logout manual do usuário.
* **Proteção de Rotas:** Todas as rotas de aplicação (exceto login, cadastro e recursos públicos estáticos) exigem autenticação ativa. Usuários não autenticados são redirecionados para a tela de login.

## 16. Controle de Acesso

* **Papéis:** Apenas o perfil `Usuário Pessoal`.
* **Isolamento de Dados:** Filtro automático por `usuario_id` em todas as consultas SQL/ORM. Tentativas de acesso a recursos de outro ID de usuário retornam erro 403 (Acesso Negado).

## 17. Auditoria e Histórico

* **Auditoria Básica:** Rastreamento temporal via colunas `created_at` e `updated_at` em todas as tabelas principais.
* **Soft Delete:** Utilização de `deleted_at` para impedir perda acidental de dados e manter consistência relacional.

## 18. Soft Delete e Exclusões

* Registros principais (lançamentos, contas, categorias) que necessitam de remoção utilizam exclusão lógica (`deleted_at` preenchido ou status `arquivado`), garantindo que históricos financeiros passados permaneçam íntegros.

## 19. Logs

### Log de erros

* **Registros:** Exceções não tratadas, falhas de conexão com o banco e erros críticos no Flask.
* **Informações gravadas:** Data/hora, mensagem de erro, stack trace, ID do usuário (quando disponível).
* **Contingência:** Se o banco de dados estiver indisponível, o erro é gravado obrigatoriamente em arquivo de texto na pasta protegida `logs/error.log`.
* **Segurança do Log:** Armazenado fora da raiz pública web, sem acesso direto via URL.

### Log de segurança

* **Registros:** Tentativas de login inválidas, acessos negados, ações suspeitas e tentativas de violação de rotas protegidas.

## 20. Configurações Globais

* **Estratégia de Configuração Técnica:**
* Uso estrito de arquivo de configuração em código Python localizado em `config/config.py` dentro do `[Diretório do Projeto - Repositório]`. **Nenhum arquivo `.env` será utilizado.**
* O arquivo `config/config.py` armazena parâmetros de conexão com o MySQL, credenciais de OAuth, chaves secretas da aplicação e flags de debug.
* *Proteção:* A pasta `config/` e o arquivo `config.py` são protegidos contra acesso direto pelo navegador através da arquitetura de rotas do Flask e configurações do servidor web.



## 21. Uploads, Anexos e Arquivos

* O envio de arquivos, fotos de recibos, comprovantes ou notas fiscais está **formalmente fora do escopo da primeira versão**, conforme estipulado nas decisões técnicas.

## 22. Relatórios, Consultas e Exportações

* Relatórios, consultas avançadas e listagens são integralmente interativos e exibidos em tempo real na própria interface em tela.
* **Exportações:** A exportação de dados em formatos externos (PDF, CSV, Excel) **não faz parte da primeira versão**.

## 23. APIs e Integrações Externas

* **Integração Exclusiva:** API de autenticação do Google (Google OAuth / OpenID Connect) para login rápido. Nenhuma outra API externa ou integração bancária automática (OFX/Open Finance) está presente na primeira versão.

## 24. Segurança Funcional

* Proteção rigorosa de rotas por sessão validada no backend.
* Armazenamento seguro de senhas por hash robusto.
* Isolamento estrito de dados entre usuários (prevenção contra IDOR - Insecure Direct Object References).
* Mensagens de erro genéricas e seguras para o usuário final, evitando exposição de detalhes de infraestrutura.

## 25. Organização Sugerida da Implementação

1. Preparação do `[Diretório do Projeto - Repositório]` e ambiente virtual Python (`venv`).
2. Criação da estrutura inicial de pastas (`app/`, `config/`, `database/migrations/`, `logs/`).
3. Configuração do arquivo `config/config.py` (sem uso de `.env`) e proteção contra acesso direto.
4. Inicialização do framework Flask e configuração do ORM / conexão com MySQL.
5. Criação da estrutura de migrations (Alembic / Flask-Migrate) e tabelas do banco de dados (usuários, contas, categorias, lançamentos, recorrentes, logs).
6. Implementação do módulo de Autenticação (Login tradicional com hash e Google OAuth).
7. Implementação do controle de acesso e isolamento por usuário.
8. Implementação do módulo de Contas / Carteiras e saldos iniciais.
9. Implementação do módulo de Categorias e tetos de orçamento.
10. Implementação do módulo de Lançamentos (avulsos, transferências, filtros e paginação).
11. Implementação da automação de Lançamentos Recorrentes.
12. Implementação do Painel Principal (Dashboard) com indicadores, gráfico de despesas e alertas de vencimento.
13. Implementação das configurações visuais (tema claro e escuro seguindo o `DESIGN.md`).
14. Implementação do sistema de logs de erro com contingência em arquivo.
15. Revisão de segurança, testes locais em XAMPP e preparação para deploy no PythonAnywhere.

## 26. Critérios de Aceitação Técnica e Funcional

* [ ] Sistema implementado seguindo rigorosamente a stack Python/Flask, MySQL e React/HTML/CSS.
* [ ] Padrão arquitetural MVC respeitado com separação clara entre Models, Controllers e Views.
* [ ] Isolamento de dados por usuário testado e funcional em todas as rotas.
* [ ] Autenticação via e-mail/senha (com hash) e Google OAuth operando corretamente.
* [ ] Banco de dados estruturado via migrations com índices de desempenho criados.
* [ ] Funcionalidades principais (Dashboard, Lançamentos, Transferências, Contas, Categorias, Recorrentes, Temas) operando conforme especificado.
* [ ] Alertas visuais de vencimento e estouro de orçamento ativos.
* [ ] Log de erros operacional com contingência em arquivo quando o banco falhar.
* [ ] Ausência total de arquivos `.env` (configuração centralizada em `config/config.py`).
* [ ] Pastas internas protegidas contra acesso direto via navegador.
* [ ] Interface visual aderente ao guia *High-Contrast Dark* (`DESIGN.md`).

## 27. Pontos Pendentes e Decisões Futuras

Não foram identificadas pendências para iniciar a codificação com base neste FSD.