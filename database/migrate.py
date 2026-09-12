"""Script seguro de execução de migrations versionadas via CLI (docs/FSD.md - Seção 11.3).

Executa as migrations SQL presentes em database/migrations/ no banco MySQL configurado
em config/config.py, controlando a idempotência através da tabela migrations_controle.

Uso:
    python database/migrate.py
"""
import os
import sys

# Assegurar que a raiz do projeto esteja no sys.path para importar config
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config.config import Config

MIGRATIONS_DIR = os.path.join(BASE_DIR, "database", "migrations")


def extrair_comandos_sql(conteudo_sql: str) -> list[str]:
    """Divide o arquivo SQL em comandos válidos, ignorando blocos vazios e comentários isolados."""
    comandos = []
    partes = conteudo_sql.split(";")
    for parte in partes:
        linhas_uteis = []
        for linha in parte.splitlines():
            linha_limpa = linha.strip()
            if not linha_limpa or linha_limpa.startswith("--") or linha_limpa.startswith("#"):
                continue
            linhas_uteis.append(linha)
        comando_limpo = "\n".join(linhas_uteis).strip()
        if comando_limpo:
            comandos.append(comando_limpo)
    return comandos


def executar_migrations():
    """Lê e executa as migrações pendentes no MySQL."""
    print("=" * 60)
    print("EXECUTOR DE MIGRATIONS — FinançasSimples")
    print("=" * 60)
    print(f"Host: {Config.DB_HOST}:{Config.DB_PORT}")
    print(f"Banco de Dados: {Config.DB_NAME}")
    print(f"Diretório de Migrations: {MIGRATIONS_DIR}")
    print("-" * 60)

    try:
        import pymysql
    except ImportError:
        print("[ERRO] O conector PyMySQL não está instalado.")
        print("Instale as dependências com: pip install -r requirements.txt")
        sys.exit(1)

    try:
        # Conexão inicial para garantir a criação do banco se necessário
        conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            charset="utf8mb4",
            autocommit=False,
        )
    except Exception as e:
        print(f"[ERRO DE CONEXÃO] Falha ao conectar ao servidor MySQL: {e}")
        print("Certifique-se de que o serviço MySQL (ex: XAMPP) esteja ativo.")
        sys.exit(1)

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
            cursor.execute(f"USE `{Config.DB_NAME}`;")

            # Garantir tabela de controle de migrations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `migrations_controle` (
                    `id` INT UNSIGNED AUTO_INCREMENT NOT NULL,
                    `migration_name` VARCHAR(191) NOT NULL,
                    `executado_em` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (`id`),
                    CONSTRAINT `uk_migration_name` UNIQUE (`migration_name`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            conn.commit()

            # Obter migrations já executadas
            cursor.execute("SELECT migration_name FROM `migrations_controle`;")
            executadas = {row[0] for row in cursor.fetchall()}

        # Listar arquivos de migração ordenados
        if not os.path.exists(MIGRATIONS_DIR):
            os.makedirs(MIGRATIONS_DIR, exist_ok=True)

        arquivos = sorted([f for f in os.listdir(MIGRATIONS_DIR) if f.endswith(".sql")])

        if not arquivos:
            print("[INFO] Nenhum arquivo .sql encontrado em database/migrations/.")
            conn.close()
            return

        pendentes = [f for f in arquivos if f not in executadas]

        if not pendentes:
            print(f"[OK] Banco de dados atualizado! Todas as {len(arquivos)} migrations já foram aplicadas.")
            conn.close()
            return

        print(f"Total de migrations pendentes: {len(pendentes)}")

        for arquivo in pendentes:
            caminho = os.path.join(MIGRATIONS_DIR, arquivo)
            print(f"-> Aplicando: {arquivo}...")
            with open(caminho, "r", encoding="utf-8") as f:
                conteudo_sql = f.read()

            comandos = extrair_comandos_sql(conteudo_sql)

            try:
                with conn.cursor() as cursor:
                    # Executar comandos individuais do arquivo SQL
                    for sql in comandos:
                        cursor.execute(sql)

                    # Registrar migração aplicada
                    cursor.execute(
                        "INSERT INTO `migrations_controle` (`migration_name`) VALUES (%s);",
                        (arquivo,),
                    )
                conn.commit()
                print(f"   [SUCESSO] {arquivo} aplicada com sucesso ({len(comandos)} comandos executados).")
            except Exception as err:
                conn.rollback()
                print(f"   [FALHA] Erro ao aplicar {arquivo}: {err}")
                conn.close()
                sys.exit(1)

        conn.close()
        print("-" * 60)
        print("[CONCLUÍDO] Todas as migrações pendentes foram aplicadas com sucesso.")

    except Exception as e:
        print(f"[ERRO GERAL] Falha durante o processamento das migrations: {e}")
        if conn:
            conn.close()
        sys.exit(1)


if __name__ == "__main__":
    executar_migrations()
