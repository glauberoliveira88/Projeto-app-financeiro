# DOCUMENTO DE ESPECIFICAÇÃO FUNCIONAL (FSD)

## 1. Visão Geral

* **Nome do sistema:** FinançasSimples.
* **Objetivo principal:** Proporcionar controle financeiro pessoal simplificado, visual e ágil para o acompanhamento de receitas, despesas, carteiras e transferências, permitindo ao usuário organizar sua vida financeira cotidiana de forma prática e sem termos contábeis complexos.
* **Resumo do funcionamento:** O sistema opera como um painel web integrado e unificado. Apresenta indicadores em tempo real com saldos mensais, receitas e despesas consolidadas, gráfico monocromático de despesas por categoria, bloco de alertas visuais para contas vencidas ou próximas do vencimento e monitoramento de tetos de orçamento por categoria. Permite a gestão completa de lançamentos avulsos e recorrentes (fixos gerados automaticamente na virada do mês), controle de múltiplas contas/carteiras com saldos individuais, transferências entre contas próprias e acesso seguro híbrido (e-mail/senha ou conta Google).
* **Público usuário:** Pessoas físicas que buscam organizar o orçamento diário em um ambiente de uso estritamente individual por painel exclusivo.
* **Contexto de uso:** Aplicação web responsiva acessível de forma fluida em computadores, tablets e smartphones, com suporte a temas claro e escuro, tendo a estética *High-Contrast Dark* (Obsidian) como padrão visual orientador.
* **Observações relevantes para implementação:**
  * O sistema é estritamente de uso individual por painel; não há compartilhamento de contas ou multiusuário no mesmo painel.
  * O isolamento absoluto de dados entre usuários no banco de dados deve ser garantido em todas as rotas e consultas.
  * A usabilidade deve priorizar agilidade em telas de toque (mobile-first), feedback visual instantâneo e ausência de burocracias cadastrais.
  * A aderência aos padrões de design (superfícies near-black, separação por bordas finas, tipografia Geist, cores funcionais) é obrigatória para assegurar precisão e legibilidade.

---

## 2. Documentos do Projeto para Implementação

Para a construção e implementação do sistema, a IA codificadora deverá utilizar exclusivamente os seguintes documentos:

* `docs/FSD.md` (este documento de especificação funcional);
* `docs/DESIGN.md` (guia de diretrizes visuais e interface *High-Contrast Dark*).

*(Nota: Este FSD consolida integralmente todos os requisitos funcionais, regras de negócio, definições de arquitetura, modelagem de dados e requisitos técnicos do projeto. Nenhuma consulta a documentos preliminares anteriores é necessária para a implementação).*

---

## 3. Stack Definida

* **Linguagem de programação no backend:** Python.
* **Framework backend:** Flask (organizado modularmente através de Blueprints e Application Factory).
* **Banco de dados:** MySQL (banco de dados relacional).
* **Tecnologias de interface (frontend):** HTML5, CSS3, JavaScript moderno (ES6+) e React para componentes de interface e estado reativo.
* **Diretrizes de design e harmonização visual:**
  * O padrão visual principal, oficial e estruturante do projeto é a identidade *High-Contrast Dark* (Obsidian), conforme detalhado no documento de design: fonte Geist, paleta zinc, superfícies near-black (`#09090b`), destaque primário em violeta suave (`#a78bfa`), verde esmeralda (`#34d399`) para sucessos e receitas, vermelho (`#ef4444`) estritamente para atrasos e erros, e separação de containers por bordas sutis (`1px solid #27272a`), sem o uso de sombras pesadas ou cores decorativas.
  * O suporte ao "Tema Claro" atua como uma variação acessível e invertida de alto contraste baseada na mesma sobriedade: superfícies claras em zinc (`#ffffff` e `#f4f4f5`), bordas em `1px solid #e4e4e7`, tipografia em `#09090b` e `#71717a`, preservando exatamente os mesmos acentos funcionais violeta, verde esmeralda e vermelho. Dessa forma, a diretriz *"Never use light backgrounds"* do documento de design governa a integridade do tema escuro oficial, enquanto a alternância para o tema claro atende à flexibilidade de uso do usuário com a mesma precisão estética.
* **Bibliotecas e frameworks auxiliares:**
  * Backend:
    * Flask (núcleo da aplicação web e roteamento);
    * Flask-Login ou gerenciamento de sessão seguro via cookies HTTP-only;
    * SQLAlchemy / Flask-SQLAlchemy (camada de abstração e comunicação relacional com MySQL);
    * Conector MySQL: `PyMySQL` ou `mysql-connector-python`;
    * Segurança e criptografia: `werkzeug.security` ou `bcrypt` para hashing seguro de senhas;
    * Autenticação OAuth: `google-auth` / `requests-oauthlib` para integração com Google OAuth 2.0;
    * Envio de E-mails / Notificação: `Flask-Mail` ou módulo nativo `smtplib` para despacho seguro de mensagens de recuperação de senha;
    * Migrations: Mecanismo versionado com suporte a scripts SQL controlados / Alembic (Flask-Migrate).
  * Frontend:
    * React e ReactDOM (renderização de componentes reativos, gestão de estado local e formulários), integrados via scripts empacotados localmente em `app/static/js/vendor/` (ou módulos ESM nativos), dispensando a necessidade de runtime ou build via Node.js/npm no ambiente de desenvolvimento e produção (PythonAnywhere);
    * Biblioteca de ícones leves via SVG empacotados localmente em `app/static/` (alinhados ao protótipo visual da interface), sem chamadas externas a CDNs.
* **Padrão arquitetural:** MVC (Model-View-Controller) adaptado para Python/Flask e React.
* **Restrições técnicas:**
  * Moeda padrão e exclusiva: Real brasileiro (R$). Não há suporte a moedas estrangeiras.
  * Uploads de arquivos: Totalmente fora de escopo na primeira versão (sem envio de fotos, comprovantes ou notas fiscais).
  * Exportações: Totalmente fora de escopo na primeira versão (sem arquivos CSV, Excel ou PDF).
  * Integrações bancárias: Totalmente fora de escopo (sem conexões automáticas OFX ou Open Finance).
* **Observações sobre uso local de bibliotecas:**
  * O projeto deve preferir o empacotamento local de assets (CSS, JS, fontes) na pasta `app/static/`, assegurando funcionamento autônomo sem dependência crítica de conexões externas de CDN no ambiente de execução.

---

## 4. Ambientes do Projeto

* **Ambiente de desenvolvimento local:**
  * Sistema operacional padrão do desenvolvedor.
  * Ambiente virtual Python isolado (`venv`).
  * Servidor de desenvolvimento embutido do Flask (`python run.py` ou `flask run`).
  * Banco de dados MySQL gerenciado localmente via XAMPP (porta padrão 3306).
* **Ambiente de testes ou homologação:**
  * Não haverá ambiente formal ou obrigatório de testes/homologação externo nesta primeira versão.
  * Todas as validações funcionais, testes de rotas, testes de sessão e integridade de banco de dados serão realizados diretamente no ambiente local antes do deploy final.
* **Ambiente de produção:**
  * Hospedagem em nuvem configurada para aplicações Python, definida para o **PythonAnywhere**.
  * Servidor web WSGI gerenciado pelo PythonAnywhere apontando para a aplicação Flask (`wsgi.py`).
  * Banco de dados MySQL provisionado no PythonAnywhere.
* **Observações sobre deploy:**
  * O deploy consistirá na clonagem do repositório no PythonAnywhere, ativação do ambiente virtual com as dependências do `requirements.txt`, configuração do arquivo de conexão `config/config.py` com as credenciais do banco de produção, execução controlada das migrations via console Python e reinicialização do web app no painel WSGI.

---

## 5. Arquitetura do Sistema

A referência principal para toda a estrutura de arquivos e diretórios do sistema é:

`[Diretório do Projeto - Repositório]`

Este diretório representa a pasta raiz do projeto versionada no repositório Git. Essa pasta poderá ser alocada dentro da pasta pública adequada de cada servidor ou ambiente, convivendo inclusive com subpastas sem conflitos:
* No XAMPP local, pode residir em `htdocs/nome-do-projeto/` (ex: `htdocs/financas-simples/`);
* Na Hostnet ou outros servidores Apache, pode residir em `www/nome-do-projeto/` ou `public_html/nome-do-projeto/`;
* No PythonAnywhere, pode residir na raiz do usuário (ex: `/home/usuario/financas-simples/`).

A aplicação não deve assumir que é a única proprietária da raiz do servidor web.

### Aplicação do padrão MVC (Model-View-Controller)

O sistema organiza suas responsabilidades estritamente sob o padrão MVC:

1. **Model (`app/models/`):**
   * Responsável pela camada de dados, regras de persistência, mapeamento das tabelas do MySQL e integridade referencial.
   * Encapsula todas as operações de banco de dados, exigindo que toda consulta filtre obrigatoriamente os dados com base no `usuario_id` do usuário logado na sessão.
   * Não lida diretamente com renderização visual nem com manipulação de requisições HTTP.

2. **Controller (`app/controllers/`):**
   * Implementado em Flask através de módulos e Blueprints específicos (ex: `auth_controller.py`, `dashboard_controller.py`, `lancamentos_controller.py`, `contas_controller.py`, `categorias_controller.py`, `configuracoes_controller.py`).
   * Recebe as requisições HTTP do cliente, valida parâmetros de entrada, orquestra a lógica de negócio acionando os Models necessários e retorna respostas estruturadas.
   * **Contrato de Comunicação Frontend-Backend (API JSON):**
     * O Flask serve o shell HTML base através da rota web principal (`/` e páginas auxiliares).
     * Toda a comunicação de dados entre a interface React e o backend é realizada de forma assíncrona sob o prefixo padronizado `/api/`, trafegando estritamente JSON:
       * `/api/auth/*`: Rotas de autenticação, cadastro, login, logout, recuperação e verificação de sessão;
       * `/api/dashboard/*`: Consulta de indicadores, métricas consolidadas e distribuição por categorias;
       * `/api/lancamentos/*`: Operações CRUD de receitas, despesas, transferências e filtros;
       * `/api/contas/*`: Gestão de carteiras, saldos em tempo real e arquivamento/reativação;
       * `/api/categorias/*`: Gestão de categorias, tetos de gastos e reatribuição em lote;
       * `/api/recorrentes/*`: Gestão de modelos fixos e gatilho de automação mensal;
       * `/api/usuario/*`: Consulta e alteração de preferências (ex: tema claro/escuro).
   * Aplica decoradores de segurança (ex: `@login_required`) e tratamento centralizado de exceções.

3. **View (`app/templates/` e `app/static/`):**
   * Responsável pela interface que o usuário visualiza e interage.
   * O Flask entrega a casca HTML base através de `app/templates/index.html`. A partir desse ponto de montagem, a interface é assumida pelos componentes e fluxos construídos em React.
   * **Injeção e Manipulação de Token CSRF no Frontend:** O template `app/templates/index.html` injeta o token CSRF em uma meta tag HTML: `<meta name="csrf-token" content="{{ csrf_token() }}">`. A camada de serviço HTTP do React (`api.js` / cliente `fetch`) lê automaticamente o valor dessa meta tag e anexa o cabeçalho `X-CSRFToken` em todas as requisições assíncronas de mutação de estado (`POST`, `PUT`, `PATCH`, `DELETE`), garantindo proteção transparente contra CSRF.
   * O frontend consome os endpoints sob o prefixo `/api/`, gerencia estados de carregamento, modais, formulários interativos, validações em tempo real e gráficos dinâmicos.

### Proteção de arquivos e pastas internas

Pastas internas como `config/`, `app/`, `app/models/`, `app/controllers/`, `database/`, `database/migrations/` e `logs/` contêm códigos de negócio, credenciais, scripts de banco de dados e registros que **não podem ser acessados diretamente pelo navegador sob nenhuma circunstância**.

A proteção deve seguir duas camadas fundamentais:
1. **Proteção em nível de servidor web / Apache (`.htaccess`):** Em ambientes com Apache (como XAMPP ou Hostnet), arquivos `.htaccess` localizados na raiz do repositório e nas pastas sensíveis devem aplicar diretivas de negação de acesso (ex: `Require all denied` ou bloqueio de extensões `.py`, `.sql`, `.log`, `.conf`).
2. **Proteção estrutural da aplicação (Flask):** O roteamento da aplicação não expõe links diretos para o sistema de arquivos. Apenas a pasta `app/static/` é mapeada para entrega pública de assets (CSS, JS, fontes e imagens). Qualquer requisição que não coincida com as rotas controladas pelos Controllers deve retornar erro seguro 404.
3. **Arquivo de configuração em código:** Parâmetros de infraestrutura, credenciais de banco e chaves de segurança devem residir obrigatoriamente em `config/config.py` (arquivo de código Python) e **nunca em arquivos de texto plano `.env`**, eliminando o risco de leitura direta caso ocorra uma falha de interpretação do servidor web.

### Sugestão da Estrutura de Diretórios

```text
[Diretório do Projeto - Repositório]/
├── app/
│   ├── __init__.py               # Fábrica da aplicação Flask (App Factory)
│   ├── controllers/              # Controladores / Blueprints Flask (Rotas Web e API)
│   │   ├── __init__.py
│   │   ├── auth_controller.py
│   │   ├── dashboard_controller.py
│   │   ├── lancamentos_controller.py
│   │   ├── contas_controller.py
│   │   ├── categorias_controller.py
│   │   └── configuracoes_controller.py
│   ├── models/                   # Models de dados e regras de negócio
│   │   ├── __init__.py
│   │   ├── usuario.py
│   │   ├── conta.py
│   │   ├── categoria.py
│   │   ├── lancamento.py
│   │   ├── lancamento_recorrente.py
│   │   ├── log_erro.py
│   │   └── log_seguranca.py
│   ├── templates/                # Templates HTML servidos pelo Flask
│   │   └── index.html            # Shell base da aplicação (injetando CSRF token e React)
│   └── static/                   # Assets acessíveis pelo navegador
│       ├── css/
│       │   └── style.css         # Estilos da interface (Design Obsidian)
│       ├── js/
│       │   ├── app.js            # Aplicação React e componentes da interface
│       │   └── vendor/           # Scripts auxiliares e bibliotecas locais
│       └── fonts/                # Família de fontes Geist
├── config/
│   └── config.py                 # Arquivo de configuração em código Python (sem .env)
├── database/
│   ├── migrate.py                # Script seguro de execução de migrations via CLI
│   └── migrations/               # Arquivos SQL versionados de migração
│       ├── 001_create_initial_tables.sql
│       └── 002_create_indexes.sql
├── logs/                         # Pasta de logs de contingência em arquivo (protegida)
│   ├── .gitkeep
│   └── error.log                 # Log de contingência do sistema
├── .htaccess                     # Regras de proteção para servidores Apache
├── requirements.txt              # Lista de dependências Python (Flask, Flask-Mail, PyMySQL, etc.)
├── run.py                        # Ponto de entrada para execução local (desenvolvimento)
└── wsgi.py                       # Ponto de entrada WSGI para produção (PythonAnywhere)
```

