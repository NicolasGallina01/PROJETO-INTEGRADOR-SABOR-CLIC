-- Dados de demonstracao para um banco novo.
USE sabor_clic;
START TRANSACTION;
-- Sem contas com senhas ficticias: usuarios devem ser criados com hash pela aplicacao.
INSERT INTO Ingrediente (nome, unidade_medida, estoque_atual, estoque_minimo, custo_unitario)
VALUES ('Macarrao Espaguete', 'kg', 50, 5, 10);
SET @massa = LAST_INSERT_ID();
INSERT INTO Ingrediente (nome, unidade_medida, estoque_atual, estoque_minimo, custo_unitario)
VALUES ('Molho de Tomate', 'litro', 20, 3, 8);
SET @molho = LAST_INSERT_ID();
INSERT INTO Prato (nome, preco_unitario, categoria, descricao, tempo_preparo)
VALUES ('Espaguete ao Sugo', 28, 'Massas', 'Massa com molho de tomate', 20);
SET @prato = LAST_INSERT_ID();
INSERT INTO Ficha_Tecnica (id_prato, id_ingrediente, quantidade_ingrediente)
VALUES (@prato, @massa, 0.200), (@prato, @molho, 0.150);
INSERT INTO Bancada (nome, tipo, capacidade, valor_hora)
VALUES ('Bancada 01', 'Preparacao geral', 4, 25), ('Bancada 02', 'Massas', 3, 30);
COMMIT;
