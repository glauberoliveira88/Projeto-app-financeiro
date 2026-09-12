# Contexto do Projeto para Agentes de IA — FinançasSimples

Este documento é a referência central e obrigatória para qualquer agente de IA que atue no desenvolvimento e manutenção do projeto **FinançasSimples**.

---

## Protocolo dos Arquivos Vivos

Antes de iniciar qualquer trabalho:
1. Ler `docs/FSD.md`.
2. Ler `docs/DESIGN.md`.
3. Ler `docs/INSUMOS.md`.
4. Ler `docs/PLANO.md`.
5. Ler `docs/STATUS.md`.
6. Ler `docs/ERROS.md`.

Use sempre caminhos relativos à raiz do projeto.
Não transformar estes caminhos em links absolutos.
Não usar links `file:///`.
Não registrar caminhos locais da máquina atual dentro do `AGENTS.md`.

Ao terminar qualquer trabalho:
1. Atualizar `docs/STATUS.md`.
2. Registrar erros e soluções em `docs/ERROS.md`, se houver.
3. Informar ao usuário o que foi feito.
4. Informar como testar ou validar a entrega.

---

## Diretrizes Gerais

* **Idioma de comunicação:** Responder e comunicar-se sempre em **português do Brasil**.
* **Fidelidade ao escopo:** Trabalhar estritamente dentro do que está especificado em `docs/FSD.md` e `docs/DESIGN.md`. Não inventar funcionalidades, integrações ou telas fora de escopo.
* **Portabilidade de caminhos:** Nunca utilizar caminhos absolutos locais da máquina do usuário nem links `file:///`. Manter todos os caminhos relativos à raiz do repositório.

---

## Stack Técnica e Restrições (Definidas no FSD)

* **Backend:** Python (v3.10+) com framework Flask estruturado com Application Factory (`app/__init__.py`) e Blueprints modulares em `app/controllers/`.
* **Banco de Dados:** MySQL (banco relacional). Camada de dados gerida via Flask-SQLAlchemy / PyMySQL com migrations versionadas em arquivos SQL (`database/migrations/`) controladas por `database/migrate.py` e registradas na tabela `migrations_controle`.
* **Frontend:** HTML5, CSS3 moderno, JavaScript (ES6+) e React / ReactDOM para interface e componentes de estado reativo. Integrado localmente via scripts empacotados em `app/static/js/vendor/`, **sem necessidade de Node.js, npm ou runtime auxiliar de build**.
* **Padrão Arquitetural:** MVC (Model-View-Controller) adaptado para Flask e React:
  * *Model:* `app/models/` (persistência, relacionamentos e regras de dados);
  * *Controller:* `app/controllers/` (Blueprints HTTP e endpoints sob o prefixo `/api/*`);
  * *View:* `app/templates/index.html` (shell base) e `app/static/` (CSS, JS, imagens e fontes).
* **Contrato de API:** Toda a comunicação entre o frontend React e o backend Flask trafega exclusivamente JSON sob o prefixo `/api/`.
* **Restrições de Escopo Rígidas:**
  * Moeda padrão e única: Real brasileiro (R$). Sem conversão ou suporte a moedas estrangeiras.
  * Sem upload de arquivos, recibos, fotos ou notas fiscais.
  * Sem exportação externa em arquivos CSV, Excel ou relatórios PDF na primeira versão.
  * Sem conexões automáticas a extratos bancários (OFX) ou APIs do Open Finance.
  * Sem painéis administrativos corporativos ou multiusuário compartilhado (painel estritamente individual).

---

## Ambientes do Projeto

* **Ambiente de Desenvolvimento Local:**
  * Python com ambiente virtual isolado (`venv`).
  * MySQL gerenciado localmente via XAMPP (porta 3306).
  * Servidor de desenvolvimento Flask executado via `python run.py`.
* **Ambiente de Produção:**
  * Nuvem PythonAnywhere.
  * Ponto de entrada WSGI configurado apontando para `wsgi.py`.
  * Banco de dados MySQL gerenciado no console do PythonAnywhere.

---

## Comandos Principais

* **Ativação do ambiente virtual (Windows PowerShell):**
  `.\venv\Scripts\Activate.ps1`
* **Instalação de dependências:**
  `pip install -r requirements.txt`
* **Execução das migrações do banco:**
  `python database/migrate.py`
* **Inicialização da aplicação em desenvolvimento:**
  `python run.py`

---

## Estrutura do Repositório

