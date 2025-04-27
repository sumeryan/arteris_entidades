import json
from json_to_entity_transformer import transform_json_to_entity_structure

# Exemplo de JSON de entrada (conforme fornecido no requisito)
input_json = {
    "data": {
        "name": "01967343-b7d4-7e20-908c-c48e8cf68789",
        "owner": "Administrator",
        "creation": "2025-04-26 15:02:19.987104",
        "modified": "2025-04-27 11:03:40.115750",
        "modified_by": "Administrator",
        "docstatus": 0,
        "idx": 6,
        "nomeativo": "Automovel",
        "doctype": "Asset",
        "operadoresoumotoristas": [
            {
                "name": "0196778f-92d5-71e2-aea3-e2fbf6faffdb",
                "owner": "Administrator",
                "creation": "2025-04-26 15:02:19.987104",
                "modified": "2025-04-27 11:03:40.115750",
                "modified_by": "Administrator",
                "docstatus": 0,
                "idx": 1,
                "operador": "0196778e-f60f-79f3-8043-3f3089d2a9ac",
                "quantidade": 1,
                "parent": "01967343-b7d4-7e20-908c-c48e8cf68789",
                "parentfield": "operadoresoumotoristas",
                "parenttype": "Asset",
                "doctype": "Asset Operator"
            }
        ]
    }
}

# Exemplo simplificado de metadados de campos (simulando o que seria retornado por get_docfields_for_doctype)
doctypes_metadata = {
    "Asset": [
        {
            "fieldname": "nomeativo",
            "label": "Nome do Ativo",
            "fieldtype": "Data"
        },
        {
            "fieldname": "operadoresoumotoristas",
            "label": "Operadores ou Motoristas",
            "fieldtype": "Table",
            "options": "Asset Operator"
        }
    ],
    "Asset Operator": [
        {
            "fieldname": "operador",
            "label": "Operador/Motorista",
            "fieldtype": "Link",
            "options": "User"
        },
        {
            "fieldname": "quantidade",
            "label": "Quantidade",
            "fieldtype": "Int"
        }
    ]
}

def main():
    print("Iniciando teste do transformador JSON para estrutura de entidades...")
    
    # Transformar o JSON de entrada em estrutura de entidades
    entity_structure = transform_json_to_entity_structure(input_json, doctypes_metadata)
    
    # Imprimir resultado formatado
    print("\nEstrutura de entidades gerada:")
    print(json.dumps(entity_structure, indent=4))
    
    # Salvar resultado em um arquivo
    with open("output_entity_structure.json", "w", encoding="utf-8") as f:
        json.dump(entity_structure, f, indent=4, ensure_ascii=False)
    
    print("\nEstrutura de entidades salva em output_entity_structure.json")

if __name__ == "__main__":
    main()