---

## 6. Escopo Funcional da Primeira Versão

### 6.1. Módulo de Autenticação e Acesso
* **Objetivo:** Permitir que o usuário acesse seu painel financeiro exclusivo com segurança e praticidade.
* **Usuários envolvidos:** Usuário Pessoal (visitante e usuário cadastrado).
* **Ações permitidas:**
  * Cadastro de novo usuário via formulário tradicional (nome, e-mail, senha e confirmação de senha), com provisionamento automático:
    1. Da lista canônica das 10 categorias padrão iniciais;
    2. De uma carteira padrão inicial (nome: *"Carteira"*, saldo inicial: R$ 0,00, status: *ativo*), garantindo que o usuário possa realizar lançamentos imediatos logo após a criação da conta.
  * Login tradicional informando e-mail e senha.
  * Login rápido integrado via conta Google (Google OAuth 2.0), aplicando o mesmo provisionamento automático de categorias e da carteira padrão caso seja o primeiro acesso.
  * Recuperação de senha por e-mail mediante envio de link seguro com token temporário expirável.
  * Redefinição de senha informando nova senha e validação do token.
  * Logout manual encerrando a sessão ativa.
* **Resultado esperado:** Acesso concedido e inicialização de sessão com carregamento exclusivo dos dados do usuário logado.
* **Dependências:** Sistema de sessões Flask, banco de dados MySQL, integração Google OAuth e serviço SMTP configurado no Flask.
* **Regras relacionadas:** Senhas devem ter no mínimo 8 caracteres. E-mails devem ser únicos no sistema. Sessão permanece ativa até que o usuário clique em sair (logout manual).

### 6.2. Módulo do Painel Principal (Dashboard)
* **Objetivo:** Fornecer visão imediata, consolidada e visual da saúde orçamentária do mês corrente ou do mês selecionado.
* **Usuários envolvidos:** Usuário Pessoal autenticado.
* **Ações permitidas:**
  * Visualizar cartões com os três indicadores essenciais do período:
    1. Saldo Líquido do Mês (Receitas pagas - Despesas pagas);
    2. Total de Receitas (somatório das entradas do mês);
    3. Total de Despesas (somatório das saídas do mês).
  * Visualizar gráfico de barras simples e monocromático (em tons de violeta/zinc) com a distribuição de despesas por categoria no mês ativo.
  * Visualizar bloco de destaque de alertas contendo contas pendentes com vencimento próximo (nos próximos 5 dias) ou já vencidas (em atraso).
  * Selecionar mês e ano para navegação histórica livre entre períodos passados e futuros.
* **Resultado esperado:** O painel recalcula instantaneamente os valores e alertas com base no mês/ano escolhido.
* **Dependências:** Lançamentos cadastrados no período e regras de cálculo de saldos.
* **Regras relacionadas:** Transferências internas entre contas não compõem nem alteram o somatório geral de receitas ou de despesas.

### 6.3. Módulo de Gestão de Lançamentos
* **Objetivo:** Gerenciar com agilidade todas as movimentações financeiras do usuário.
* **Usuários envolvidos:** Usuário Pessoal autenticado.
* **Ações permitidas:**
  * Registrar novo lançamento avulso (receita ou despesa) informando: tipo, valor (positivo em R$), data de competência, data de vencimento, descrição, categoria associada, conta/carteira de origem, forma de pagamento básica (Dinheiro, PIX, Cartão de Débito, Cartão de Crédito, Boleto, Transferência), status (`pago` ou `pendente`) e observação textual opcional.
  * Realizar transferência entre contas próprias informando: valor, data, conta de origem, conta de destino e observação opcional.
  * Editar qualquer lançamento existente (alterando descrição, valor, data, status, categoria ou conta).
  * Excluir logicamente (*soft delete*) qualquer lançamento avulso.
  * Filtrar listagem de lançamentos por: período (mês/ano), conta específica, categoria, tipo (receita, despesa, transferência) e status (`pago`, `pendente`).
  * Buscar movimentações por texto em tempo real (filtrando pela descrição).
* **Resultado esperado:** Lançamento persistido no banco, saldo da carteira atualizado e listagem refletindo imediatamente a operação.
* **Dependências:** Contas ativas e categorias cadastradas.
* **Regras relacionadas:** Lançamentos com status `pago` impactam diretamente o saldo corrente da conta selecionada. Lançamentos com status `pendente` afetam a previsão e geram alertas de vencimento, mas só alteram o saldo realizado quando marcados como `pago`. Em transferências, a data de vencimento é preenchida automaticamente com a mesma data da transferência e o status é definido como `pago`.

### 6.4. Módulo de Lançamentos Recorrentes (Automação de Fixos)
* **Objetivo:** Eliminar o retrabalho operacional de redigitação de despesas e receitas fixas todo mês.
* **Usuários envolvidos:** Usuário Pessoal autenticado.
* **Ações permitidas:**
  * Cadastrar modelo de lançamento recorrente informando: tipo (receita ou despesa), valor, descrição, categoria, conta preferencial, forma de pagamento e dia de vencimento padrão no mês (1 a 31).
  * Ativar ou desativar temporariamente um modelo recorrente.
  * Editar parâmetros do modelo recorrente.
  * Excluir modelo recorrente.
* **Resultado esperado:** Na virada do ciclo mensal, o sistema detecta os modelos recorrentes ativos e gera de forma autônoma os lançamentos correspondentes para o novo mês com status `pendente`. Caso o dia do vencimento seja superior à quantidade de dias do mês (ex: dia 31 em meses de 30 ou 28 dias), a data é ajustada para o último dia válido do mês.
* **Gatilho de Execução Sincronizado:** Para garantir que os lançamentos fixos estejam sempre gerados independente da tela inicial acessada pelo usuário, a rotina interna de verificação e geração de recorrências é executada de forma transparente tanto na consulta do Dashboard (`GET /api/dashboard/resumo`) quanto na listagem de lançamentos (`GET /api/lancamentos`), assegurando que a lista de movimentações esteja sempre atualizada.
* **Dependências:** Tabela de lançamentos e rotina de verificação no primeiro acesso do usuário no período.
* **Regras relacionadas:** Lançamentos gerados a partir de um modelo recorrente tornam-se lançamentos independentes no mês correspondente, podendo ser editados ou pagos individualmente sem alterar o modelo base.

### 6.5. Módulo de Contas e Carteiras
* **Objetivo:** Organizar onde o patrimônio e os recursos financeiros do usuário estão custodiados.
* **Usuários envolvidos:** Usuário Pessoal autenticado.
* **Ações permitidas:**
  * Cadastrar nova conta (ex: Conta Corrente Banco A, Carteira Dinheiro Físico, Poupança, Cartão Pré-pago) definindo nome da conta e saldo inicial. O nome da conta deve ser único para o usuário.
  * Editar o nome da conta.
  * Visualizar lista de contas ativas com seus respectivos saldos calculados em tempo real (Saldo Inicial + Receitas Pagas - Despesas Pagas + Transferências Recebidas - Transferências Enviadas).
  * Arquivar conta que não é mais utilizada (inativação lógica), retirando-a dos seletores de novos lançamentos sem perder o histórico financeiro passado.
  * Reativar conta previamente arquivada.
  * Exclusão definitiva: permitida estritamente se a conta não possuir nenhum registro de lançamento histórico vinculado (nem ativo, nem em soft delete). Se houver histórico vinculado, a exclusão física é bloqueada e a interface orienta o arquivamento.
* **Resultado esperado:** Controle visual preciso da liquidez por carteira.
* **Dependências:** Módulo de lançamentos.
* **Regras relacionadas:** É terminantemente bloqueada a exclusão física de contas que possuam histórico de lançamentos vinculados. Para descontinuar uma conta com movimentações, o usuário deve utilizar a função de arquivamento.

### 6.6. Módulo de Categorias e Orçamentos
* **Objetivo:** Classificar movimentações e controlar tetos de gastos.
* **Usuários envolvidos:** Usuário Pessoal autenticado.
* **Ações permitidas:**
  * **Carga Inicial da Lista Canônica de Categorias Padrão:** No primeiro acesso do usuário (via cadastro ou Google), o sistema provisiona automaticamente as seguintes 10 categorias padrão:
    * **Categorias de Receita:**
      1. *Salário*
      2. *Rendimentos*
      3. *Outras Receitas*
    * **Categorias de Despesa:**
      1. *Alimentação*
      2. *Moradia*
      3. *Transporte*
      4. *Saúde*
      5. *Educação*
      6. *Lazer*
      7. *Outras Despesas*
  * Cadastrar novas categorias personalizadas informando nome e tipo (receita ou despesa). O nome da categoria deve ser único para o mesmo usuário e tipo.
  * Definir teto de orçamento mensal opcional para categorias de despesa (valor monetário máximo planejado para o mês).
  * Editar nome e teto orçamentário da categoria.
  * Arquivar categoria para impedir novas associações em lançamentos.
  * Excluir categoria:
    * Se a categoria não possuir nenhum lançamento registrado no banco (nem ativo, nem soft-deletado), a exclusão física direta é permitida.
    * Se possuir lançamentos vinculados no banco, o sistema bloqueia a exclusão direta e apresenta as opções de: (a) arquivamento imediato; ou (b) fluxo de reatribuição em lote, que migra todos os lançamentos (ativos e soft-deletados) e modelos recorrentes para outra categoria ativa do mesmo tipo antes de executar a exclusão da categoria original, prevenindo violações de integridade referencial.
* **Resultado esperado:** Categorização consistente e alertas visuais automáticos no painel sempre que o total de despesas de uma categoria atingir ou superar o teto de gastos estipulado.
* **Dependências:** Módulo de lançamentos e painel principal.

### 6.7. Configurações Visuais e Perfil
* **Objetivo:** Garantir conforto visual e personalização básica.
* **Usuários envolvidos:** Usuário Pessoal autenticado.
* **Ações permitidas:**
  * Alternar manualmente entre tema escuro (*High-Contrast Dark* - padrão oficial) e tema claro através de botão seletor acessível no cabeçalho ou menu, alternando dinamicamente o logotipo exibido (`logo_tema_escuro.png` para tema escuro e `logo_tema_claro.png` para tema claro).
  * Visualizar dados do perfil (nome e e-mail).
* **Resultado esperado:** Interface e logotipo atualizados instantaneamente com a preferência de tema persistida localmente (ou no perfil) para os próximos acessos.

---

## 7. Fora de Escopo

Os seguintes itens, funcionalidades e integrações **NÃO** fazem parte da primeira versão do sistema e não devem ser implementados:

1. **Uploads, anexos e fotos de comprovantes:** Não haverá envio nem armazenamento de fotos de recibos, comprovantes bancários em PDF ou notas fiscais. O recurso foi adiado para versões futuras para simplificar infraestrutura e armazenamento.
2. **Importação automática de extratos bancários:** Não haverá importação de arquivos bancários em formato OFX, CSV ou integração via Open Finance / APIs bancárias. O registro de movimentações é manual e por automação de recorrências.
3. **Gestão de investimentos e patrimônio complexo:** Não haverá acompanhamento de ativos de renda fixa, ações da bolsa, dividendos, fundos imobiliários ou carteiras de criptomoedas.
4. **Divisão de despesas e contas em grupo:** Não haverá recursos de rateio de despesas, contas de casal conjuntas ou divisão de custos de viagens. O uso é estritamente individual.
5. **Exportação de relatórios em arquivos externos:** Não haverá geração nem download de planilhas Excel/CSV ou arquivos de relatório em PDF. Todas as consultas e acompanhamentos são realizados de forma dinâmica e interativa diretamente na interface web.
6. **Múltiplas moedas:** Não haverá conversão de moedas ou suporte a dólares, euros ou moedas internacionais. O sistema operará única e exclusivamente em Real brasileiro (R$).
7. **Perfis múltiplos ou papéis administrativos corporativos:** Não haverá cadastro de papéis como "Gerente", "Operador", "Auditor" ou "Contador". Apenas o perfil único `Usuário Pessoal`.

---

## 8. Perfis de Usuário e Permissões

O FinançasSimples é uma aplicação de finanças pessoais voltada para o uso individual. Desta forma, o sistema contempla apenas um perfil de usuário ativo:

### Perfil: Usuário Pessoal
* **Descrição:** Pessoa física que cria sua conta no sistema e passa a gerenciar seu próprio orçamento financeiro.
* **Áreas acessíveis:** Todas as áreas da aplicação pertencentes ao seu próprio painel (Login, Cadastro, Recuperação de Senha, Dashboard, Lançamentos, Contas/Carteiras, Categorias, Lançamentos Recorrentes e Configurações).
* **Permissões concedidas:**
  * Gerenciamento de suas próprias contas/carteiras (criar, visualizar, editar nome, arquivar, reativar e excluir apenas se não houver histórico de movimentações);
  * Gerenciamento completo de suas próprias categorias e limites de orçamento (incluindo exclusão com reatribuição total de histórico);
  * Gerenciamento completo de seus próprios lançamentos avulsos e modelos recorrentes;
  * Visualização dos indicadores e gráficos calculados estritamente sobre suas próprias movimentações.
