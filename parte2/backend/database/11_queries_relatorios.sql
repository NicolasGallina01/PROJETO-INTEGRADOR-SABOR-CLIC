-- 11_queries_relatorios.sql
-- Consultas SQL para os relatórios exigidos.

-- 1. Relatório de Vendas (Total faturado e quantidade de pedidos por status)
SELECT 
    status, 
    COUNT(id) AS total_pedidos, 
    SUM(total) AS receita_total
FROM pedidos
GROUP BY status;

-- 2. Relatório de Estoque (Alerta de ingredientes com baixo estoque - ex: < 5)
SELECT 
    nome, 
    quantidade_estoque, 
    unidade_medida
FROM ingredientes
WHERE quantidade_estoque <= 5.0
ORDER BY quantidade_estoque ASC;

-- 3. Ocupação de Bancadas (Quantidade de agendamentos confirmados por cozinha)
SELECT 
    c.nome AS cozinha, 
    c.capacidade_bancadas,
    COUNT(a.id) AS total_agendamentos_confirmados
FROM cozinhas c
LEFT JOIN agendamentos a ON c.id = a.cozinha_id AND a.status = 'confirmado'
GROUP BY c.id, c.nome, c.capacidade_bancadas;

-- 4. Restrição de Conflitos: Consulta que o Back-end usará para checar se a bancada está livre
-- O Flask deverá substituir o '?' pelos valores da tentativa de agendamento
/*
SELECT COUNT(*) as conflitos FROM agendamentos
WHERE cozinha_id = ?
AND status = 'confirmado'
AND (
    (? BETWEEN data_hora_inicio AND data_hora_fim) 
    OR (? BETWEEN data_hora_inicio AND data_hora_fim)
);
*/
