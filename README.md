# JSON para Estrutura de Entidades

Este módulo transforma dados JSON de DocTypes em uma estrutura de entidades padronizada, utilizando metadados de campos para determinar tipos de dados e descrições.

## Funcionalidades

- Transforma dados JSON de DocTypes em uma estrutura de entidades
- Utiliza metadados de campos para determinar tipos e descrições
- Restringe a lista de atributos apenas aos campos listados em doctypes_metadata
- Mapeia tipos de campo para tipos genéricos (string, numeric, datetime, boolean, etc.)
- Processa relacionamentos entre entidades (Table e Link)

## Estrutura de Saída

A estrutura de saída segue o seguinte formato:

```json
{
  "entities": [
    {
      "entity": {
        "type": "string",
        "description": "string",
        "attributes": [
          {
            "key": "string",
            "value": "string|number|boolean|null",
            "type": "string|numeric|datetime|boolean|etc",
            "description": "string"
          }
        ],
        "relationships": [
          {
            "sourceKey": "string",
            "destinationEntity": "string",
            "destinationKey": "string"
          }
        ]
      }
    }
  ]
}
```

## Como Usar

### Importação do Módulo

```python
from json_to_entity_transformer import transform_json_to_entity_structure
```

### Exemplo de Uso

```python
import json
from json_to_entity_transformer import transform_json_to_entity_structure
from get_docktypes import process_arteris_doctypes

# Carregar JSON de entrada
with open('input.json', 'r') as f:
    json_data = json.load(f)

# Obter metadados dos campos
api_base_url = "https://example.com/api/resource"
api_token = "token key:secret"
doctypes_metadata, _, _ = process_arteris_doctypes(api_base_url, api_token)

# Transformar JSON em estrutura de entidades
entity_structure = transform_json_to_entity_structure(json_data, doctypes_metadata)

# Salvar resultado
with open('output.json', 'w') as f:
    json.dump(entity_structure, f, indent=4)
```

### Uso Independente

O módulo pode ser usado de forma independente, sem necessidade de integração com o fluxo existente. Basta fornecer o JSON de entrada e os metadados dos campos.

## Mapeamento de Tipos

O módulo mapeia os tipos de campo do DocType para tipos genéricos:

- **string**: Data, Small Text, Text, Text Editor, Code, Link, Select, Read Only, Color
- **numeric**: Int, Float, Currency, Percent
- **datetime**: Date, Datetime, Time
- **boolean**: Check
- **table**: Table
- **file**: Attach
- **image**: Attach Image, Signature
- **geolocation**: Geolocation

## Tratamento de Relacionamentos

O módulo identifica e processa dois tipos de relacionamentos:

1. **Table**: Para campos do tipo Table, o módulo cria entidades filhas e estabelece relacionamentos onde o campo "parent" da entidade filha se relaciona com o campo "name" da entidade pai.

2. **Link**: Campos do tipo Link são tratados como relacionamentos entre entidades, onde o valor do campo Link se relaciona com o campo "name" da entidade referenciada.

## Exemplo de Saída

Para o seguinte JSON de entrada:

```json
{
    "data": {
        "name": "01967343-b7d4-7e20-908c-c48e8cf68789",
        "nomeativo": "Automovel",
        "doctype": "Asset",
        "operadoresoumotoristas": [
            {
                "name": "0196778f-92d5-71e2-aea3-e2fbf6faffdb",
                "operador": "0196778e-f60f-79f3-8043-3f3089d2a9ac",
                "quantidade": 1,
                "parent": "01967343-b7d4-7e20-908c-c48e8cf68789",
                "doctype": "Asset Operator"
            }
        ]
    }
}
```

A saída seria:

```json
{
    "entities": [
        {
            "entity": {
                "type": "Asset",
                "description": "Entidade representando o DocType Asset",
                "attributes": [
                    {
                        "key": "nomeativo",
                        "value": "Automovel",
                        "type": "string",
                        "description": "Nome do Ativo"
                    }
                ],
                "relationships": []
            }
        },
        {
            "entity": {
                "type": "Asset Operator",
                "description": "Entidade representando o DocType Asset Operator",
                "attributes": [
                    {
                        "key": "operador",
                        "value": "0196778e-f60f-79f3-8043-3f3089d2a9ac",
                        "type": "string",
                        "description": "Operador/Motorista"
                    },
                    {
                        "key": "quantidade",
                        "value": 1,
                        "type": "numeric",
                        "description": "Quantidade"
                    },
                    {
                        "key": "parent",
                        "value": "01967343-b7d4-7e20-908c-c48e8cf68789",
                        "type": "string",
                        "description": "Parent DocType"
                    }
                ],
                "relationships": [
                    {
                        "sourceKey": "parent",
                        "destinationEntity": "Asset",
                        "destinationKey": "name"
                    }
                ]
            }
        }
    ]
}
```

## Requisitos

- Python 3.6+
- Módulo `get_docktypes` para obter metadados dos campos (opcional)