```text
FinancasSimples/
├── app/
│   ├── __init__.py               # Fábrica da aplicação Flask (App Factory)
│   ├── controllers/              # Controladores / Blueprints Flask (Rotas Web e API)
│   │   ├── __init__.py
│   │   ├── auth_controller.py
│   │   ├── dashboard_controller.py
│   │   ├── lancamentos_controller.py
│   │   ├── contas_controller.py
│   │   ├── categorias_controller.py
│   │   ├── recorrentes_controller.py
│   │   └── configuracoes_controller.py
│   ├── models/                   # Models de dados e regras de negócio (SQLAlchemy)
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
│   └── static/                   # Assets estáticos servidos pelo navegador
│       ├── css/
│       │   └── style.css         # Estilos da interface (Design Obsidian)
│       ├── js/
│       │   ├── app.js            # Aplicação React e componentes da interface
│       │   └── vendor/           # Bibliotecas locais (React, ReactDOM, etc.)
│       ├── img/                  # Logotipos e imagens da interface
│       └── fonts/                # Família de fontes Geist
├── config/
│   ├── config.py                 # Configurações em código Python (sem uso de .env)
│   └── config.example.py         # Modelo de configuração sem credenciais reais
├── database/
│   ├── migrate.py                # Script seguro de execução de migrations via CLI
│   └── migrations/               # Arquivos SQL versionados de migração
├── logs/                         # Pasta protegida de contingência de logs
│   ├── .gitkeep
│   └── error.log                 # Log de contingência quando o banco MySQL estiver indisponível
├── docs/                         # Documentação, especificações e arquivos vivos
│   ├── FSD.md
│   ├── DESIGN.md
│   ├── INSUMOS.md
│   ├── PLANO.md
│   ├── STATUS.md
│   └── ERROS.md
├── .gitignore                    # Regras de exclusão do Git
├── .htaccess                     # Regras de proteção para servidores Apache
├── requirements.txt              # Lista de dependências Python
├── run.py                        # Ponto de entrada para execução local (desenvolvimento)
├── wsgi.py                       # Ponto de entrada WSGI para produção (PythonAnywhere)
└── AGENTS.md                     # Contexto de operação para IAs (este arquivo)
```

---

## Regras de Segurança

1. **Proibição Absoluta de `.env`:** Parâmetros de conexão, segredos e chaves devem residir exclusivamente em `config/config.py` (arquivo de código Python nativo), prevenindo vazamento de texto puro em servidores web mal configurados.
2. **Prevenção contra SQL Injection:** É estritamente obrigatório o uso de consultas parametrizadas (*Prepared Statements*) ou ORM (Flask-SQLAlchemy). Nenhuma interpolação ou concatenação direta de variáveis em strings SQL é permitida.
3. **Isolamento Rígido por Usuário (Tenant Isolation / Defesa anti-IDOR):**
   * O `usuario_id` é extraído unicamente da sessão autenticada (`current_user.id`).
   * Toda consulta de leitura, escrita, edição e deleção deve validar obrigatoriamente a propriedade: `WHERE usuario_id = :current_user_id`.
   * Tentativas de acessar registros alheios devem resultar em HTTP 403 Forbidden e registro imediato em `logs_seguranca`.
4. **Proteção contra CSRF:**
   * O template base `app/templates/index.html` injeta a meta tag `<meta name="csrf-token" content="{{ csrf_token() }}">`.
   * Todas as requisições HTTP assíncronas do React que realizem mutação de estado (`POST`, `PUT`, `PATCH`, `DELETE`) devem anexar o cabeçalho `X-CSRFToken`.
   * Cookies de sessão configurados com `SameSite='Lax'` e `HttpOnly=True`.
5. **Armazenamento Seguro de Senhas:** Criptografia adaptativa irreversível com sal via `werkzeug.security` (`generate_password_hash` com scrypt ou pbkdf2) ou `bcrypt`. Senhas com no mínimo 8 caracteres.
6. **Defesa contra Força Bruta:** Bloqueio temporário (15 minutos) após 5 tentativas de login consecutivas falhas por IP/e-mail, gravando o incidente na tabela `logs_seguranca`.
7. **Proteção de Pastas e Arquivos Sensíveis:**
   * Arquivo `.htaccess` na raiz e restrições no Flask bloqueiam acesso direto a extensões `.py`, `.sql`, `.log`, `.conf` e pastas internas (`config/`, `app/`, `database/`, `logs/`).
   * Apenas `app/static/` entrega arquivos públicos ao navegador.
8. **Mecanismo Resiliente de Logs:**
   * Falhas de execução não tratadas (500) gravadas na tabela `logs_erros`.
   * Se o MySQL falhar, o capturador registra a falha no arquivo protegido `logs/error.log`.
   * O usuário final nunca recebe stack traces ou mensagens técnicas de banco, apenas mensagens seguras e amigáveis.

---

## Diretrizes de Interface e Design System

* **Documento Orientador:** `docs/DESIGN.md`.
* **Estética Principal:** *High-Contrast Dark* (Obsidian) como padrão oficial:
  * Superfícies: zinc profundo e near-black (`#09090b` de fundo, cartões entre `#0c0c0f` e `#27272a`).
  * Bordas: finas e precisas (`1px solid #27272a`), sem o uso de sombras decorativas pesadas.
  * Acentos Funcionais: violeta suave (`#a78bfa`) para links e elementos interativos primários, verde esmeralda (`#34d399`) para receitas e sucessos, vermelho (`#ef4444`) estritamente para erros, atrasos e cancelamentos.
  * Tipografia: família **Geist** com letter-spacing refinado (-0.02em em títulos).
* **Variação de Tema Claro:** Baseada na mesma sobriedade funcional em zinc claro (`#ffffff` e `#f4f4f5`), bordas em `1px solid #e4e4e7`, mantendo exatamente os mesmos acentos violeta, verde e vermelho.
* **Logotipos Dinâmicos:** Alternância sincronizada de logos entre `app/static/img/logo_tema_escuro.png` (tema escuro) e `app/static/img/logo_tema_claro.png` (tema claro).

---

## Boas Práticas de Código

* Código modular, legível e funções pequenas com responsabilidade única.
* Nomes descritivos em português para modelos, tabelas e variáveis de negócio.
* Comentários úteis e objetivos em português do Brasil quando necessário.
* Tratamento centralizado de exceções e respostas JSON consistentes (`{"sucesso": bool, "dados": ..., "erro": ...}`).
* Sem dependências fantasmas ou ferramentas desnecessárias não previstas no FSD.
