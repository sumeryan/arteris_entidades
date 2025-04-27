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