* **Ações bloqueadas e restrições absolutas:**
  * É expressamente bloqueada qualquer tentativa de leitura, alteração ou exclusão de registros pertencentes a outro usuário.
  * O usuário não tem acesso a painéis de administração global, servidores ou tabelas técnicas de outros usuários.
  * O sistema aplica restrição automática: todas as consultas ao banco de dados injetam o predicado `usuario_id = current_user.id`.

### Matriz de Permissões

| Funcionalidade / Recurso | Ações Permitidas para o Usuário Pessoal | Restrições Aplicadas |
| :--- | :--- | :--- |
| **Autenticação e Perfil** | Cadastrar, logar, deslogar, redefinir senha e alterar preferências visuais. | Não pode alterar o identificador (`id`) de usuário ou vincular e-mail já existente. |
| **Contas / Carteiras** | Criar contas, editar nome, consultar saldos, arquivar, reativar e excluir contas sem histórico. | Bloqueada a exclusão física se houver qualquer lançamento atrelado (exige arquivamento). Não acessa contas de terceiros. |
| **Categorias** | Criar categorias, editar nome e teto de gastos, arquivar e excluir (com reatribuição total se houver histórico). | Bloqueada a exclusão direta se houver lançamentos vinculados (exige reatribuição de todo o histórico ativo e inativo ou arquivamento). Não acessa categorias de terceiros. |
| **Lançamentos Avulsos** | Criar, visualizar, filtrar, editar e excluir logicamente (*soft delete*). | Afeta apenas carteiras do próprio usuário. Não pode alterar registros de terceiros. |
| **Lançamentos Recorrentes** | Criar modelos, editar, desativar, ativar e excluir modelos de fixos. | Geração de lançamentos restrita ao painel do próprio usuário. |
| **Dashboard e Gráficos** | Navegar entre períodos mensais, consultar indicadores e alertas de vencimento. | Totalmente isolado por `usuario_id`. |
| **Administração Global** | Nenhuma ação permitida. | Sem rotas públicas de administração técnica. |

---

## 9. Recursos Estruturais do Sistema

Os seguintes recursos estruturais foram formalmente definidos para sustentação do sistema:

### 9.1. Autenticação Híbrida
* **Objetivo:** Fornecer acesso seguro, rápido e confiável ao painel financeiro.
* **Onde será aplicado:** Telas e rotas de entrada do sistema (`/login`, `/cadastro`, `/recuperar-senha`, `/api/auth/*`).
* **Comportamento esperado:**
  * O usuário pode optar por criar conta e efetuar login utilizando e-mail e senha tradicionais.
  * As senhas são criptografadas antes da gravação no banco utilizando hash seguro (`bcrypt` ou algoritmo baseado em PBKDF2/scrypt via `werkzeug.security`), garantindo que o texto plano nunca seja exposto.
  * Alternativamente, o usuário pode clicar em "Entrar com Google". O sistema utiliza o fluxo oficial Google OAuth 2.0 (OpenID Connect), recebe o token do Google, valida a autenticidade e, caso o usuário ainda não exista, provisiona a conta automaticamente no banco de dados vinculando o e-mail verificado, gerando a lista canônica de categorias padrão e criando a carteira inicial padrão (*"Carteira"* com saldo inicial R$ 0,00).
  * A sessão permanece ativa através de cookie seguro e assinado pelo Flask até que o usuário efetue o logout manual.

### 9.2. RBAC Simplificado e Isolamento Estrito de Dados (Tenant Isolation)
* **Objetivo:** Garantir a privacidade e confidencialidade absoluta das informações financeiras de cada usuário.
* **Onde será aplicado:** Em todos os Controllers, Models e consultas SQL do sistema.
* **Comportamento esperado:**
  * O `usuario_id` é extraído diretamente da sessão autenticada no backend e nunca a partir de parâmetros editáveis enviados pelo navegador.
  * Todas as operações de leitura (`SELECT`), escrita (`INSERT`), atualização (`UPDATE`) e exclusão (`DELETE` ou *soft delete*) devem conter a cláusula `WHERE usuario_id = :current_user_id`.
  * Qualquer tentativa de manipulação de IDs de terceiros (prevenção contra IDOR) resulta em bloqueio imediato e retorno de código HTTP 403 (Acesso Negado).

### 9.3. Auditoria de Dados
* **Objetivo:** Rastreabilidade mínima temporal e de integridade dos registros financeiros.
* **Onde será aplicado:** Em todas as tabelas transacionais e cadastrais do banco de dados (`usuarios`, `contas`, `categorias`, `lancamentos_recorrentes`, `lancamentos`).
* **Comportamento esperado:**
  * Cada tabela contém obrigatoriamente as colunas `created_at` (data e hora de inserção) e `updated_at` (data e hora da última modificação), mantidas de forma automatizada pelo banco de dados ou pelo ORM.
  * A interface exibe discretamente no detalhamento de lançamentos a data e horário da última atualização para fins de conferência do usuário.

### 9.4. Soft Delete (Exclusão Lógica)
* **Objetivo:** Preservar a consistência do histórico contábil e evitar que a exclusão de um registro danifique saldos consolidados ou cálculos de períodos passados.
* **Onde será aplicado:** Na tabela de `lancamentos` (através de coluna `deleted_at`) e nas tabelas de `contas` e `categorias` (através de status `arquivado`).
* **Comportamento esperado:**
  * Quando um lançamento é excluído pelo usuário, o sistema não remove a linha do banco; em vez disso, preenche a coluna `deleted_at` com o timestamp atual.
  * As consultas do sistema filtram rotineiramente `deleted_at IS NULL`.
  * A remoção do lançamento reverte imediatamente o saldo realizado na conta bancária correspondente caso seu status fosse `pago`.

### 9.5. Log de Erros com Mecanismo de Contingência
* **Objetivo:** Registrar e diagnosticar falhas na aplicação Flask com segurança, sem expor dados de infraestrutura ao usuário.
* **Onde será aplicado:** Em interceptadores globais de erro no Flask e blocos de tratamento de exceções críticas.
* **Comportamento esperado:**
  * Erros não tratados (500) e falhas operacionais são gravados na tabela `logs_erros` no MySQL contendo data/hora, nível do erro, mensagem, rota e ID do usuário quando disponível.
  * **Estratégia de contingência:** Caso a falha decorra de indisponibilidade do próprio banco de dados MySQL, queda de conexão ou falha crítica anterior à inicialização do banco, o sistema captura a exceção e grava o log de erro em um arquivo de texto protegido: `logs/error.log`.
  * A pasta `logs/` reside dentro do `[Diretório do Projeto - Repositório]` com proteção de acesso web via servidor (`.htaccess`).
  * O usuário final nunca visualiza mensagens de traceback ou erros de SQL; recebe apenas uma mensagem amigável e segura em tela informando que ocorreu uma instabilidade temporária.

### 9.6. Log de Segurança
* **Objetivo:** Rastrear eventos críticos de segurança para proteção contra abusos e tentativas de invasão.
* **Onde será aplicado:** Camadas de autenticação, recuperação de senha e autorização.
* **Comportamento esperado:**
  * Registra eventos como: falha de login (credenciais incorretas), bloqueio por limite de tentativas consecutivas, tentativas de acesso a recursos pertencentes a outro usuário (erro 403 / IDOR), solicitações de recuperação de senha e alterações de credenciais.
  * Informações armazenadas na tabela `logs_seguranca`: data/hora, tipo de evento, IP do cliente, `usuario_id` (se identificado) e descrição resumida da tentativa.

### 9.7. Configurações Globais Técnicas em Código
* **Objetivo:** Manter as credenciais e flags de sistema seguras e desacopladas, sem risco de exposição pública por falha de servidor.
* **Onde será aplicado:** Arquivo `config/config.py`.
* **Comportamento esperado:**
  * É expressamente vedado o uso de arquivos `.env` neste projeto.
  * Toda a configuração técnica reside em arquivo Python nativo (`config/config.py`), o qual define parâmetros de conexão com MySQL, chave secreta de sessão (`SECRET_KEY`), credenciais do Google OAuth, configurações de e-mail SMTP e flags de depuração.
  * O arquivo é acessado apenas internamente via `import` e protegido contra leitura web.

---

## 10. Entidades do Sistema

### 10.1. Entidade: Usuário (`Usuario`)
* **Finalidade:** Identificar a pessoa no sistema, autenticar sua sessão e atuar como a chave de isolamento de todos os seus dados.
* **Principais informações:** Identificador único, nome completo, e-mail cadastrado, hash criptográfico da senha, ID da conta Google (quando autenticado via Google), preferência de tema visual (claro/escuro), timestamps de criação e atualização.
* **Relacionamentos funcionais:** Possui 1 para N com Contas, 1 para N com Categorias, 1 para N com Lançamentos, 1 para N com Lançamentos Recorrentes e 1 para N com Logs de Segurança.
* **Regras de manutenção:**
  * Criação via tela de cadastro ou primeiro login Google.
  * E-mail único e obrigatório.
  * Edição permitida para nome e tema visual.
  * Não há exclusão direta de usuário na primeira versão.
* **Auditoria:** Sim (`created_at`, `updated_at`).
* **Soft Delete:** Não aplicável na primeira versão.

### 10.2. Entidade: Conta / Carteira (`Conta`)
* **Finalidade:** Representar um local onde o dinheiro do usuário está custodiado (conta bancária, carteira física, poupança, etc.).
* **Principais informações:** Identificador único, ID do usuário proprietário, nome da conta (único por usuário), saldo inicial informado na abertura, status (`ativo` ou `arquivado`), timestamps de criação e atualização.
* **Relacionamentos funcionais:** Pertence a 1 Usuário; possui 1 para N com Lançamentos (como conta de origem ou como conta de destino em transferências) e 1 para N com Lançamentos Recorrentes.
* **Regras de manutenção:**
  * Criação informando nome e saldo inicial obrigatórios. O sistema valida se o nome já existe para o usuário.
  * Edição permitida para o nome da conta.
  * Exclusão definitiva bloqueada se houver qualquer lançamento vinculado à conta (ativo ou em soft delete); o usuário deve utilizar a ação de arquivar (`status = 'arquivado'`). Possibilidade de reativação a qualquer momento. Exclusão física permitida exclusivamente se a conta nunca teve movimentações.
* **Auditoria:** Sim (`created_at`, `updated_at`).
* **Soft Delete:** Sim (inativação lógica via campo `status = 'arquivado'`).

### 10.3. Entidade: Categoria (`Categoria`)
* **Finalidade:** Classificar a natureza dos ganhos e gastos e possibilitar o acompanhamento orçamentário por centro de custo.
* **Principais informações:** Identificador único, ID do usuário proprietário, nome da categoria (único por usuário e tipo), tipo (`receita` ou `despesa`), teto de orçamento mensal opcional (para despesas), status (`ativo` ou `arquivado`), timestamps de criação e atualização.
* **Relacionamentos funcionais:** Pertence a 1 Usuário; possui 1 para N com Lançamentos e 1 para N com Lançamentos Recorrentes.
* **Regras de manutenção:**
  * O sistema provisiona a lista canônica de categorias padrão (10 itens) no primeiro acesso do usuário.
  * O usuário pode criar novas categorias informando nome e tipo. O sistema valida a unicidade do nome para o mesmo tipo.
  * Edição permitida para nome e valor do teto mensal.
  * Exclusão: Bloqueada se houver qualquer lançamento vinculado no banco (inclusive soft-deletados), a menos que o usuário utilize a rotina de reatribuição em lote para mover todo o histórico (lançamentos ativos, soft-deletados e modelos recorrentes) para outra categoria antes de excluir, ou opte pelo arquivamento.
* **Auditoria:** Sim (`created_at`, `updated_at`).
* **Soft Delete:** Sim (via campo `status = 'arquivado'`).

### 10.4. Entidade: Lançamento (`Lancamento`)
* **Finalidade:** Registrar cada movimentação financeira concreta (receita, despesa ou transferência interna entre contas).
* **Principais informações:** Identificador único, ID do usuário proprietário, tipo (`receita`, `despesa`, `transferencia`), valor monetário (sempre positivo em R$), data de competência (data em que o fato ocorreu ou é contabilizado), data de vencimento (prazo de pagamento/recebimento; em transferências é idêntica à data de competência), descrição, ID da categoria (obrigatório para receita e despesa; nulo em transferência), ID da conta de origem, ID da conta de destino (preenchido apenas em transferências), forma de pagamento (Dinheiro, PIX, Cartão de Débito, Cartão de Crédito, Boleto, Transferência), status (`pago` ou `pendente`), observação textual livre, ID do lançamento recorrente originador (quando aplicável), timestamps de auditoria e data de exclusão lógica (`deleted_at`).
* **Relacionamentos funcionais:** Pertence a 1 Usuário, 1 Categoria (opcional em transferências), 1 Conta de origem, 1 Conta de destino (opcional) e 1 Lançamento Recorrente (opcional).
* **Regras de manutenção:**
  * Criação valida se todos os campos obrigatórios foram preenchidos e se as contas e categorias pertencem ao usuário autenticado.
  * Edição recalcula imediatamente os saldos das contas envolvidas e atualiza os indicadores do dashboard.
  * Exclusão realizada via soft delete (`deleted_at = NOW()`), desfazendo o impacto no saldo realizado se o status era `pago`.
* **Auditoria:** Sim (`created_at`, `updated_at`).
* **Soft Delete:** Sim (via coluna `deleted_at`).

### 10.5. Entidade: Lançamento Recorrente (`LancamentoRecorrente`)
* **Finalidade:** Servir de molde ou modelo para a geração automática de despesas e receitas fixas na virada de cada ciclo mensal.
* **Principais informações:** Identificador único, ID do usuário proprietário, tipo (`receita` ou `despesa`), valor monetário, descrição, ID da categoria, ID da conta preferencial, forma de pagamento padrão, dia de vencimento fixo no mês (1 a 31), indicador de status ativo (booleano), timestamps de criação e atualização.
* **Relacionamentos funcionais:** Pertence a 1 Usuário, 1 Categoria e 1 Conta; possui 1 para N com Lançamentos gerados a partir do modelo.
* **Regras de manutenção:**
  * Permite ao usuário cadastrar contas de água, luz, aluguel, salários e assinaturas fixas.
  * Permite pausar/desativar a recorrência (`ativo = FALSE`) ou reativá-la.
  * Edição do modelo afeta apenas os lançamentos gerados nos meses futuros; não altera os lançamentos já criados no passado.
