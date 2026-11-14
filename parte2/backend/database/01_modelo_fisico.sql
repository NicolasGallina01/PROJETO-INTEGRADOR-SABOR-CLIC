-- MySQL 8.0.16 ou superior (restricoes CHECK).
-- Criacao de banco novo; nao e uma migracao de dados existentes.
CREATE DATABASE IF NOT EXISTS sabor_clic CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sabor_clic;

CREATE TABLE `Usuario` (
    `id_usuario` INT NOT NULL AUTO_INCREMENT,
    `nome` VARCHAR(60) NOT NULL,
    `email` VARCHAR(80) NOT NULL UNIQUE,
    `senha_hash` VARCHAR(255) NOT NULL,
    `ativo` TINYINT NOT NULL DEFAULT 1,
    PRIMARY KEY (`id_usuario`)
) ENGINE = InnoDB;

CREATE TABLE `Administrador` (
    `id_usuario` INT NOT NULL,
    `nivel_permissao` INT NOT NULL,
    PRIMARY KEY (`id_usuario`)
) ENGINE = InnoDB;

CREATE TABLE `Cliente` (
    `id_usuario` INT NOT NULL,
    `data_cadastro` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `telefone` VARCHAR(20) NULL,
    `numero_endereco` VARCHAR(10) NULL,
    `logradouro` VARCHAR(80) NULL,
    `cep` VARCHAR(15) NULL,
    PRIMARY KEY (`id_usuario`)
) ENGINE = InnoDB;

CREATE TABLE `Cozinheiro` (
    `id_usuario` INT NOT NULL,
    `turno` ENUM('MANHA', 'TARDE', 'NOITE') NOT NULL,
    `especialidade` VARCHAR(30) NOT NULL,
    PRIMARY KEY (`id_usuario`)
) ENGINE = InnoDB;

CREATE TABLE `Prato` (
    `id_prato` INT NOT NULL AUTO_INCREMENT,
    `nome` VARCHAR(100) NOT NULL,
    `preco_unitario` DECIMAL(10,2) NOT NULL,
    `ativo` TINYINT NOT NULL DEFAULT 1,
    `categoria` VARCHAR(50) NOT NULL,
    `descricao` TEXT NULL,
    `imagem_url` VARCHAR(2048) NULL,
    `tempo_preparo` INT NOT NULL DEFAULT 0,
    PRIMARY KEY (`id_prato`)
) ENGINE = InnoDB;

CREATE TABLE `Ingrediente` (
    `id_ingrediente` INT NOT NULL AUTO_INCREMENT,
    `nome` VARCHAR(60) NOT NULL,
    `unidade_medida` VARCHAR(20) NOT NULL,
    `estoque_atual` DECIMAL(12,3) NOT NULL DEFAULT 0,
    `estoque_minimo` DECIMAL(12,3) NOT NULL DEFAULT 0,
    `categoria` VARCHAR(50) NULL,
    `validade` DATE NULL,
    `custo_unitario` DECIMAL(10,2) NOT NULL DEFAULT 0,
    PRIMARY KEY (`id_ingrediente`)
) ENGINE = InnoDB;

CREATE TABLE `Venda` (
    `id_venda` INT NOT NULL AUTO_INCREMENT,
    `valor_pagamento` DECIMAL(10,2) NOT NULL,
    `data_pagamento` DATETIME NULL,
    `forma_pagamento` ENUM('DINHEIRO', 'PIX', 'DEBITO', 'CREDITO') NULL,
    `id_agendamento` INT NULL,
    `status_pagamento` ENUM('pendente', 'pago', 'cancelado', 'estornado') NOT NULL DEFAULT 'pendente',
    PRIMARY KEY (`id_venda`),
    INDEX `fk_Venda_Agendamento1_idx` (`id_agendamento`)
) ENGINE = InnoDB;

CREATE TABLE `Agendamento` (
    `id_agendamento` INT NOT NULL AUTO_INCREMENT,
    `id_usuario` INT NOT NULL,
    `status` ENUM('confirmado', 'cancelado') NOT NULL DEFAULT 'confirmado',
    `hora_criacao` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `observacao` VARCHAR(500) NULL,
    PRIMARY KEY (`id_agendamento`),
    INDEX `fk_Agendamento_Cliente1_idx` (`id_usuario`)
) ENGINE = InnoDB;

