DELIMITER //

-- Trigger para inserção
CREATE TRIGGER atualiza_funcao_insert
BEFORE INSERT ON `tabContract Measurement Work Role`
FOR EACH ROW
BEGIN
    DECLARE funcao_valor VARCHAR(36);
    
    -- Busca o valor da função na tabela de referência usando os valores da nova linha
    SELECT name INTO funcao_valor
    FROM `tabContract Item Work Role`
    WHERE parent = NEW.item
    AND funcao = NEW.funcao
    LIMIT 1;
    
    -- Atualiza o campo funcao do novo registro se encontrar um valor
    IF funcao_valor IS NOT NULL THEN
        SET NEW.funcaoitem = funcao_valor;
    END IF;
END//

-- Trigger para atualização
CREATE TRIGGER atualiza_funcao_update
BEFORE UPDATE ON `tabContract Measurement Work Role`
FOR EACH ROW
BEGIN
    DECLARE funcao_valor VARCHAR(36);
    
    -- Busca o valor da função na tabela de referência usando os valores atualizados
    SELECT name INTO funcao_valor
    FROM `tabContract Item Work Role`
    WHERE parent = NEW.item
    AND funcao = NEW.funcao
    LIMIT 1;
    
    -- Atualiza o campo funcao do registro atualizado se encontrar um valor
    IF funcao_valor IS NOT NULL THEN
        SET NEW.funcaoitem = funcao_valor;
    END IF;
END//

DELIMITER ;