* **Auditoria:** Sim (`created_at`, `updated_at`).
* **Soft Delete:** Não (utiliza controle por flag `ativo`).

---

## 11. Modelo de Dados Proposto

### 11.1. Estrutura de Tabelas, Campos, Constraints e Tipos (MySQL)

#### Tabela: `usuarios`
* `id` INT UNSIGNED AUTO_INCREMENT NOT NULL — Chave Primária (PK).
* `nome` VARCHAR(150) NOT NULL — Nome completo do usuário.
* `email` VARCHAR(191) NOT NULL — E-mail de login. CONSTRAINT UNIQUE `uk_usuarios_email`.
* `senha_hash` VARCHAR(255) NULL — Hash criptográfico da senha (pode ser nulo para usuários exclusivos do Google).
* `google_id` VARCHAR(100) NULL — Identificador exclusivo fornecido pelo Google OAuth. CONSTRAINT UNIQUE `uk_usuarios_google_id`.
* `tema_preferido` ENUM('dark', 'light') NOT NULL DEFAULT 'dark' — Preferência de tema visual.
* `token_recuperacao` VARCHAR(100) NULL — Token gerado para recuperação de senha.
* `token_recuperacao_expira` DATETIME NULL — Data e hora limite de expiração do token de recuperação.
* `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP — Timestamp de cadastro.
* `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP — Timestamp de alteração.

#### Tabela: `contas`
* `id` INT UNSIGNED AUTO_INCREMENT NOT NULL — Chave Primária (PK).
* `usuario_id` INT UNSIGNED NOT NULL — Chave Estrangeira (FK) referenciando `usuarios(id)` ON DELETE CASCADE.
* `nome` VARCHAR(100) NOT NULL — Nome de exibição da carteira/conta.
* `saldo_inicial` DECIMAL(12, 2) NOT NULL DEFAULT 0.00 — Saldo informado no cadastro da conta.
* `status` ENUM('ativo', 'arquivado') NOT NULL DEFAULT 'ativo' — Status para controle de arquivamento.
* `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP.
* `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP.
* CONSTRAINT UNIQUE `uk_contas_usuario_nome` (`usuario_id`, `nome`).

#### Tabela: `categorias`
* `id` INT UNSIGNED AUTO_INCREMENT NOT NULL — Chave Primária (PK).
* `usuario_id` INT UNSIGNED NOT NULL — Chave Estrangeira (FK) referenciando `usuarios(id)` ON DELETE CASCADE.
* `nome` VARCHAR(100) NOT NULL — Nome da categoria.
* `tipo` ENUM('receita', 'despesa') NOT NULL — Define se a categoria classifica entradas ou saídas.
* `teto_orcamento` DECIMAL(12, 2) NULL DEFAULT NULL — Teto de gastos mensal opcional para controle orçamentário.
* `status` ENUM('ativo', 'arquivado') NOT NULL DEFAULT 'ativo' — Controle de inativação lógica.
* `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP.
* `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP.
* CONSTRAINT UNIQUE `uk_categorias_usuario_nome_tipo` (`usuario_id`, `nome`, `tipo`).

#### Tabela: `lancamentos_recorrentes`
* `id` INT UNSIGNED AUTO_INCREMENT NOT NULL — Chave Primária (PK).
* `usuario_id` INT UNSIGNED NOT NULL — Chave Estrangeira (FK) referenciando `usuarios(id)` ON DELETE CASCADE.
* `tipo` ENUM('receita', 'despesa') NOT NULL — Tipo de movimentação.
* `valor` DECIMAL(12, 2) NOT NULL — Valor fixo previsto.
* `descricao` VARCHAR(150) NOT NULL — Descrição da despesa ou receita recorrente.
* `categoria_id` INT UNSIGNED NOT NULL — Chave Estrangeira (FK) referenciando `categorias(id)` ON DELETE RESTRICT.
* `conta_id` INT UNSIGNED NOT NULL — Chave Estrangeira (FK) referenciando `contas(id)` ON DELETE RESTRICT.
* `forma_pagamento` VARCHAR(50) NOT NULL DEFAULT 'PIX' — Forma de pagamento padrão prevista.
* `dia_vencimento` TINYINT UNSIGNED NOT NULL — Dia do mês para o vencimento (1 a 31).
* `ativo` BOOLEAN NOT NULL DEFAULT TRUE — Indicador de atividade da recorrência.
* `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP.
* `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP.

#### Tabela: `lancamentos`
* `id` INT UNSIGNED AUTO_INCREMENT NOT NULL — Chave Primária (PK).
* `usuario_id` INT UNSIGNED NOT NULL — Chave Estrangeira (FK) referenciando `usuarios(id)` ON DELETE CASCADE.
* `tipo` ENUM('receita', 'despesa', 'transferencia') NOT NULL — Natureza da movimentação.
* `valor` DECIMAL(12, 2) NOT NULL — Valor monetário em R$ (sempre positivo).
* `data_competencia` DATE NOT NULL — Data contábil/efetiva do lançamento.
* `data_vencimento` DATE NOT NULL — Data prevista para vencimento/liquidação. Em registros do tipo `transferencia`, o valor é gravado automaticamente idêntico a `data_competencia`.
* `descricao` VARCHAR(200) NOT NULL — Descrição legível da movimentação.
* `categoria_id` INT UNSIGNED NULL — Chave Estrangeira (FK) referenciando `categorias(id)` ON DELETE RESTRICT (nulo em transferências).
* `conta_id` INT UNSIGNED NOT NULL — Chave Estrangeira (FK) referenciando `contas(id)` ON DELETE RESTRICT (conta de origem).
* `conta_destino_id` INT UNSIGNED NULL — Chave Estrangeira (FK) referenciando `contas(id)` ON DELETE RESTRICT (preenchido exclusivamente em transferências).
* `forma_pagamento` VARCHAR(50) NOT NULL DEFAULT 'Dinheiro' — Forma de pagamento utilizada.
* `status` ENUM('pago', 'pendente') NOT NULL DEFAULT 'pago' — Status de liquidação. Em transferências é sempre registrado como `pago`.
* `observacao` TEXT NULL — Campo opcional para notas textuais livres.
* `recorrente_id` INT UNSIGNED NULL — Chave Estrangeira (FK) referenciando `lancamentos_recorrentes(id)` ON DELETE SET NULL.
* `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP.
* `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP.
* `deleted_at` DATETIME NULL DEFAULT NULL — Data da exclusão lógica (*soft delete*).

#### Tabela: `logs_erros`
* `id` INT UNSIGNED AUTO_INCREMENT NOT NULL — Chave Primária (PK).
* `usuario_id` INT UNSIGNED NULL — FK referenciando `usuarios(id)` ON DELETE SET NULL.
* `nivel` VARCHAR(20) NOT NULL — Nível do log (ERROR, CRITICAL, WARNING).
* `rota` VARCHAR(255) NULL — Endpoint ou URL requisitada.
* `mensagem` TEXT NOT NULL — Mensagem descritiva do erro técnico.
* `stack_trace` MEDIUMTEXT NULL — Detalhamento técnico do rastreamento do erro.
* `ip` VARCHAR(45) NULL — Endereço IP do cliente.
* `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP.

#### Tabela: `logs_seguranca`
* `id` INT UNSIGNED AUTO_INCREMENT NOT NULL — Chave Primária (PK).
* `usuario_id` INT UNSIGNED NULL — FK referenciando `usuarios(id)` ON DELETE SET NULL.
* `evento` VARCHAR(100) NOT NULL — Identificador do evento (ex: LOGIN_INVALIDO, BLOQUEIO_TENTATIVAS, ACESSO_NEGADO_403, RECUPERACAO_SENHA).
* `ip` VARCHAR(45) NULL — Endereço IP de origem.
* `detalhes` TEXT NULL — Detalhes complementares da requisição.
* `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP.

#### Tabela: `migrations_controle`
* `id` INT UNSIGNED AUTO_INCREMENT NOT NULL — Chave Primária (PK).
* `migration_name` VARCHAR(191) NOT NULL — Nome único do arquivo de migração executado. CONSTRAINT UNIQUE `uk_migration_name`.
* `executado_em` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP — Timestamp da execução no banco de dados.

### 11.2. Índices de Desempenho e Otimização de Consultas

Para assegurar carregamento instantâneo do painel, listagens sem lentidão e cálculo ágil de saldos e orçamentos, as seguintes chaves e índices devem ser criados:

1. `idx_lancamentos_usuario_competencia` em `lancamentos (usuario_id, data_competencia, deleted_at)`:
   * **Objetivo:** Otimizar as buscas do Dashboard e listagens mensais que filtram movimentações pelo mês/ano de competência do usuário ativo excluindo os deletados.
2. `idx_lancamentos_usuario_status_vencimento` em `lancamentos (usuario_id, status, data_vencimento, deleted_at)`:
   * **Objetivo:** Acelerar a consulta de contas vencidas e a vencer para o bloco de alertas do Dashboard.
3. `idx_lancamentos_usuario_conta` em `lancamentos (usuario_id, conta_id, deleted_at)`:
   * **Objetivo:** Otimizar o cálculo do saldo em tempo real de cada conta bancária para débitos de despesas, créditos de receitas e saídas de transferências.
4. `idx_lancamentos_usuario_conta_destino` em `lancamentos (usuario_id, conta_destino_id, deleted_at)`:
   * **Objetivo:** Otimizar o cálculo do saldo em tempo real nas entradas de transferências recebidas por uma conta bancária (`conta_destino_id`).
5. `idx_lancamentos_usuario_categoria` em `lancamentos (usuario_id, categoria_id, deleted_at)`:
   * **Objetivo:** Acelerar a consolidação do gráfico de despesas por categoria e verificação de tetos de orçamento.
6. `idx_contas_usuario_status` em `contas (usuario_id, status)`:
   * **Objetivo:** Otimizar a listagem de contas ativas nos seletores de cadastro.
7. `idx_categorias_usuario_tipo_status` em `categorias (usuario_id, tipo, status)`:
   * **Objetivo:** Acelerar a filtragem de categorias por tipo nos formulários.
8. `idx_recorrentes_usuario_ativo` em `lancamentos_recorrentes (usuario_id, ativo)`:
   * **Objetivo:** Agilizar o processamento da virada do mês que busca modelos ativos para geração de lançamentos.

### 11.3. Estratégia de Migrations do Projeto

O banco de dados do FinançasSimples deve ser construído e mantido integralmente através de uma arquitetura de migrations versionadas, eliminando a necessidade de criação manual de tabelas, índices e constraints em ferramentas como phpMyAdmin.

* **Conceito e finalidade:** Cada migration é um arquivo versionado no repositório (alocado em `database/migrations/`) contendo as instruções SQL necessárias para estruturar tabelas, campos, chaves primárias, chaves estrangeiras, índices e sementes iniciais.
* **Prevenção de execução duplicada:** O controle é realizado pela tabela `migrations_controle`. Antes de aplicar qualquer arquivo de migração, o executor verifica se o nome do arquivo já consta gravado nessa tabela. Caso já exista, o arquivo é ignorado; caso não exista, as instruções são executadas em bloco transacional e o registro é inserido.
* **Proteção das migrations:** A pasta `database/migrations/` e o script `database/migrate.py` residem internamente no repositório e **não devem ser acessíveis diretamente pelo navegador**. O acesso direto via URL deve ser expressamente bloqueado pelo `.htaccess` e pela camada de roteamento do Flask.
* **Forma segura de execução:**
  * As migrations devem ser executadas exclusivamente via linha de comando no terminal de desenvolvimento local ou no console bash do PythonAnywhere, através do comando:
    `python database/migrate.py`
  * Não haverá rota pública ou tela web aberta para rodar migrations, prevenindo ataques de injeção ou execuções indevidas em produção.

---

## 12. Módulos e Telas

A interface do usuário adota estritamente as diretrizes do documento de design (*High-Contrast Dark* / Obsidian: fundo near-black `#09090b`, primário violeta suave `#a78bfa`, bordas zinc `1px solid #27272a`, cards com 8px de raio e tipografia Geist), com alternância acessível para tema claro em escala zinc correspondente.

### 12.1. Tela de Login e Cadastro (`/login`, `/cadastro`)
* **Objetivo:** Identificar o usuário e autenticá-lo no sistema.
* **Usuários que acessam:** Visitantes e usuários cadastrados deslogados.
* **Endpoints consumidos:** `POST /api/auth/login`, `POST /api/auth/cadastro`, `GET /api/auth/google`.
* **Principais informações:** Logotipo do FinançasSimples, formulário com campos de E-mail e Senha (e Nome no cadastro), botão de ação primário ("Entrar" ou "Criar Conta"), divisor sutil ("ou"), botão de ação com o Google ("Continuar com o Google" com logotipo oficial do Google) e link secundário para "Esqueci minha senha".
* **Mensagens esperadas:** Alertas de validação em vermelho (`#ef4444`) para credenciais inválidas ou e-mail já cadastrado; mensagem de sucesso em verde (`#34d399`) após criação de conta.
* **Estados:** Normal, Carregando (botão desabilitado com indicador de processamento), Erro de validação.

### 12.2. Tela de Recuperação de Senha (`/recuperar-senha`, `/redefinir-senha/<token>`)
* **Objetivo:** Permitir ao usuário recuperar o acesso caso tenha esquecido sua senha.
* **Usuários que acessam:** Usuários com e-mail cadastrado.
* **Endpoints consumidos:** `POST /api/auth/recuperar-senha`, `POST /api/auth/redefinir-senha`.
* **Principais informações:** Campo para digitação do e-mail cadastrado, instruções claras de envio de link e, na tela do link, campos para nova senha e confirmação.
* **Mensagens esperadas:** Mensagem amigável de que o link foi enviado (sem revelar se o e-mail existe no banco para mitigar enumeração de contas); alerta de erro caso o token tenha expirado ou seja inválido.

