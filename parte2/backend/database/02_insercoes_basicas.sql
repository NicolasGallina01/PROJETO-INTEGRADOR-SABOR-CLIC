-- 02_insercoes_basicas.sql
-- DML: Dados iniciais para testes do sistema (Seeders).

-- Inserindo Usuários
INSERT INTO usuarios (nome, email, senha, perfil) VALUES
('Administrador Geral', 'admin@saboreclic.com.br', 'hash_senha_admin', 'admin'),
('Chef Jacquin', 'jacquin@saboreclic.com.br', 'hash_senha_chef', 'cozinheiro'),
('Cliente Fome', 'cliente@email.com', 'hash_senha_cliente', 'cliente');

-- Inserindo Cozinhas
INSERT INTO cozinhas (nome, capacidade_bancadas) VALUES
('Cozinha Fria', 2),
('Cozinha Quente (Massas e Carnes)', 4);

-- Inserindo Ingredientes
INSERT INTO ingredientes (nome, quantidade_estoque, unidade_medida) VALUES
('Macarrão Espaguete', 50.0, 'kg'),
('Molho de Tomate', 20.0, 'litros'),
('Carne Moída', 15.0, 'kg'),
('Parmesão Ralado', 5.0, 'kg');

-- Inserindo Pratos
INSERT INTO pratos (nome, descricao, preco, cozinha_id) VALUES
('Macarronada Bolonhesa', 'Massa fresca com molho à bolonhesa caseiro', 35.50, 2),
('Espaguete ao Sugo', 'Massa clássica com molho de tomate fresco', 28.00, 2);

-- Inserindo Ficha Técnica (Prato x Ingredientes)
INSERT INTO prato_ingrediente (prato_id, ingrediente_id, quantidade_necessaria) VALUES
(1, 1, 0.2),  -- 200g de macarrão
(1, 2, 0.15), -- 150ml de molho
(1, 3, 0.2),  -- 200g de carne moída
(1, 4, 0.05); -- 50g de parmesão

-- Inserindo um Pedido Inicial de Teste
INSERT INTO pedidos (usuario_id, status, total) VALUES
(3, 'concluido', 35.50);

INSERT INTO itens_pedido (pedido_id, prato_id, quantidade, preco_unitario) VALUES
(1, 1, 1, 35.50);