CREATE TABLE `Pedido` (
    `id_pedido` INT NOT NULL AUTO_INCREMENT,
    `id_cliente` INT NOT NULL,
    `id_cozinheiro` INT NULL,
    `id_venda` INT NULL,
    `endereco_entrega` VARCHAR(255) NULL,
    `criado_em` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status` ENUM('aguardando', 'em_preparo', 'pronto', 'entregue', 'cancelado') NOT NULL DEFAULT 'aguardando',
    `prazo_estimado` DATETIME NULL,
    `valor_total` DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (`id_pedido`),
    INDEX `fk_Pedido_Cozinheiro1_idx` (`id_cozinheiro`),
    INDEX `fk_Pedido_Venda1_idx` (`id_venda`)
) ENGINE = InnoDB;

CREATE TABLE `Bancada` (
    `id_bancada` INT NOT NULL AUTO_INCREMENT,
    `nome` VARCHAR(60) NOT NULL,
    `tipo` VARCHAR(80) NULL,
    `capacidade` INT NOT NULL,
    `ativo` TINYINT NOT NULL DEFAULT 1,
    `valor_hora` DECIMAL(10,2) NOT NULL DEFAULT 0,
    PRIMARY KEY (`id_bancada`)
) ENGINE = InnoDB;

CREATE TABLE `Agendamento_Bancada` (
    `id_agendamento_bancada` INT NOT NULL AUTO_INCREMENT,
    `id_bancada` INT NOT NULL,
    `id_agendamento` INT NOT NULL,
    `data_hora_inicio` DATETIME NOT NULL,
    `data_hora_fim` DATETIME NOT NULL,
    PRIMARY KEY (`id_agendamento_bancada`),
    UNIQUE (`id_agendamento`, `id_bancada`),
    CHECK (`data_hora_fim` > `data_hora_inicio`),
    INDEX `fk_Bancada_has_Agendamento_Agendamento1_idx` (`id_agendamento`),
    INDEX `fk_Bancada_has_Agendamento_Bancada1_idx` (`id_bancada`)
) ENGINE = InnoDB;

CREATE TABLE `Item_Pedido` (
    `id_item_pedido` INT NOT NULL AUTO_INCREMENT,
    `id_prato` INT NOT NULL,
    `id_pedido` INT NOT NULL,
    `preco_unitario` DECIMAL(10,2) NOT NULL,
    `quantidade` INT NOT NULL,
    `subtotal` DECIMAL(12,2) GENERATED ALWAYS AS (`quantidade` * `preco_unitario`) STORED,
    PRIMARY KEY (`id_item_pedido`),
    CHECK (`quantidade` > 0),
    CHECK (`preco_unitario` >= 0),
    INDEX `fk_Prato_has_Pedido_Pedido1_idx` (`id_pedido`),
    INDEX `fk_Prato_has_Pedido_Prato1_idx` (`id_prato`)
) ENGINE = InnoDB;

CREATE TABLE `Ficha_Tecnica` (
    `id_prato` INT NOT NULL,
    `id_ingrediente` INT NOT NULL,
    `quantidade_ingrediente` DECIMAL(12,3) NOT NULL CHECK (`quantidade_ingrediente` > 0),
    PRIMARY KEY (`id_prato`, `id_ingrediente`),
    INDEX `fk_Prato_has_Ingrediente_Ingrediente1_idx` (`id_ingrediente`),
    INDEX `fk_Prato_has_Ingrediente_Prato1_idx` (`id_prato`)
) ENGINE = InnoDB;

CREATE TABLE `Substituicao_Ingrediente` (
    `id_ingrediente_principal` INT NOT NULL,
    `id_ingrediente_substituto` INT NOT NULL,
    `nivel_prioridade` INT NOT NULL,
    PRIMARY KEY (`id_ingrediente_principal`, `id_ingrediente_substituto`),
    INDEX `fk_Ingrediente_has_Ingrediente_Ingrediente2_idx` (`id_ingrediente_substituto`),
    INDEX `fk_Ingrediente_has_Ingrediente_Ingrediente1_idx` (`id_ingrediente_principal`)
) ENGINE = InnoDB;

CREATE TABLE `Pedido_Consumo` (
    `id_pedido` INT NOT NULL,
    `id_ingrediente` INT NOT NULL,
    `quantidade` DECIMAL(12,3) NOT NULL CHECK (`quantidade` > 0),
    PRIMARY KEY (`id_pedido`, `id_ingrediente`),
    FOREIGN KEY (`id_pedido`) REFERENCES `Pedido` (`id_pedido`),
    FOREIGN KEY (`id_ingrediente`) REFERENCES `Ingrediente` (`id_ingrediente`)
) ENGINE = InnoDB;

ALTER TABLE `Administrador` ADD CONSTRAINT `fk_Administrador_Usuario1` FOREIGN KEY (`id_usuario`) REFERENCES `Usuario` (`id_usuario`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `Cliente` ADD CONSTRAINT `fk_Cliente_Usuario1` FOREIGN KEY (`id_usuario`) REFERENCES `Usuario` (`id_usuario`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `Cozinheiro` ADD CONSTRAINT `fk_Cozinheiro_Usuario1` FOREIGN KEY (`id_usuario`) REFERENCES `Usuario` (`id_usuario`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `Venda` ADD CONSTRAINT `fk_Venda_Agendamento1` FOREIGN KEY (`id_agendamento`) REFERENCES `Agendamento` (`id_agendamento`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `Agendamento` ADD CONSTRAINT `fk_Agendamento_Cliente1` FOREIGN KEY (`id_usuario`) REFERENCES `Cliente` (`id_usuario`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `Pedido` ADD CONSTRAINT `fk_Pedido_Cozinheiro1` FOREIGN KEY (`id_cozinheiro`) REFERENCES `Cozinheiro` (`id_usuario`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `Pedido` ADD CONSTRAINT `fk_Pedido_Venda1` FOREIGN KEY (`id_venda`) REFERENCES `Venda` (`id_venda`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `Agendamento_Bancada` ADD CONSTRAINT `fk_Bancada_has_Agendamento_Bancada1` FOREIGN KEY (`id_bancada`) REFERENCES `Bancada` (`id_bancada`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `Agendamento_Bancada` ADD CONSTRAINT `fk_Bancada_has_Agendamento_Agendamento1` FOREIGN KEY (`id_agendamento`) REFERENCES `Agendamento` (`id_agendamento`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `Item_Pedido` ADD CONSTRAINT `fk_Prato_has_Pedido_Prato1` FOREIGN KEY (`id_prato`) REFERENCES `Prato` (`id_prato`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `Item_Pedido` ADD CONSTRAINT `fk_Prato_has_Pedido_Pedido1` FOREIGN KEY (`id_pedido`) REFERENCES `Pedido` (`id_pedido`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `Ficha_Tecnica` ADD CONSTRAINT `fk_Prato_has_Ingrediente_Prato1` FOREIGN KEY (`id_prato`) REFERENCES `Prato` (`id_prato`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `Ficha_Tecnica` ADD CONSTRAINT `fk_Prato_has_Ingrediente_Ingrediente1` FOREIGN KEY (`id_ingrediente`) REFERENCES `Ingrediente` (`id_ingrediente`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `Substituicao_Ingrediente` ADD CONSTRAINT `fk_Ingrediente_has_Ingrediente_Ingrediente1` FOREIGN KEY (`id_ingrediente_principal`) REFERENCES `Ingrediente` (`id_ingrediente`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `Substituicao_Ingrediente` ADD CONSTRAINT `fk_Ingrediente_has_Ingrediente_Ingrediente2` FOREIGN KEY (`id_ingrediente_substituto`) REFERENCES `Ingrediente` (`id_ingrediente`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `Pedido` ADD CONSTRAINT `fk_Pedido_Cliente` FOREIGN KEY (`id_cliente`) REFERENCES `Cliente` (`id_usuario`);
ALTER TABLE `Prato` ADD CHECK (`preco_unitario` >= 0), ADD CHECK (`tempo_preparo` >= 0);
ALTER TABLE `Ingrediente` ADD CHECK (`estoque_atual` >= 0), ADD CHECK (`estoque_minimo` >= 0), ADD CHECK (`custo_unitario` >= 0);
ALTER TABLE `Bancada` ADD CHECK (`capacidade` > 0), ADD CHECK (`valor_hora` >= 0);
ALTER TABLE `Pedido` ADD CHECK (`valor_total` >= 0);
ALTER TABLE `Venda` ADD CHECK (`valor_pagamento` >= 0);
ALTER TABLE `Substituicao_Ingrediente` ADD CHECK (`id_ingrediente_principal` <> `id_ingrediente_substituto`), ADD CHECK (`nivel_prioridade` > 0);