### 12.3. Painel Principal (Dashboard) (`/dashboard`)
* **Objetivo:** Oferecer a visão central e imediata do mês selecionado.
* **Usuários que acessam:** Usuário Pessoal autenticado.
* **Endpoints consumidos:** `GET /api/dashboard/resumo?mes=X&ano=Y`, `PATCH /api/lancamentos/<id>/pagar`.
* **Componentes e informações exibidas:**
  * **Barra de navegação de período:** Seletor de mês e ano com setas para avançar/retroceder e indicação visual do mês vigente (ex: "Setembro de 2026").
  * **Cartões de Indicadores (Métricas):**
    * *Saldo do Mês:* Valor em destaque calculado como (Receitas Pagas - Despesas Pagas). Cor verde esmeralda (`#34d399`) para saldo positivo e vermelho (`#ef4444`) para negativo.
    * *Receitas do Mês:* Somatório das receitas com status pago ou previsto.
    * *Despesas do Mês:* Somatório das despesas com status pago ou previsto.
  * **Gráfico de Despesas por Categoria:** Gráfico de barras simples, elegante e monocromático (utilizando gradientes de violeta `#a78bfa` e tons zinc), indicando a proporção de gastos em cada categoria de despesa no mês.
  * **Bloco de Alertas de Vencimento:** Bloco com lista rápida de lançamentos pendentes vencidos (destacados em vermelho `#ef4444`) e contas que vencem nos próximos 5 dias (destacadas com indicador de atenção), acompanhados de botão rápido de "Marcar como Pago".
  * **Botão Flutuante / Ação Rápida:** Botão de destaque violeta "+ Novo Lançamento" para abertura rápida do formulário de movimentação.
* **Estados:** Estado vazio com mensagem incentivadora caso o mês não possua lançamentos; estado de carregamento esqueleto (*skeleton loader*) ao alternar períodos.

### 12.4. Módulo de Lançamentos (`/lancamentos`)
* **Objetivo:** Gestão detalhada, filtragem e busca de todas as movimentações financeiras.
* **Usuários que acessam:** Usuário Pessoal autenticado.
* **Endpoints consumidos:** `GET /api/lancamentos?mes=X&ano=Y&conta=Z&status=W&busca=T`, `DELETE /api/lancamentos/<id>`.
* **Componentes e informações exibidas:**
  * Barra de filtros superiores: Seletor de período (mês/ano), dropdown de contas, dropdown de categorias, seletor de tipo (Todos, Receitas, Despesas, Transferências) e seletor de status (Todos, Pago, Pendente).
  * Campo de busca textual rápida (filtra por descrição em tempo real).
  * Tabela ou lista de lançamentos em estilo card para mobile, exibindo: data, descrição, categoria, conta, forma de pagamento, valor (formatado em R$) com indicação visual (+ verde para receita, - padrão/vermelho para despesa, neutro para transferência), badge de status (`Pago` ou `Pendente`) e botões de ação rápida (Editar, Alternar Status e Excluir).
* **Estados:** Carregando, Lista vazia ("Nenhum lançamento encontrado para os filtros selecionados"), Lista preenchida.

### 12.5. Modal/Formulário de Cadastro e Edição de Lançamento
* **Objetivo:** Registrar ou atualizar receitas, despesas e transferências.
* **Endpoints consumidos:** `POST /api/lancamentos`, `PUT /api/lancamentos/<id>`, `POST /api/lancamentos/transferencia`.
* **Campos do formulário:**
  * Abas no topo: [Despesa] | [Receita] | [Transferência].
  * Se Despesa ou Receita: Valor (R$), Data de Competência, Data de Vencimento, Descrição, Categoria (select), Conta/Carteira (select), Forma de Pagamento (select), Status (checkbox ou botão alternador "Já foi pago?"), Observações (textarea opcional).
  * Se Transferência: Valor (R$), Data, Conta de Origem (select), Conta de Destino (select), Observações (opcional).
* **Botões e ações:** Botão primário "Salvar Lançamento" e botão secundário "Cancelar".

### 12.6. Módulo de Contas e Carteiras (`/contas`)
* **Objetivo:** Visualizar e cadastrar locais de custódia do dinheiro e seus respectivos saldos.
* **Endpoints consumidos:** `GET /api/contas`, `POST /api/contas`, `PUT /api/contas/<id>`, `PATCH /api/contas/<id>/arquivar`, `PATCH /api/contas/<id>/reativar`, `DELETE /api/contas/<id>`.
* **Componentes e informações exibidas:**
  * Cartão de saldo consolidado somando todas as contas ativas.
  * Grade de cartões de contas exibindo: nome da conta, badge indicativo (ativa/arquivada), saldo atualizado calculado e menu de ações (Editar Nome, Arquivar/Reativar e Excluir quando sem movimentações vinculadas).
  * Botão "+ Nova Conta": Abre modal com campos Nome da Conta e Saldo Inicial.

### 12.7. Módulo de Categorias e Orçamentos (`/categorias`)
* **Objetivo:** Gerenciar as categorias de despesas e receitas e configurar os tetos mensais de orçamento.
* **Endpoints consumidos:** `GET /api/categorias`, `POST /api/categorias`, `PUT /api/categorias/<id>`, `PATCH /api/categorias/<id>/arquivar`, `POST /api/categorias/<id>/reatribuir-excluir`, `DELETE /api/categorias/<id>`.
* **Componentes e informações exibidas:**
  * Duas seções bem demarcadas: Categorias de Despesa e Categorias de Receita.
  * Para cada categoria de despesa: Nome, barra de progresso visual do orçamento (mostrando quanto foi gasto no mês versus o teto estipulado e porcentagem consumida) e indicador de alerta caso o teto seja ultrapassado (> 100%).
  * Botões de ação: Editar, Definir/Remover Teto, Arquivar e Excluir.
  * Botão "+ Nova Categoria": Formulário para nome, tipo e teto opcional.
  * Modal de Reatribuição em Lote: Disparado ao tentar excluir uma categoria que possui lançamentos vinculados no banco, exigindo que o usuário selecione uma nova categoria de destino para transferir todo o histórico ou cancele a exclusão.

### 12.8. Módulo de Lançamentos Recorrentes (`/recorrentes`)
* **Objetivo:** Cadastrar e monitorar despesas e receitas fixas que se repetem todo mês.
* **Endpoints consumidos:** `GET /api/recorrentes`, `POST /api/recorrentes`, `PUT /api/recorrentes/<id>`, `DELETE /api/recorrentes/<id>`, `PATCH /api/recorrentes/<id>/toggle`.
* **Componentes e informações exibidas:**
  * Lista de modelos fixos ativos e inativos exibindo descrição, tipo, valor, categoria, conta preferencial, dia de vencimento (ex: "Todo dia 10") e chave seletora (*toggle switch*) de Ativo/Inativo.
  * Botão "+ Novo Fixo".

### 12.9. Tela de Configurações e Perfil (`/configuracoes`)
* **Objetivo:** Gerenciar dados da conta e preferências visuais.
* **Endpoints consumidos:** `GET /api/usuario/perfil`, `PATCH /api/usuario/tema`.
* **Componentes e informações exibidas:**
  * Dados do perfil: Nome completo e E-mail (somente leitura ou edição básica de nome).
  * Seletor de Tema Visual: Alternador manual com ícones [Sol - Tema Claro] e [Lua - Tema Escuro], refletindo imediatamente na interface.

---

## 13. Fluxos Funcionais

### 13.1. Autenticação e Acesso

#### 13.1.1. Fluxo de Cadastro de Novo Usuário (Tradicional)
* **Perfil:** Usuário Pessoal (visitante).
* **Pré-condições:** Usuário não cadastrado com acesso à rota `/cadastro`.
* **Passo a passo:**
  1. O usuário acessa a tela de cadastro e preenche os campos: Nome completo, E-mail, Senha e Confirmação de senha.
  2. O usuário clica em "Criar Minha Conta".
  3. O frontend valida o preenchimento obrigatório, formato de e-mail e confere se a senha possui no mínimo 8 caracteres e coincide com a confirmação.
  4. O frontend submete requisição `POST /api/auth/cadastro`.
  5. O backend verifica se o e-mail informado já existe na tabela `usuarios`. Se existir, retorna erro HTTP 400 com a mensagem: "Este endereço de e-mail já está cadastrado".
  6. O backend gera o hash criptográfico seguro da senha via `werkzeug.security.generate_password_hash`.
  7. O backend insere o novo registro na tabela `usuarios` com `tema_preferido = 'dark'`.
  8. Em uma transação atômica, o backend provisiona:
     * A lista canônica das 10 categorias padrão vinculadas ao novo `usuario_id` (Receitas: Salário, Rendimentos, Outras Receitas; Despesas: Alimentação, Moradia, Transporte, Saúde, Educação, Lazer, Outras Despesas);
     * A carteira padrão inicial vinculada ao usuário: Nome *"Carteira"*, Saldo Inicial `0.00`, Status `'ativo'`, viabilizando a inserção imediata de lançamentos.
  9. O backend inicializa a sessão do usuário gravando o cookie HTTP-only assinado e retorna resposta de sucesso.
  10. O frontend recebe a confirmação e redireciona automaticamente o usuário para o `/dashboard`.

#### 13.1.2. Fluxo de Login Tradicional
* **Perfil:** Usuário Pessoal (cadastrado).
* **Passo a passo:**
  1. O usuário acessa `/login`, informa e-mail e senha cadastrados e clica em "Entrar".
  2. O frontend envia requisição `POST /api/auth/login`.
  3. O backend busca o usuário pelo e-mail e valida o hash da senha via `werkzeug.security.check_password_hash`.
  4. Se as credenciais estiverem corretas, o backend zera o contador de tentativas falhas, inicializa a sessão Flask e responde com sucesso. O frontend redireciona para o `/dashboard`.
  5. Se as credenciais estiverem incorretas, incrementa o contador de falhas daquele IP/e-mail, grava o evento `LOGIN_INVALIDO` na tabela `logs_seguranca` e retorna erro HTTP 401 ("E-mail ou senha incorretos").

#### 13.1.3. Fluxo de Autenticação com Conta Google (OAuth 2.0)
* **Perfil:** Usuário Pessoal (visitante ou cadastrado).
* **Passo a passo:**
  1. O usuário clica no botão "Continuar com o Google".
  2. O backend gera o redirecionamento para a URL de consentimento oficial do Google com os escopos `openid`, `email` e `profile`.
  3. O usuário autoriza o compartilhamento de dados nos servidores do Google.
  4. O Google redireciona para a rota `/api/auth/google/callback` com o código de autorização.
  5. O backend troca o código pelo token de autenticação, valida a assinatura e extrai o `google_id`, `email` e `name`.
  6. O backend verifica se o e-mail já existe na base:
     * Se não existir: cria o usuário em `usuarios`, vincula o `google_id` e provisiona em bloco atômico as 10 categorias padrão canônicas e a carteira padrão inicial (*"Carteira"* com saldo `0.00`).
     * Se já existir: atualiza o registro associando o `google_id`.
  7. Inicializa a sessão segura e redireciona o usuário para o `/dashboard`.

### 13.2. Fluxo de Registro de Nova Movimentação (Receita ou Despesa)
* **Perfil:** Usuário Pessoal autenticado.
* **Pré-condições:** O usuário possui ao menos uma conta cadastrada.
* **Passo a passo:**
  1. O usuário clica no botão "+ Novo Lançamento" no Dashboard ou tela de Lançamentos.
  2. O modal é exibido com foco no campo de valor.
  3. O usuário seleciona o tipo (Receita ou Despesa), digita o valor em R$, data de competência, data de vencimento, descrição, escolhe a categoria e a conta bancária e define se o item já foi liquidado (`pago`) ou está em aberto (`pendente`).
  4. O usuário clica em "Salvar Lançamento".
  5. O frontend valida os campos e envia requisição `POST /api/lancamentos`.
  6. O Controller verifica a sessão, valida se a conta e a categoria pertencem ao `current_user.id` e grava a linha na tabela `lancamentos`.
  7. Se o status for `pago`, o saldo da conta selecionada é recalculado no painel.
  8. O modal se fecha e a listagem e os indicadores do dashboard são atualizados instantaneamente em tela.
* **Erros possíveis:** Conta ou categoria inexistente/pertencente a outro usuário (erro 403), valor menor ou igual a zero, data inválida.

### 13.3. Fluxo de Transferência entre Contas Próprias
* **Perfil:** Usuário Pessoal autenticado.
* **Pré-condições:** O usuário possui ao menos duas contas ativas cadastradas.
* **Passo a passo:**
  1. O usuário abre o formulário de lançamentos e seleciona a aba "Transferência".
  2. O formulário exibe os campos específicos: Valor, Data da Transferência, Conta de Origem e Conta de Destino.
  3. O usuário preenche os campos, certificando-se de que a conta de origem e destino sejam diferentes.
  4. O usuário clica em "Confirmar Transferência".
  5. O frontend submete requisição `POST /api/lancamentos/transferencia`.
  6. O backend valida a operação: garante que ambas as contas pertencem ao usuário autenticado e registra um lançamento com:
     * `tipo = 'transferencia'`;
     * `conta_id` = conta de origem;
     * `conta_destino_id` = conta de destino;
     * `categoria_id = NULL`;
     * `data_competencia` = data informada;
     * `data_vencimento` = data informada (mesmo valor de `data_competencia`);
     * `status = 'pago'`.
  7. O sistema debita o valor no saldo da conta de origem e credita o mesmo valor na conta de destino.
  8. O somatório de receitas e despesas gerais do mês permanece inalterado.
  9. A tela exibe confirmação de sucesso com os saldos individuais das duas carteiras recalculados.
* **Erros possíveis:** Conta de origem idêntica à conta de destino (bloqueio imediato com aviso "A conta de destino deve ser diferente da conta de origem").

