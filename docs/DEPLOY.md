# Guia de Deploy em Produção — FinançasSimples

Este documento descreve o procedimento operacional padrão para implantação do sistema **FinançasSimples** no ambiente de produção hospedado no **PythonAnywhere**, conforme as especificações de `docs/FSD.md` (Seções 4, 5 e 20.2).

---

## 1. Pré-Requisitos no PythonAnywhere

1. Conta ativa no [PythonAnywhere](https://www.pythonanywhere.com/).
2. Instância do **MySQL** provisionada na aba **Databases** do painel:
   - Definir uma senha forte para o usuário MySQL;
   - Anotar o endereço do servidor MySQL (formato: `seu_usuario.mysql.pythonanywhere-services.com`);
   - Criar o banco de dados da aplicação com charset `utf8mb4` (ex: `seu_usuario$financas_simples`).

---

## 2. Clonagem do Repositório e Ambiente Virtual

Abra um console Bash no PythonAnywhere e execute:

```bash
# 1. Navegar até o diretório raiz do usuário
cd ~

# 2. Clonar o repositório do projeto
git clone <URL_DO_REPOSITORIO> financas-simples

# 3. Acessar o diretório do projeto
cd ~/financas-simples

# 4. Criar o ambiente virtual isolado com Python 3.10+
python3.10 -m venv venv

# 5. Ativar o ambiente virtual
source venv/bin/activate

# 6. Atualizar o pip e instalar as dependências oficiais do projeto
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Configuração de Produção (`config/config.py`)

> [!IMPORTANT]
> **Proibição Absoluta de `.env`:** Parâmetros de infraestrutura, credenciais de banco e chaves de segurança residem exclusivamente em `config/config.py`. Nunca crie nem faça upload de arquivos `.env`.

Edite o arquivo `config/config.py` com as credenciais reais do seu ambiente de produção PythonAnywhere:

```python
# config/config.py (Trecho de configuração de produção)

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # Credenciais do MySQL do PythonAnywhere
    DB_HOST = "seu_usuario.mysql.pythonanywhere-services.com"
    DB_PORT = 3306
    DB_NAME = "seu_usuario$financas_simples"
    DB_USER = "seu_usuario"
    DB_PASSWORD = "sua_senha_segura_do_mysql"
    
    # URI de conexão SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
    
    # Chave secreta de alta entropia para sessões em produção
    SECRET_KEY = "gerar_uma_chave_secreta_longa_e_aleatoria_aqui"
    
    # Cookies seguros exclusivos para tráfego HTTPS
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    
    # Parâmetros SMTP para despacho real de e-mails de recuperação de senha
    MAIL_SERVER = "smtp.seu-provedor.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = "seu-email@dominio.com"
    MAIL_PASSWORD = "sua-senha-de-aplicativo"
    MAIL_DEFAULT_SENDER = "FinançasSimples <seu-email@dominio.com>"
    
    # Logs em contingência
    LOG_TO_FILE = True
```

---

## 4. Execução das Migrations Versionadas

Com o banco provisionado e o arquivo `config/config.py` configurado, execute as migrações controladas via CLI a partir do console com o ambiente virtual ativo:

```bash
cd ~/financas-simples
source venv/bin/activate

# Executa as migrations SQL controladas
python database/migrate.py
```

O script criará de forma idempotente:
* As 8 tabelas centrais: `usuarios`, `contas`, `categorias`, `lancamentos_recorrentes`, `lancamentos`, `logs_erros`, `logs_seguranca`, `migrations_controle`;
* As constraints únicas: `uk_usuarios_email`, `uk_usuarios_google_id`, `uk_contas_usuario_nome`, `uk_categorias_usuario_nome_tipo`;
* Os 8 índices de otimização e alta performance.

---

## 5. Configuração da Aplicação Web no Painel do PythonAnywhere

Acesse a aba **Web** no painel de controle do PythonAnywhere e configure:

1. **Ponto de Entrada WSGI (WSGI Configuration File):**
   - Clique no link do arquivo de configuração WSGI gerado pelo PythonAnywhere (ex: `/var/www/seu_usuario_pythonanywhere_com_wsgi.py`);
   - Substitua todo o conteúdo pelo trecho abaixo:

```python
import sys
import os

# Define o caminho do projeto
project_home = '/home/seu_usuario/financas-simples'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Importa a aplicação configurada com ProductionConfig
from wsgi import application
```

2. **Virtualenv:**
   - No campo **Virtualenv**, informe o caminho completo do ambiente virtual:
     `/home/seu_usuario/financas-simples/venv`

3. **Arquivos Estáticos (Static Files):**
   - Mapeie a rota de assets públicos para que o servidor web sirva CSS, JS, imagens e fontes com máxima velocidade sem onerar o worker Python:
     * **URL:** `/static/`
     * **Directory:** `/home/seu_usuario/financas-simples/app/static/`

4. **HTTPS / Segurança:**
   - Ative a opção **Force HTTPS** no painel da aplicação web.

---

## 6. Inicialização e Validação do Deploy

1. Clique no botão verde **Reload <seu_usuario>.pythonanywhere.com** no topo da aba Web.
2. Acesse a URL pública no navegador (`https://seu_usuario.pythonanywhere.com`).
3. Realize o teste de fumaça inicial:
   - Cadastro de um novo usuário;
   - Verificação do provisionamento automático da carteira inicial (*"Carteira"*) e das 10 categorias canônicas;
   - Registro de um lançamento de receita e uma despesa;
   - Teste de alternância entre o tema oficial *High-Contrast Dark* e o tema claro;
   - Logout manual e login tradicional.

---

## 7. Monitoramento e Contingência de Logs em Produção

* **Logs de Erros de Aplicação (MySQL):** Acompanhados diretamente pela tabela `logs_erros`.
* **Logs de Segurança (MySQL):** Acompanhados pela tabela `logs_seguranca` (bloqueios de força bruta, tentativas de IDOR).
* **Contingência em Arquivo:** Caso o banco MySQL passe por manutenção ou indisponibilidade, os incidentes serão automaticamente gravados com traceback em:
  `~/financas-simples/logs/error.log`
* **Logs do Servidor Web:** Acesse os arquivos de erro do servidor web diretamente na aba Web do PythonAnywhere:
  - Error log: `/var/log/seu_usuario.pythonanywhere.com.error.log`
  - Server log: `/var/log/seu_usuario.pythonanywhere.com.server.log`
