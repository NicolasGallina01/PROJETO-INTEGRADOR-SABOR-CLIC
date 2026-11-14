USE sabor_clic;

SELECT status, COUNT(*) AS total_pedidos, SUM(valor_total) AS valor_total
FROM Pedido GROUP BY status;

-- Receita efetivamente paga.
SELECT DATE(data_pagamento) AS dia, SUM(valor_pagamento) AS receita
FROM Venda WHERE status_pagamento = 'pago'
GROUP BY DATE(data_pagamento);

SELECT nome, estoque_atual, estoque_minimo, unidade_medida
FROM Ingrediente WHERE estoque_atual <= estoque_minimo ORDER BY estoque_atual;

SELECT b.id_bancada, b.nome, COUNT(a.id_agendamento) AS reservas_confirmadas
FROM Bancada b
LEFT JOIN Agendamento_Bancada ab ON ab.id_bancada = b.id_bancada
LEFT JOIN Agendamento a ON a.id_agendamento = ab.id_agendamento AND a.status = 'confirmado'
GROUP BY b.id_bancada, b.nome;

-- Para reservar: iniciar transacao e bloquear a Bancada com SELECT ... FOR UPDATE,
-- depois consultar conflitos e inserir a reserva antes do COMMIT.
-- Todos os caminhos de reserva devem seguir esse protocolo.
-- Consulta parametrizada pelo mysql.connector:
-- SELECT COUNT(*) FROM Agendamento_Bancada ab
-- JOIN Agendamento a ON a.id_agendamento = ab.id_agendamento
-- WHERE ab.id_bancada = %s AND a.status = 'confirmado'
-- AND ab.data_hora_inicio < %s AND ab.data_hora_fim > %s;
-- Parametros: bancada, fim pretendido, inicio pretendido.