### 13.4. Fluxo de Processamento Automático de Lançamentos Recorrentes
* **Perfil:** Usuário Pessoal autenticado.
* **Pré-condições:** Modelos de lançamentos fixos configurados e ativos na tabela `lancamentos_recorrentes`.
* **Passo a passo:**
  1. Ao acessar qualquer tela principal que carregue dados financeiros do período — especificamente o Dashboard (`GET /api/dashboard/resumo`) ou a listagem de lançamentos (`GET /api/lancamentos`) —, o sistema aciona a rotina interna e atômica de verificação de recorrências.
  2. O sistema consulta se já existem lançamentos gerados no mês corrente para cada modelo recorrente ativo (`recorrente_id = modelo.id` e competência no mês/ano atual).
  3. Para cada modelo recorrente que ainda não teve lançamento gerado no mês vigente, o sistema calcula a data de vencimento:
     * Se o `dia_vencimento` do modelo for maior que a quantidade de dias do mês corrente (ex: dia 31 em abril ou em fevereiro), a data de vencimento e competência é ajustada automaticamente para o último dia válido daquele mês (ex: 30 de abril ou 28/29 de fevereiro).
     * Caso contrário, utiliza o próprio `dia_vencimento` no mês/ano atual.
  4. O sistema insere o registro na tabela `lancamentos` com:
     * Descrição, valor, categoria, conta e forma de pagamento copiados do modelo;
     * Data de competência e data de vencimento calculadas conforme a regra de virada de mês;
     * Status inicial definido como `pendente`;
     * Vínculo com `recorrente_id`.
  5. O usuário visualiza esses lançamentos já disponíveis tanto na sua listagem quanto no bloco de alertas de contas a vencer, sincronizados independente da tela pela qual acessou o sistema.

### 13.5. Fluxo de Monitoramento de Tetos de Orçamento
* **Perfil:** Usuário Pessoal autenticado.
* **Pré-condições:** Categoria de despesa com teto de orçamento mensal cadastrado.
* **Passo a passo:**
  1. Ao registrar uma nova despesa ou ao carregar a tela de Categorias e Dashboard, o sistema soma o total de despesas daquela categoria no mês selecionado.
  2. O sistema calcula a razão percentual: `(Total Gasto / Teto) * 100`.
  3. Se o total gasto for menor que 80%, a barra exibe progresso normal em violeta suave.
  4. Se o total atingir entre 80% e 99%, exibe alerta visual sutil de proximidade do limite.
  5. Se o total atingir ou ultrapassar 100%, o sistema destaca visualmente a categoria com borda de aviso em vermelho (`#ef4444`) e badge informativo indicando o montante excedido.

### 13.6. Fluxo de Exclusão de Categoria com Reatribuição em Lote e Preservação de Integridade
* **Perfil:** Usuário Pessoal autenticado.
* **Pré-condições:** Categoria que o usuário deseja excluir possui lançamentos históricos vinculados.
* **Passo a passo:**
  1. Na tela de Categorias, o usuário clica no botão "Excluir" de uma categoria existente.
  2. O backend verifica a existência de vínculos físicos na tabela `lancamentos` através da consulta:
     `SELECT COUNT(*) FROM lancamentos WHERE categoria_id = :cat_id AND usuario_id = :user_id` (avaliando todos os registros, independentemente de `deleted_at`, além de referências em `lancamentos_recorrentes`).
  3. **Cenário A — Sem lançamentos vinculados:** Se a contagem for exatamente 0, o sistema realiza a exclusão física imediata da categoria com sucesso (`DELETE FROM categorias WHERE id = :cat_id`).
  4. **Cenário B — Com lançamentos vinculados:** Se a contagem for maior que 0, a exclusão física direta é bloqueada devido à constraint relacional (`ON DELETE RESTRICT`). O sistema abre o modal explicativo: *"Esta categoria possui movimentações registradas no histórico. Para excluí-la, você deve transferir essas movimentações para outra categoria ativa ou optar pelo arquivamento."*
  5. O modal apresenta um seletor com as outras categorias ativas de mesmo tipo (receita ou despesa).
  6. O usuário seleciona a categoria de destino e clica em "Reatribuir e Excluir".
  7. O frontend envia requisição `POST /api/categorias/<id>/reatribuir-excluir` informando a `nova_categoria_id`.
  8. Em uma **transação atômica única** (`BEGIN TRANSACTION`):
     * Reatribui todos os lançamentos (ativos e soft-deletados) do usuário para a nova categoria:
       `UPDATE lancamentos SET categoria_id = :nova_categoria_id WHERE categoria_id = :antiga_categoria_id AND usuario_id = :user_id`;
     * Reatribui os modelos recorrentes vinculados:
       `UPDATE lancamentos_recorrentes SET categoria_id = :nova_categoria_id WHERE categoria_id = :antiga_categoria_id AND usuario_id = :user_id`;
     * Remove a categoria antiga com segurança e sem falhas de foreign key:
       `DELETE FROM categorias WHERE id = :antiga_categoria_id AND usuario_id = :user_id`.
  9. A transação é confirmada (`COMMIT`), a lista é atualizada e a integridade de dados permanece absoluta.

### 13.7. Fluxo de Arquivamento e Reativação de Conta/Carteira
* **Perfil:** Usuário Pessoal autenticado.
* **Passo a passo (Arquivamento):**
  1. Na tela de Contas, o usuário seleciona a opção "Arquivar" em uma carteira que não utiliza mais.
  2. O sistema exibe modal informativo: "Arquivar esta conta ocultará a carteira dos seletores de novos lançamentos, mas preservará integralmente seu histórico financeiro passado. Deseja continuar?"
  3. O usuário confirma a ação.
  4. O frontend envia requisição `PATCH /api/contas/<id>/arquivar`.
  5. O backend atualiza `contas SET status = 'arquivado' WHERE id = :id AND usuario_id = :user_id`.
  6. A conta passa a ser exibida na seção de "Contas Arquivadas" e não aparece mais nas opções de cadastro de novos lançamentos.
* **Passo a passo (Reativação):**
  1. Na seção de contas arquivadas, o usuário clica em "Reativar".
  2. O backend atualiza `status = 'ativo'`. A carteira retorna imediatamente aos seletores normais de movimentações.

### 13.8. Fluxo de Alternância de Tema Visual (Claro / Escuro)
* **Perfil:** Usuário Pessoal autenticado.
* **Passo a passo:**
  1. O usuário clica no botão seletor de tema no cabeçalho ou nas configurações.
  2. O frontend alterna dinamicamente a classe CSS raiz da aplicação (adicionando ou removendo o modificador do tema claro sobre a base zinc) e altera a imagem do logotipo exibido (`logo_tema_escuro.png` para tema escuro e `logo_tema_claro.png` para tema claro).
  3. O frontend grava a preferência imediatamente no armazenamento local (`localStorage`) e envia requisição assíncrona `PATCH /api/usuario/tema` com o novo valor (`dark` ou `light`).
  4. O backend persiste a preferência na coluna `tema_preferido` da tabela `usuarios`.
  5. Em acessos futuros em qualquer dispositivo, o sistema inicializa com o tema e a logotipo correspondente salvos no perfil.

---

## 14. Validações e Regras de Negócio

### 14.1. Regras de Campos Obrigatórios e Formatos
* **E-mail:** Obrigatório, deve atender ao formato padrão de e-mail RFC e ser único no sistema (`uk_usuarios_email`).
* **Senha:** Obrigatória no cadastro tradicional, tamanho mínimo de 8 caracteres.
* **Nomes de Contas:** Obrigatórios, tamanho entre 2 e 100 caracteres, únicos por usuário (`uk_contas_usuario_nome`).
* **Nomes de Categorias:** Obrigatórios, tamanho entre 2 e 100 caracteres, únicos por usuário e por tipo (`uk_categorias_usuario_nome_tipo`).
* **Valores monetários:** Obrigatórios em lançamentos, contas e orçamentos. Devem ser numéricos decimais estritamente positivos (> 0.00), armazenados com 2 casas decimais no formato do Real brasileiro (R$).
* **Datas:** Obrigatórias nos formatos padrão ISO `AAAA-MM-DD` internamente e exibidas na interface como `DD/MM/AAAA`. A data de competência e a data de vencimento são obrigatórias em todo lançamento. Em transferências, `data_vencimento` assume o mesmo valor de `data_competencia`.
* **Descrições:** Obrigatórias, tamanho entre 2 e 200 caracteres, tratadas contra caracteres de injeção e tags HTML.

### 14.2. Regras de Negócio Financeiras
1. **Isolamento de Transferências:** Operações de transferência entre contas debitam a conta de origem e creditam a conta de destino, afetando exclusivamente o saldo das duas contas envolvidas. Em hipótese alguma o valor transferido deve ser somado como receita ou despesa nos indicadores gerais do Dashboard.
2. **Cálculo de Saldo Realizado de Conta:** O saldo de qualquer conta é a soma algébrica de:
   $$\text{Saldo Atual} = \text{Saldo Inicial} + \sum(\text{Receitas Pagas}) - \sum(\text{Despesas Pagas}) + \sum(\text{Transferências Recebidas}) - \sum(\text{Transferências Enviadas})$$
   Lançamentos com status `pendente` ou com `deleted_at IS NOT NULL` não compõem o saldo realizado.
3. **Cálculo do Saldo Líquido Mensal do Dashboard:**
   $$\text{Saldo Líquido Mensal} = \sum(\text{Receitas do Mês}) - \sum(\text{Despesas do Mês})$$
4. **Proteção de Integridade por Vínculo Histórico:** Nenhuma conta bancária que possua movimentações cadastradas pode ser removida fisicamente do banco de dados. A ação padrão é o arquivamento (`status = 'arquivado'`), garantindo que o extrato e a conciliação do passado permaneçam inalterados.
5. **Destaque Visual de Vencimentos em Atraso:** Todo lançamento que cumprir a condição simultânea `status = 'pendente'` E `data_vencimento < CURRENT_DATE()` é automaticamente classificado como "Em Atraso" e recebe destaque visual em vermelho (`#ef4444`) no bloco de alertas.
6. **Proteção contra Saldo Negativo na Transferência:** O sistema emite alerta preventivo caso o valor da transferência seja superior ao saldo atual da conta de origem, exigindo confirmação explícita do usuário antes de efetivar o débito.
7. **Tratamento de Dias em Lançamentos Recorrentes:** Quando o dia de vencimento de uma recorrência for superior ao último dia do mês corrente (ex: dia 31 em fevereiro ou meses de 30 dias), o sistema gera o lançamento com competência e vencimento no último dia válido daquele mês.

---

## 15. Autenticação e Sessão

* **Tipo de autenticação:** Híbrida (E-mail/senha tradicional com hash forte e Google OAuth 2.0 / OpenID Connect).
* **Fluxo de Login:**
  * Endpoint `POST /api/auth/login` recebe e valida as credenciais.
  * Senhas verificadas via funções nativas seguras de hash (`werkzeug.security.check_password_hash` com algoritmos adaptativos `scrypt` ou `pbkdf2:sha256`).
  * No sucesso, o identificador do usuário é armazenado na sessão segura do Flask.
* **Fluxo de Logout:**
  * Endpoint `POST /api/auth/logout` destrói os dados da sessão no servidor, limpa o cookie de autenticação do cliente e responde confirmação para redirecionamento à tela de login.
* **Recuperação de Acesso e Envio de E-mails:**
  * O usuário solicita recuperação informando o e-mail na rota `POST /api/auth/recuperar-senha`.
  * O sistema gera um token pseudo-aleatório criptográfico de uso único com validade de 60 minutos, grava o hash do token e timestamp em `usuarios`, e dispara o link para o e-mail cadastrado através das configurações SMTP definidas em `config/config.py`.
  * **Comportamento em Desenvolvimento Local:** Caso as credenciais de SMTP não estejam configuradas no ambiente local, o sistema captura a condição de forma segura e imprime o link completo de recuperação no console/log de desenvolvimento, permitindo testes completos e fluidos de ponta a ponta sem bloqueios.
  * Na rota `POST /api/auth/redefinir-senha`, o usuário insere a nova senha acompanhada do token, a qual é atualizada no banco, invalidando o token utilizado.
* **Proteção contra Força Bruta:**
  * Se houver 5 tentativas consecutivas de login inválidas para o mesmo e-mail ou IP em um intervalo de 15 minutos, o sistema bloqueia novas tentativas por 15 minutos e grava um registro de severidade alta na tabela `logs_seguranca`.
* **Gerenciamento de Sessão:**
  * Cookies de sessão gerados com os atributos: `HttpOnly = True` (inibe acesso por JavaScript malicioso), `SameSite = 'Lax'` (mitiga ataques de CSRF) e `Secure = True` quando em ambiente HTTPS/produção.
  * Sessão configurada para expiração persistente padrão (permanece ativa enquanto o usuário navegar com frequência, expirando apenas após inatividade prolongada ou logout voluntário).
* **Proteção de Rotas:**
  * Todas as rotas de backend sob `/api/*` (exceto `/api/auth/login`, `/api/auth/cadastro`, `/api/auth/recuperar-senha`, `/api/auth/redefinir-senha` e `/api/auth/google*`) e rotas privadas são protegidas pelo decorador de autorização `@login_required`.
  * Requisições não autenticadas em rotas web são redirecionadas para `/login`; requisições não autenticadas enviadas para endpoints de API retornam imediatamente resposta JSON com status HTTP 401 Unauthorized.

---

## 16. Controle de Acesso

* **Modelo:** Isolamento estrito de painel pessoal (Single-Tenant lógico por ID de usuário).
* **Papéis:** Perfil único `Usuário Pessoal`. Não há papéis de superusuário ou administrador que possam visualizar dados financeiros alheios na interface web.
* **Menus por perfil:** A interface exibe menu de navegação direcionado ao próprio painel do usuário:
  * Início / Dashboard
  * Lançamentos
  * Contas / Carteiras
  * Categorias e Orçamentos
  * Lançamentos Fixos (Recorrentes)
  * Configurações / Perfil
  * Sair (Logout)
* **Telas e Ações Bloqueadas:**
  * Não há telas públicas além das de autenticação.
  * Nenhuma ação de listagem, inserção, alteração ou exclusão pode ser executada sem a verificação do vínculo entre o registro e o usuário da sessão ativa.
