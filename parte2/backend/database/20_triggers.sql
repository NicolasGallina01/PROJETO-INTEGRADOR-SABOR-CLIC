-- 20_triggers.sql
-- Triggers para regras de negócio no banco (baixa automática de estoque).

DELIMITER //

CREATE TRIGGER tg_baixa_estoque AFTER INSERT ON itens_pedido
FOR EACH ROW
BEGIN
    -- Atualiza a quantidade do estoque para cada ingrediente que compõe o prato
    -- Calcula: (quantidade do prato comprada) * (quantidade necessária do ingrediente)
    UPDATE ingredientes i
    INNER JOIN prato_ingrediente pi ON i.id = pi.ingrediente_id
    SET i.quantidade_estoque = i.quantidade_estoque - (NEW.quantidade * pi.quantidade_necessaria)
    WHERE pi.prato_id = NEW.prato_id;
END //

DELIMITER ;
