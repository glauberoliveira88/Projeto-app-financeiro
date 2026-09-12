-- ==============================================================================
-- FinançasSimples — Migration 002: Criação dos Índices de Desempenho
-- Especificação Técnica: docs/FSD.md - Seção 11.2
-- ==============================================================================

-- 1. Otimização para Dashboard e listagens mensais por período contábil
CREATE INDEX `idx_lancamentos_usuario_competencia` 
ON `lancamentos` (`usuario_id`, `data_competencia`, `deleted_at`);

-- 2. Otimização para bloco de alertas de contas vencidas e a vencer
CREATE INDEX `idx_lancamentos_usuario_status_vencimento` 
ON `lancamentos` (`usuario_id`, `status`, `data_vencimento`, `deleted_at`);

-- 3. Otimização para cálculo de saldo em tempo real por conta de origem
CREATE INDEX `idx_lancamentos_usuario_conta` 
ON `lancamentos` (`usuario_id`, `conta_id`, `deleted_at`);

-- 4. Otimização para cálculo de saldo nas transferências recebidas
CREATE INDEX `idx_lancamentos_usuario_conta_destino` 
ON `lancamentos` (`usuario_id`, `conta_destino_id`, `deleted_at`);

-- 5. Otimização para consolidação por categoria e verificação de tetos de gastos
CREATE INDEX `idx_lancamentos_usuario_categoria` 
ON `lancamentos` (`usuario_id`, `categoria_id`, `deleted_at`);

-- 6. Otimização para listagem e filtros de contas ativas/arquivadas
CREATE INDEX `idx_contas_usuario_status` 
ON `contas` (`usuario_id`, `status`);

-- 7. Otimização para filtragem de categorias por tipo (receita/despesa) e status
CREATE INDEX `idx_categorias_usuario_tipo_status` 
ON `categorias` (`usuario_id`, `tipo`, `status`);

-- 8. Otimização para rotina de geração de lançamentos da virada de mês
CREATE INDEX `idx_recorrentes_usuario_ativo` 
ON `lancamentos_recorrentes` (`usuario_id`, `ativo`);