* **Validação de Propriedade no Backend:**
  * Antes de atualizar ou excluir qualquer lançamento, conta ou categoria (`id = :id`), o controller executa a checagem:
    `SELECT id FROM entidade WHERE id = :id AND usuario_id = :current_user_id`
  * Se o registro não for encontrado ou pertencer a outro ID, o sistema aborta a operação, gera log de segurança de tentativa de acesso indevido e retorna status HTTP 403 Forbidden.
* **Mensagens para acesso negado:**
  * A interface exibe mensagem amigável: "Acesso não autorizado. Você não possui permissão para acessar ou alterar este recurso."

---

## 17. Auditoria e Histórico

* **Registros auditados:** Todas as transações financeiras e cadastros centrais: `usuarios`, `contas`, `categorias`, `lancamentos_recorrentes` e `lancamentos`.
* **Ações auditadas:** Inserções, alterações de dados e exclusões lógicas.
* **Campos mínimos obrigatórios:**
  * `created_at`: Data e hora exata da criação do registro.
  * `updated_at`: Data e hora da última alteração.
  * `deleted_at`: Data e hora da exclusão lógica (em `lancamentos`).
* **Visualização da auditoria:**
  * No detalhamento ou modal de edição de lançamentos e contas, é exibida discretamente uma linha informativa: "Criado em DD/MM/AAAA às HH:MM | Atualizado em DD/MM/AAAA às HH:MM".
* **Retenção de histórico:**
  * Os dados financeiros pertencentes a um usuário são mantidos perpetuamente enquanto sua conta estiver ativa, permitindo a navegação retroativa para qualquer mês de anos anteriores.

---

## 18. Soft Delete e Exclusões

* **Entidades que utilizam Soft Delete:**
  * `lancamentos`: Utiliza coluna `deleted_at DATETIME NULL`. Registros com data preenchida são considerados excluídos e ignorados nas consultas regulares (`WHERE deleted_at IS NULL`).
  * `contas`: Utiliza o mecanismo de inativação lógica via campo `status = 'arquivado'`. A conta deixa de ser exibida nas listas de seleção para novos lançamentos, mas permanece no banco para garantir que transações passadas não fiquem órfãs.
  * `categorias`: Utiliza inativação lógica via `status = 'arquivado'` ou reatribuição em lote de histórico antes da exclusão física.
  * `lancamentos_recorrentes`: Utiliza desativação lógica através do campo booleano `ativo = FALSE`.
* **Permissão de exclusão:**
  * O próprio usuário pode solicitar a exclusão de seus lançamentos e categorias sem vínculos.
* **Restauração e Exclusão Definitiva:**
  * Não há lixeira pública ou tela de restauração na primeira versão do sistema. Uma vez que o lançamento é excluído pelo usuário, a exclusão lógica garante que ele não reapareça na interface e seu impacto financeiro é revertido.
  * Não há rotina de exclusão física definitiva no banco na primeira versão para registros com movimentações, assegurando a integridade e rastreabilidade para suporte técnico em contingência.
* **Cuidados contra exclusão indevida:**
  * Toda ação de exclusão no frontend exige confirmação explícita do usuário através de modal de segurança com texto de confirmação (ex: "Tem certeza de que deseja excluir este lançamento de R$ 150,00? O saldo da conta será recalculado automaticamente.").

---

## 19. Logs

### 19.1. Log de Erros

* **Erros registrados:** Falhas de execução não tratadas (exceções 500), erros de sintaxe ou restrições de banco de dados MySQL, exceções de comunicação com a API do Google OAuth e erros em rotinas de cálculo.
* **Informações gravadas:**
  * Data e hora exatas do evento;
  * Nível de severidade (`ERROR`, `CRITICAL`);
  * Rota/Endpoint HTTP solicitado e método (GET/POST/PUT/DELETE);
  * Mensagem descritiva da exceção;
  * Rastreamento detalhado da pilha de execução (*stack trace*);
  * Identificador do usuário (`usuario_id`), se autenticado;
  * Endereço IP do cliente requisitante.
* **Destino primário:** Tabela `logs_erros` no banco de dados MySQL.
* **Mecanismo de contingência em arquivo:**
  * Se ocorrer falha crítica de conexão com o MySQL, indisponibilidade do serviço do banco ou erro durante a própria gravação na tabela `logs_erros`, o sistema aciona automaticamente a contingência via módulo nativo `logging` do Python.
  * O erro é gravado no arquivo: `logs/error.log`.
  * A pasta `logs/` reside internamente dentro do `[Diretório do Projeto - Repositório]`, protegida por diretivas de servidor (`.htaccess`) para impedir qualquer acesso ou leitura por URL web.
* **Apresentação segura ao usuário final:**
  * O usuário final nunca recebe telas de depuração (*debug screens*), códigos de erro de banco ou trechos de código-fonte. A resposta ao usuário é sempre uma mensagem amigável: "Ocorreu um erro interno ao processar sua solicitação. A equipe técnica já foi notificada. Por favor, tente novamente em instantes."

### 19.2. Log de Segurança

* **Eventos monitorados e registrados:**
  * Tentativas de login falhas (e-mail incorreto ou senha divergente);
  * Bloqueio temporário de IP/e-mail por excesso de tentativas consecutivas (defesa contra força bruta);
  * Tentativas de violação de isolamento de dados (tentativa de acessar ID de conta, categoria ou lançamento pertencente a outro usuário — HTTP 403);
  * Solicitações e confirmações de redefinição de senha;
  * Tentativas de requisição a arquivos ou rotas protegidas sem autenticação ativa.
* **Informações gravadas:**
  * Data e hora do evento;
  * Nome padronizado do evento (ex: `LOGIN_FAILED`, `BRUTE_FORCE_BLOCKED`, `ACCESS_DENIED_IDOR`, `PASSWORD_RESET_REQ`);
  * Endereço IP do cliente;
  * `usuario_id` associado (quando conhecido);
  * Detalhes complementares (ex: e-mail utilizado na tentativa, ID do recurso violado).
* **Destino:** Tabela estruturada `logs_seguranca` no banco de dados MySQL.

---

## 20. Configurações Globais

### 20.1. Configurações do Sistema e Perfil do Usuário
* **Preferência de Tema Visual:** Configuração de tema (`dark` ou `light`). Valor padrão: `dark`. O usuário pode alterar a qualquer momento no cabeçalho ou menu de configurações.
* **Símbolo de Moeda:** Fixo e imutável para `R$` (Real brasileiro).
* **Formatação Numérica:** Padrão brasileiro: separador de milhar por ponto (`.`) e separador de decimais por vírgula (`,`).
* **Fallback de Configuração:** Se a preferência de tema do usuário estiver indefinida no banco, a aplicação adota automaticamente o padrão `dark` (*High-Contrast Dark*).

### 20.2. Estratégia de Configuração Técnica (Sem Uso de `.env`)

* **Diretriz de Segurança Mandatória:** **É terminantemente proibido o uso de arquivos de extensão `.env` para armazenamento de configurações e credenciais neste projeto.**
* **Justificativa técnica:** Arquivos `.env` podem ser servidos como texto puro pelo navegador caso haja um erro simples de configuração no servidor web ou na hospedagem compartilhada.
* **Padrão adotado:** Arquivo de configuração em código Python nativo:
  `config/config.py` (localizado dentro do `[Diretório do Projeto - Repositório]`).
* **Parâmetros contidos no `config/config.py`:**
  * Configurações de Conexão com o Banco de Dados MySQL:
    * `DB_HOST`: Host do MySQL (ex: `localhost` no XAMPP ou host do PythonAnywhere);
    * `DB_PORT`: Porta de conexão (padrão 3306);
    * `DB_NAME`: Nome do banco de dados (ex: `financas_simples`);
    * `DB_USER`: Usuário do banco de dados;
    * `DB_PASSWORD`: Senha do usuário do banco de dados.
  * Parâmetros de Segurança da Aplicação:
    * `SECRET_KEY`: Chave secreta de alta entropia para assinatura criptográfica de cookies e sessões Flask;
    * `SESSION_COOKIE_SECURE`: Booleano (falso em ambiente de desenvolvimento local e verdadeiro em produção HTTPS);
    * `SESSION_COOKIE_HTTPONLY`: `True`;
    * `SESSION_COOKIE_SAMESITE`: `'Lax'`.
  * Credenciais de Integração Google OAuth:
    * `GOOGLE_CLIENT_ID`: Identificador de cliente obtido no Google Cloud Console;
    * `GOOGLE_CLIENT_SECRET`: Segredo do cliente Google;
    * `GOOGLE_DISCOVERY_URL`: URL de descoberta OpenID Connect do Google.
  * Parâmetros de Envio de E-mail (SMTP para Recuperação de Senha):
    * `MAIL_SERVER`: Servidor SMTP (ex: `smtp.gmail.com` ou host configurado);
    * `MAIL_PORT`: Porta do servidor SMTP (ex: 587 para TLS ou 465 para SSL);
    * `MAIL_USE_TLS`: Booleano indicando uso de criptografia TLS (padrão `True`);
    * `MAIL_USE_SSL`: Booleano indicando uso de criptografia SSL (padrão `False`);
    * `MAIL_USERNAME`: E-mail autenticado no servidor SMTP;
    * `MAIL_PASSWORD`: Senha ou App Password do serviço de e-mail;
    * `MAIL_DEFAULT_SENDER`: Endereço de remetente exibido nas mensagens.
  * Parâmetros de Logs e Diagnóstico:
    * `LOG_TO_FILE`: Booleano indicando a ativação da contingência em arquivo;
    * `LOG_FILE_PATH`: Caminho absoluto ou relativo seguro para `logs/error.log`.
* **Proteção do arquivo de configuração:**
  * O carregamento ocorre exclusivamente por código através de importação interna (`from config.config import Config`).
  * O arquivo `config/config.py` e sua pasta `config/` recebem proteção por `.htaccess` contra qualquer requisição HTTP direta, além do roteamento do Flask que nunca expõe rotas para a pasta `config/`.

---

## 21. Uploads, Anexos e Arquivos

* **Status do recurso na primeira versão:** **O envio de arquivos, fotos de recibos, comprovantes bancários ou notas fiscais NÃO faz parte do escopo da primeira versão do FinançasSimples.**
* **Declaração explícita:** Não há campos de upload nos formulários, não há endpoints de recebimento de arquivos no backend e não há diretórios de armazenamento de mídias de usuário configurados no servidor.
* **Justificativa:** Foco total na velocidade de lançamento manual e automação de recorrências, preservando a simplicidade da infraestrutura e mitigando riscos de segurança associados ao manuseio de arquivos não confiáveis no servidor web.

---

## 22. Relatórios, Consultas e Exportações

* **Status das exportações externas:** **A exportação de dados em formatos externos (planilhas CSV, planilhas Excel ou arquivos de relatório em PDF) NÃO faz parte do escopo da primeira versão.**
* **Modelo de consultas e relatórios adotado:** Todos os relatórios, consultas analíticas e acompanhamentos orçamentários operam de forma interativa, reativa e em tempo real diretamente na tela da aplicação web:
  1. **Painel Gerencial (Dashboard):**
     * Indicadores consolidados de Saldo Líquido, Total de Receitas e Total de Despesas calculados sob demanda para o mês e ano filtrados.
     * Gráfico de barras com a proporção de despesas distribuídas por categoria no mês.
     * Alerta instantâneo de contas pendentes vencidas e contas que vencem nos próximos 5 dias.
  2. **Consulta Avançada de Lançamentos:**
     * Filtros combinados e opcionais por período mensal, conta bancária, categoria específica, tipo de movimentação (receita, despesa, transferência) e status de quitação (pago, pendente).
     * Barra de pesquisa com busca textual instantânea na descrição dos lançamentos.
  3. **Acompanhamento de Metas de Gastos (Tetos):**
     * Consulta consolidada do consumo orçamentário por categoria na tela de Categorias, com barras de progresso percentual comparando o total consumido com o limite estabelecido.
* **Otimização e Desempenho:** Todas as consultas em tela contam com os índices de banco de dados especificados na Seção 11, assegurando respostas em milissegundos mesmo após milhares de movimentações cadastradas.

---

## 23. APIs e Integrações Externas

* **Integrações externas confirmadas:** Exclusivamente a **API de Autenticação do Google (Google OAuth 2.0 / OpenID Connect)**.
* **Objetivo da integração:** Permitir login e criação de conta com um clique utilizando as credenciais seguras da conta Google do usuário.
* **Dados trocados:**
  * Dados enviados: Redirecionamento com escopos `openid`, `email`, `profile`.
  * Dados recebidos do Google: Identificador único (`sub` / `google_id`), endereço de e-mail confirmado (`email`) e nome do usuário (`name`).
* **Tratamento de falhas:** Caso a comunicação com os servidores do Google falhe, o usuário cancele o consentimento na tela do Google ou ocorra timeout de rede, a aplicação intercepta a exceção na rota de callback, registra o ocorrido em `logs_erros` e redireciona o usuário para a tela de login tradicional com mensagem informativa amigável ("Não foi possível autenticar com o Google no momento. Por favor, tente novamente ou utilize seu e-mail e senha.").
* **Outras integrações:** Conexões com bancos (Open Finance, OFX), webhooks externos ou consumo de APIs de cotação de moedas **estão formalmente fora de escopo na primeira versão**.

---

## 24. Segurança Funcional

O FinançasSimples implementa salvaguardas rigorosas contra as principais vulnerabilidades web (alinhadas aos princípios OWASP Top 10):

