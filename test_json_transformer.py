import json
# Importa a nova função refatorada
from json_to_entity_transformer import transform_entity_structure

# Exemplo de metadados de campos (simulando doctypes_with_fields)
# Adicionamos mais detalhes e um terceiro DocType para um teste mais completo
doctypes_with_fields_example = {
    "Asset": [
        {"fieldname": "name", "label": "ID", "fieldtype": "Data"}, # Campo 'name' geralmente existe
        {"fieldname": "nomeativo", "label": "Nome do Ativo", "fieldtype": "Data"},
        {"fieldname": "status", "label": "Status", "fieldtype": "Select"},
        {"fieldname": "operadoresoumotoristas", "label": "Operadores ou Motoristas", "fieldtype": "Table", "options": "Asset Operator"}
    ],
    "Asset Operator": [
        {"fieldname": "name", "label": "ID", "fieldtype": "Data"},
        {"fieldname": "operador", "label": "Operador/Motorista", "fieldtype": "Link", "options": "User"},
        {"fieldname": "quantidade", "label": "Quantidade", "fieldtype": "Int"},
        # O campo 'parent' nos metadados do filho não é estritamente necessário aqui,
        # pois a função refatorada adiciona baseado no child_parent_mapping,
        # mas pode estar presente nos dados reais.
        {"fieldname": "parent", "label": "Parent", "fieldtype": "Data", "parent": "Asset Operator"}
    ],
    "User": [ # DocType referenciado pelo Link em Asset Operator
        {"fieldname": "name", "label": "ID", "fieldtype": "Data"},
        {"fieldname": "full_name", "label": "Nome Completo", "fieldtype": "Data"}
    ]
}

# Exemplo de mapeamento child-parent (simulando child_parent_mapping)
# Derivado do campo 'Table' em 'Asset'
child_parent_mapping_example = [
    {"child": "Asset Operator", "parent": "Asset"}
]

# Estrutura de saída esperada (para referência ou futuras asserções)
expected_output_structure = {
  "entities": [
    {
      "entity": {
        "type": "Asset",
        "description": "Entidade representando o DocType Asset",
        "attributes": [
          # 'name' é ignorado por padrão na função process_attributes
          {
            "key": "nomeativo",
            "type": "string",
            "description": "Nome do Ativo"
          },
          {
            "key": "status",
            "type": "string", # Mapeado de Select
            "description": "Status"
          }
          # O campo Table 'operadoresoumotoristas' não vira atributo
        ],
        "relationships": [] # Asset é pai, não tem relacionamento definido aqui
      }
    },
    {
      "entity": {
        "type": "Asset Operator",
        "description": "Entidade representando o DocType Asset Operator",
        "attributes": [
           # 'name' é ignorado
          {
            "key": "operador",
            "type": "string", # Mapeado de Link
            "description": "Operador/Motorista"
          },
          {
            "key": "quantidade",
            "type": "numeric", # Mapeado de Int
            "description": "Quantidade"
          },
          { # Adicionado pela função create_entity por ser filho
            "key": "parent",
            "type": "string",
            "description": "Parent DocType"
          }
        ],
        "relationships": [ # Adicionado pela função create_entity por ser filho
          {
            "sourceKey": "parent",
            "destinationEntity": "Asset",
            "destinationKey": "name"
          }
        ]
      }
    },
    { # Incluído porque estava em doctypes_with_fields_example
       "entity": {
         "type": "User",
         "description": "Entidade representando o DocType User",
         "attributes": [
            # 'name' é ignorado
           {
             "key": "full_name",
             "type": "string",
             "description": "Nome Completo"
           }
         ],
         "relationships": [] # Não é filho no mapeamento
       }
     }
  ]
}


def main():
    print("Iniciando teste do transformador (baseado em metadados)...")

    # Transformar os metadados em estrutura de entidades
    # Usando a nova função e os novos dados de exemplo
    entity_structure = transform_entity_structure(
        doctypes_with_fields_example,
        child_parent_mapping_example
    )

    # Imprimir resultado formatado
    print("\nEstrutura de entidades gerada (baseada em metadados):")
    print(json.dumps(entity_structure, indent=4))

    # Salvar resultado em um arquivo com novo nome
    output_filename = "output_entity_structure_from_metadata.json"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(entity_structure, f, indent=4, ensure_ascii=False)
        print(f"\nEstrutura de entidades salva em {output_filename}")
    except IOError as e:
        print(f"\nErro ao salvar o arquivo {output_filename}: {e}")

    # Adicionar uma verificação simples (opcional, mas recomendado)
    # Compara a estrutura gerada com a esperada (ignorando a ordem das entidades)
    generated_entities = sorted(entity_structure['entities'], key=lambda x: x['entity']['type'])
    expected_entities = sorted(expected_output_structure['entities'], key=lambda x: x['entity']['type'])

    if generated_entities == expected_entities:
        print("\nVerificação: A estrutura gerada corresponde à esperada.")
    else:
        print("\nVerificação: AVISO - A estrutura gerada NÃO corresponde à esperada.")
        # Poderia imprimir diffs aqui para depuração

if __name__ == "__main__":
    main()