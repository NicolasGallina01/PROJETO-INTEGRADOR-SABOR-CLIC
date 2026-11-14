# Banco MySQL

Requer MySQL 8.0.16 ou superior. Em um banco novo, execute na ordem:
01_modelo_fisico.sql e 02_insercoes_basicas.sql.
11_queries_relatorios.sql contem consultas, nao criacao de tabelas.

Os scripts nao migram um banco existente. O arquivo Workbench registra
o modelo anterior; o SQL inclui as correcoes posteriores.

O backend definitivo esta em parte2/backend; consulte ../README.md.
O backend de parte1 e um prototipo com dados em memoria. O conector
foi configurado para MySQL, mas as rotas ainda precisam de persistencia,
autenticacao e transacoes. O frontend tambem continua demonstrativo.

Para preparar o prototipo: instale requirements.txt, copie .env.example
para .env e configure um usuario MySQL com acesso ao banco sabor_clic.
Execute app.py a partir da pasta Python.

Pedidos possuem cliente obrigatorio, cozinheiro e venda opcionais.
Vendas podem ter agendamento; compras de pratos nao exigem reserva.
Status de pedido: aguardando, em_preparo, pronto, entregue, cancelado.
O tempo de preparo e informado em minutos no Prato.
Reservas exigem fim posterior ao inicio. Conflitos simultaneos precisam
do bloqueio transacional descrito em 11_queries_relatorios.sql.
O projeto nao utiliza triggers. A baixa e o estorno de estoque deverao ser
implementados no servico de pedidos em transacoes.