1. **Prevenção contra SQL Injection:** Toda e qualquer consulta ao banco de dados MySQL deve utilizar estritamente consultas parametrizadas (*Prepared Statements*) ou a camada de ORM (SQLAlchemy). Nenhuma concatenação direta de strings em comandos SQL é permitida no código-fonte.
2. **Prevenção contra Cross-Site Scripting (XSS):** O React realiza escape automático de variáveis renderizadas na interface. No backend, respostas que devolvam dados textuais aplicam sanitização automática de caracteres especiais via Flask/Jinja2.
3. **Prevenção contra Insecure Direct Object References (IDOR):** Todas as operações de leitura, edição e exclusão de lançamentos, contas ou categorias validam obrigatoriamente se o registro requisitado pertence ao `usuario_id` extraído da sessão autenticada. A manipulação de IDs em parâmetros de requisição é totalmente neutralizada no backend.
4. **Prevenção contra Cross-Site Request Forgery (CSRF):** Todos os formulários e requisições de mutação de estado (POST, PUT, PATCH, DELETE) contam com tokens de proteção CSRF validados antes do processamento. O template raiz `index.html` renderiza `<meta name="csrf-token" content="{{ csrf_token() }}">`, e a camada de integração HTTP do frontend anexa esse token no cabeçalho `X-CSRFToken` em todas as requisições assíncronas. Cookies de sessão configurados com `SameSite=Lax`.
5. **Armazenamento Criptográfico de Senhas:** Nenhuma senha é armazenada em texto puro. O sistema aplica algoritmos robustos de derivação de chaves (`bcrypt` ou `scrypt` / `pbkdf2` com salt exclusivo por usuário gerados via `werkzeug.security`).
6. **Proteção de Dados Sensíveis e Mensagens de Erro:** Mensagens de erro visíveis ao usuário são genéricas e explicativas, evitando a exibição de nomes de tabelas, estruturas relacionais, versões de software ou stack traces.
7. **Proteção de Pastas e Arquivos Internos:** Pastas internas do repositório (`config/`, `app/`, `database/`, `logs/`) são protegidas contra acesso direto por URL através de regras de servidor web e estrutura de roteamento.

---

## 25. Organização Sugerida da Implementação

A implementação do sistema pela IA codificadora deve ser realizada de forma incremental, modular e progressivamente testável, considerando que o projeto será criado inicialmente em ambiente local (com Python/Flask e MySQL via XAMPP) e preparado para posterior deploy no PythonAnywhere.

A raiz de trabalho será sempre o `[Diretório do Projeto - Repositório]`. A sequência recomendada de execução é:

1. **Preparação do repositório e ambiente:**
   * Configuração do `[Diretório do Projeto - Repositório]`;
   * Inicialização do ambiente virtual Python (`venv`) e criação do arquivo `requirements.txt` com as dependências essenciais (Flask, SQLAlchemy, PyMySQL, Werkzeug, Flask-Mail, google-auth, etc.).
2. **Criação da estrutura de pastas e proteção:**
   * Criação dos diretórios `app/`, `app/controllers/`, `app/models/`, `app/templates/`, `app/static/`, `config/`, `database/migrations/` e `logs/`;
   * Criação do arquivo de proteção `.htaccess` para servidores Apache contra acesso direto a arquivos sensíveis (`.py`, `.sql`, `.log`).
3. **Configuração da aplicação em código:**
   * Criação do arquivo de configuração em código Python `config/config.py` (sem uso de `.env`), com parâmetros para desenvolvimento local (XAMPP), credenciais SMTP e suporte a produção;
   * Criação da App Factory (`app/__init__.py`), `run.py` (desenvolvimento) e `wsgi.py` (produção).
4. **Infraestrutura de banco de dados e migrations:**
   * Configuração da conexão com o banco MySQL via SQLAlchemy;
   * Criação da tabela de controle de migrations (`migrations_controle`);
   * Criação do script executor `database/migrate.py`;
   * Criação dos arquivos versionados de migração SQL inicial contendo as tabelas (`usuarios`, `contas`, `categorias`, `lancamentos_recorrentes`, `lancamentos`, `logs_erros`, `logs_seguranca`), constraints únicas (`uk_contas_usuario_nome`, `uk_categorias_usuario_nome_tipo`) e índices essenciais;
   * Execução da migration via linha de comando para materialização do schema no MySQL.
5. **Módulo estrutural de logs e contingência:**
   * Implementação do model `LogErro` e `LogSeguranca`;
   * Configuração do capturador global de exceções no Flask com gravação em banco e contingência em arquivo `logs/error.log`.
6. **Módulo de autenticação e sessão:**
   * Implementação do model `Usuario` com métodos de hash de senha;
   * Implementação do `auth_controller.py` com rotas web e endpoints `/api/auth/*` (login, cadastro tradicional com provisionamento da lista canônica de 10 categorias padrão e carteira inicial padrão *"Carteira"*, logout e recuperação de senha com integração SMTP e fallback de console);
   * Implementação da integração Google OAuth 2.0;
   * Criação do decorador `@login_required` para proteção de rotas privadas.
7. **Camada base de interface (View / Design Obsidian):**
   * Configuração do template base `app/templates/index.html` injetando a meta tag CSRF, fontes Geist e estilos Obsidian;
   * Criação dos estilos CSS em `app/static/css/style.css` aplicando as variáveis visuais do `docs/DESIGN.md` (superfícies `#09090b`, violeta `#a78bfa`, bordas `1px solid #27272a`), além dos estilos da variação de alto contraste em tema claro;
   * Montagem dos componentes base em React com cliente HTTP padronizado enviando o cabeçalho `X-CSRFToken`.
8. **Módulo de Contas / Carteiras:**
   * Implementação do model `Conta` e do controller `contas_controller.py` (endpoints `/api/contas/*`);
   * Telas e modais para cadastro de contas com validação de unicidade de nome, saldo inicial, visualização de saldos, arquivamento e reativação.
9. **Módulo de Categorias e Orçamentos:**
   * Implementação do model `Categoria` e do controller `categorias_controller.py` (endpoints `/api/categorias/*`);
   * Garantia da lista canônica das 10 categorias padrão no provisionamento de novos usuários;
   * Telas para cadastro de categorias com validação de unicidade, configuração de teto mensal, arquivamento e modal de reatribuição em lote com integridade transacional abrangendo registros ativos e soft-deletados.
10. **Módulo de Lançamentos:**
    * Implementação do model `Lancamento` e controller `lancamentos_controller.py` (endpoints `/api/lancamentos/*`);
    * Implementação dos formulários de receita, despesa e transferência entre contas (com preenchimento automático de `data_vencimento = data_competencia` e `status = pago`);
    * Implementação da exclusão lógica (*soft delete*) e recálculo dinâmico de saldos;
    * Inclusão do gatilho de verificação de lançamentos recorrentes ao carregar os lançamentos.
11. **Módulo de Lançamentos Recorrentes:**
    * Implementação do model `LancamentoRecorrente` e endpoints `/api/recorrentes/*`;
    * Rotina de automação para verificação e geração de lançamentos no início do ciclo mensal com ajuste automático para meses de menos de 31 dias, sincronizada entre Dashboard e Lançamentos.
12. **Módulo do Painel Principal (Dashboard):**
    * Implementação do controller `dashboard_controller.py` (endpoints `/api/dashboard/*`);
    * Consolidação dos indicadores em tempo real (saldo do mês, receitas, despesas);
    * Implementação do gráfico monocromático de despesas por categoria;
    * Bloco de alertas para contas vencidas e a vencer com ação rápida de liquidação;
    * Seletor de navegação por períodos mensais e acionamento da automação de fixos.
13. **Módulo de Configurações e Temas:**
    * Implementação do seletor de tema claro/escuro com persistência da preferência e respeito ao design *High-Contrast Dark*.
14. **Testes locais, revisão de segurança e validação final:**
    * Validação completa de todos os fluxos no XAMPP local;
    * Testes de tentativas de violação de IDOR e força bruta para comprovação dos logs de segurança;
    * Teste do mecanismo de contingência de log desconectando o MySQL temporariamente;
    * Ajustes finos de responsividade mobile e preparação das instruções de deploy no PythonAnywhere.

---

## 26. Critérios de Aceitação Técnica e Funcional

Para que o sistema FinançasSimples seja considerado concluído e pronto para entrega, os seguintes critérios devem ser integralmente atendidos e validados:

* [ ] **Stack respeitada:** O sistema foi construído com Python/Flask no backend, MySQL no banco de dados e HTML, CSS, JavaScript e React no frontend.
* [ ] **Padrão arquitetural MVC:** A separação de responsabilidades entre Models (`app/models/`), Controllers (`app/controllers/`) e Views (`app/templates/` e `app/static/`) foi estritamente aplicada, com comunicação de dados padronizada sob o prefixo `/api/*`.
* [ ] **Estrutura baseada no repositório:** Todo o projeto está organizado a partir de `[Diretório do Projeto - Repositório]`, sem depender de nomes fixos como `public_html`, `htdocs` ou `www`.
* [ ] **Configuração em código sem `.env`:** O sistema utiliza exclusivamente `config/config.py` para parâmetros e credenciais, sem a presença de nenhum arquivo `.env`.
* [ ] **Configuração SMTP presente:** O arquivo `config/config.py` contém as variáveis de configuração de envio de e-mail SMTP, com fallback seguro para exibição no log/console em desenvolvimento local.
* [ ] **Proteção de pastas internas:** As pastas `config/`, `app/`, `database/` e `logs/` estão protegidas contra acesso direto por URL através de configurações de servidor e arquitetura Flask.
* [ ] **Proteção CSRF estruturada:** Meta tag CSRF injetada no shell HTML e cabeçalho `X-CSRFToken` transmitido em todas as chamadas assíncronas de mutação do React.
* [ ] **Banco de dados via migrations:** A estrutura relacional do MySQL é criada e atualizada exclusivamente através de migrations versionadas em `database/migrations/`.
* [ ] **Controle de execução de migrations:** A tabela `migrations_controle` impede com sucesso a reexecução duplicada de migrations.
* [ ] **Execução controlada de migrations:** As migrations são executadas apenas via linha de comando (`python database/migrate.py`), sem rotas públicas no navegador.
* [ ] **Índices de desempenho ativos:** Todos os índices previstos para otimização de consultas por usuário, competência, status, conta de origem, conta de destino e vencimento foram criados no banco.
* [ ] **Constraints de unicidade garantidas:** Constraints únicas compostas para e-mail (`uk_usuarios_email`), nome de contas (`uk_contas_usuario_nome`) e nome de categorias por tipo (`uk_categorias_usuario_nome_tipo`) devidamente aplicadas.
* [ ] **Isolamento de dados por usuário:** Em todas as rotas e tabelas, os dados são estritamente isolados por `usuario_id`, com bloqueio imediato (HTTP 403) para tentativas de acesso cruzado.
* [ ] **Autenticação híbrida operacional:** Cadastro tradicional com provisionamento das 10 categorias padrão e carteira padrão inicial (*"Carteira"*), login tradicional por e-mail/senha (com hash forte) e login via Google OAuth funcionando perfeitamente.
* [ ] **Recuperação de senha segura:** Fluxo de recuperação de senha por e-mail com token temporário e expirável em 60 minutos validado.
* [ ] **Gestão de contas e carteiras:** Cadastro de contas com saldo inicial, cálculo em tempo real de saldos, bloqueio de exclusão de contas com movimentações e suporte a arquivamento e reativação.
* [ ] **Gestão de categorias e tetos:** Cadastro de categorias com limites de gastos mensais e rotina de reatribuição em lote com integridade transacional (abrangendo lançamentos ativos e soft-deletados) ao excluir categorias com histórico.
* [ ] **Gestão de lançamentos avulsos:** Cadastro, edição, filtragem por período/status/conta e busca textual operando com agilidade.
* [ ] **Transferências internas:** Transferências debitam da origem e creditam no destino sem inflar receitas ou despesas gerais do mês, preenchendo `data_vencimento = data_competencia` e status pago automaticamente.
* [ ] **Lançamentos recorrentes automáticos:** Fixos mensais geram os lançamentos correspondentes na virada do ciclo de forma transparente (disparados pelo Dashboard e pela listagem de Lançamentos), ajustando a data quando o dia for maior que o total de dias do mês.
* [ ] **Dashboard completo:** Indicadores mensais, gráfico de barras monocromático de despesas por categoria e bloco de alertas de vencimento operando em tempo real.
* [ ] **Design Obsidian respeitado:** Interface construída com superfícies near-black (`#09090b`), tipografia Geist, violeta suave (`#a78bfa`), bordas sutis e cores funcionais conforme o `docs/DESIGN.md`, com suporte harmonizado para tema claro.
* [ ] **Soft delete operacional:** Exclusão de lançamentos utiliza `deleted_at`, revertendo saldos e mantendo consistência histórica.
* [ ] **Logs de erro e contingência ativos:** Erros são registrados em banco de dados e, na indisponibilidade do MySQL, gravados com sucesso em `logs/error.log`.
* [ ] **Logs de segurança ativos:** Tentativas de login inválidas e violações de acesso são registradas estruturadamente em `logs_seguranca`.
* [ ] **Escopo respeitado:** Nenhum recurso fora de escopo (uploads, conexões bancárias automáticas, exportações externas, múltiplas moedas) foi inventado ou implementado.

---

## 27. Pontos Pendentes e Decisões Futuras

### 27.1. Pendências para Início da Implementação
Não foram identificadas pendências para iniciar a codificação com base neste FSD. Todas as definições técnicas, regras funcionais, modelos relacionais e diretrizes visuais estão consolidados e prontos para desenvolvimento.

### 27.2. Oportunidades e Melhorias Futuras (Pós-Primeira Versão)
* **Anexo de comprovantes:** Avaliar a inclusão de uploads de fotos de recibos com armazenamento em nuvem em versões futuras.
* **Importação bancária (OFX/Open Finance):** Analisar a viabilidade de leitura de extratos bancários para conciliação automática.
* **Exportação de relatórios:** Disponibilizar no futuro a exportação de lançamentos em formatos CSV e relatórios orçamentários em PDF.
* **Gestão de metas e reservas financeiras:** Criação de módulo dedicado a "cofrinhos" ou reservas de emergência.

---

## 28. Conclusão

Este Documento de Especificação Funcional (FSD) encontra-se integralmente finalizado, consistente e aprovado para guiar com absoluta autonomia a IA codificadora e os desenvolvedores responsáveis pela materialização do sistema **FinançasSimples**.

Para a fase de implementação, os únicos documentos que devem ser fornecidos e referenciados pela IA codificadora são:
* `docs/FSD.md` (este documento consolidado);
* `docs/DESIGN.md` (guia de diretrizes visuais *High-Contrast Dark*).

Não é necessária nem recomendada a entrega de documentos intermediários anteriores, uma vez que todas as diretrizes funcionais e técnicas essenciais encontram-se plenamente consolidadas neste documento.
