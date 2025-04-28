# Plano de Ajuste para Tratamento Especial do DocType "Contract Item"

## Contexto

O DocType "Contract Item" deve ser tratado de forma diferente. Apesar de não ser carregado em subníveis de contrato, ele é um subnível de contrato e deve seguir a mesma regra de subníveis nativos.

## Análise

Analisando o arquivo `output_entity_structure_from_metadata.json`, observamos que:

1. O "Contract Item" (linhas 139-201) tem um relacionamento com "Contract" através do campo "contrato" (linhas 189-193)
2. Diferente do "Asset Operator", o "Contract Item" não tem um campo "parent" explícito em seus atributos
3. O campo "contrato" (linhas 167-171) deve ser tratado como o campo "parent" para o "Contract Item"

## Modificações Necessárias

Precisamos modificar o arquivo `data_to_engine_entities.py` para adicionar uma regra especial para o DocType "Contract Item". As seguintes alterações são necessárias:

1. **Modificar a função `identify_entity_relationships`**:
   - Adicionar uma verificação especial para o DocType "Contract Item"
   - Marcar o "Contract Item" como uma entidade Child, com "Contract" como seu Parent
   - Adicionar ao dicionário `child_to_parent` a relação "Contract Item" -> "Contract"

2. **Modificar a função `transform_to_engine_format`**:
   - Adicionar uma verificação especial para o DocType "Contract Item"
   - Tratar o campo "contrato" como o campo "parent" para o "Contract Item"
   - Garantir que o primeiro atributo seja o valor de "contrato" (chave do registro pai)

## Implementação Detalhada

### 1. Modificação na função `identify_entity_relationships`

```python
# Após o loop que analisa os relacionamentos
# Adicionar tratamento especial para "Contract Item"
if "Contract Item" in all_entities and "Contract" in all_entities:
    entity_types["Contract Item"] = "Child"
    child_to_parent["Contract Item"] = "Contract"
    logger.info(f"Adicionado tratamento especial para 'Contract Item' como Child de 'Contract'")
```

### 2. Modificação na função `transform_to_engine_format`

```python
# No bloco que processa entidades Child
if entity_type_value == "Child":
    parent_key = "parent"
    
    # Tratamento especial para "Contract Item"
    if doctype == "Contract Item":
        parent_key = "contrato"
    
    parent_value = item_data.get(parent_key)
    parent_type = "string"
    
    # Verificar se temos o valor de parent
    if parent_value:
        # Adicionar o atributo parent como o primeiro atributo
        engine_entity["attributes"].append({
            "key": "parentId",
            "value": parent_value,
            "type": parent_type
        })
    else:
        logger.warning(f"Valor de {parent_key} não encontrado para entidade Child: {key}")
```

## Próximos Passos

1. Mudar para o modo Code para implementar as alterações
2. Testar as alterações com dados reais
3. Verificar se o "Contract Item" está sendo tratado corretamente como um subnível de contrato