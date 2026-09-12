-- ==============================================================================
-- FinançasSimples — Migration 001: Criação das Tabelas Iniciais
-- Especificação Técnica: docs/FSD.md - Seção 11.1
-- ==============================================================================

-- 1. Tabela: usuarios
CREATE TABLE IF NOT EXISTS `usuarios` (
    `id` INT UNSIGNED AUTO_INCREMENT NOT NULL,
    `nome` VARCHAR(150) NOT NULL,
    `email` VARCHAR(191) NOT NULL,
    `senha_hash` VARCHAR(255) NULL,
    `google_id` VARCHAR(100) NULL,
    `tema_preferido` ENUM('dark', 'light') NOT NULL DEFAULT 'dark',
    `token_recuperacao` VARCHAR(100) NULL,
    `token_recuperacao_expira` DATETIME NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    CONSTRAINT `uk_usuarios_email` UNIQUE (`email`),
    CONSTRAINT `uk_usuarios_google_id` UNIQUE (`google_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Tabela: contas (carteiras do usuário)
CREATE TABLE IF NOT EXISTS `contas` (
    `id` INT UNSIGNED AUTO_INCREMENT NOT NULL,
    `usuario_id` INT UNSIGNED NOT NULL,
    `nome` VARCHAR(100) NOT NULL,
    `saldo_inicial` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    `status` ENUM('ativo', 'arquivado') NOT NULL DEFAULT 'ativo',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_contas_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
    CONSTRAINT `uk_contas_usuario_nome` UNIQUE (`usuario_id`, `nome`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Tabela: categorias
CREATE TABLE IF NOT EXISTS `categorias` (
    `id` INT UNSIGNED AUTO_INCREMENT NOT NULL,
    `usuario_id` INT UNSIGNED NOT NULL,
    `nome` VARCHAR(100) NOT NULL,
    `tipo` ENUM('receita', 'despesa') NOT NULL,
    `teto_orcamento` DECIMAL(12, 2) NULL DEFAULT NULL,
    `status` ENUM('ativo', 'arquivado') NOT NULL DEFAULT 'ativo',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_categorias_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
    CONSTRAINT `uk_categorias_usuario_nome_tipo` UNIQUE (`usuario_id`, `nome`, `tipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Tabela: lancamentos_recorrentes (modelos de fixos mensais)
CREATE TABLE IF NOT EXISTS `lancamentos_recorrentes` (
    `id` INT UNSIGNED AUTO_INCREMENT NOT NULL,
    `usuario_id` INT UNSIGNED NOT NULL,
    `tipo` ENUM('receita', 'despesa') NOT NULL,
    `valor` DECIMAL(12, 2) NOT NULL,
    `descricao` VARCHAR(150) NOT NULL,
    `categoria_id` INT UNSIGNED NOT NULL,
    `conta_id` INT UNSIGNED NOT NULL,
    `forma_pagamento` VARCHAR(50) NOT NULL DEFAULT 'PIX',
    `dia_vencimento` TINYINT UNSIGNED NOT NULL,
    `ativo` BOOLEAN NOT NULL DEFAULT TRUE,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_recorrentes_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_recorrentes_categoria` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_recorrentes_conta` FOREIGN KEY (`conta_id`) REFERENCES `contas` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Tabela: lancamentos
CREATE TABLE IF NOT EXISTS `lancamentos` (
    `id` INT UNSIGNED AUTO_INCREMENT NOT NULL,
    `usuario_id` INT UNSIGNED NOT NULL,
    `tipo` ENUM('receita', 'despesa', 'transferencia') NOT NULL,
    `valor` DECIMAL(12, 2) NOT NULL,
    `data_competencia` DATE NOT NULL,
    `data_vencimento` DATE NOT NULL,
    `descricao` VARCHAR(200) NOT NULL,
    `categoria_id` INT UNSIGNED NULL,
    `conta_id` INT UNSIGNED NOT NULL,
    `conta_destino_id` INT UNSIGNED NULL,
    `forma_pagamento` VARCHAR(50) NOT NULL DEFAULT 'Dinheiro',
    `status` ENUM('pago', 'pendente') NOT NULL DEFAULT 'pago',
    `observacao` TEXT NULL,
    `recorrente_id` INT UNSIGNED NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted_at` DATETIME NULL DEFAULT NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_lancamentos_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_lancamentos_categoria` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_lancamentos_conta` FOREIGN KEY (`conta_id`) REFERENCES `contas` (`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_lancamentos_conta_destino` FOREIGN KEY (`conta_destino_id`) REFERENCES `contas` (`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_lancamentos_recorrente` FOREIGN KEY (`recorrente_id`) REFERENCES `lancamentos_recorrentes` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Tabela: logs_erros
CREATE TABLE IF NOT EXISTS `logs_erros` (
    `id` INT UNSIGNED AUTO_INCREMENT NOT NULL,
    `usuario_id` INT UNSIGNED NULL,
    `nivel` VARCHAR(20) NOT NULL,
    `rota` VARCHAR(255) NULL,
    `mensagem` TEXT NOT NULL,
    `stack_trace` MEDIUMTEXT NULL,
    `ip` VARCHAR(45) NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_logs_erros_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Tabela: logs_seguranca
CREATE TABLE IF NOT EXISTS `logs_seguranca` (
    `id` INT UNSIGNED AUTO_INCREMENT NOT NULL,
    `usuario_id` INT UNSIGNED NULL,
    `evento` VARCHAR(100) NOT NULL,
    `ip` VARCHAR(45) NULL,
    `detalhes` TEXT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_logs_seguranca_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Tabela: migrations_controle
CREATE TABLE IF NOT EXISTS `migrations_controle` (
    `id` INT UNSIGNED AUTO_INCREMENT NOT NULL,
    `migration_name` VARCHAR(191) NOT NULL,
    `executado_em` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    CONSTRAINT `uk_migration_name` UNIQUE (`migration_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
