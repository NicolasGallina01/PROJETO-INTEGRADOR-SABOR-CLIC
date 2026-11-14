-- Aplicar uma vez em bancos criados antes da sessão 5.
USE sabor_clic;
CREATE TABLE IF NOT EXISTS Pedido_Consumo (
    id_pedido INT NOT NULL,
    id_ingrediente INT NOT NULL,
    quantidade DECIMAL(12,3) NOT NULL CHECK (quantidade > 0),
    PRIMARY KEY (id_pedido, id_ingrediente),
    FOREIGN KEY (id_pedido) REFERENCES Pedido(id_pedido),
    FOREIGN KEY (id_ingrediente) REFERENCES Ingrediente(id_ingrediente)
) ENGINE=InnoDB;
