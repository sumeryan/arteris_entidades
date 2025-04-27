import json # Import json as it might be used indirectly or in future extensions

def transform_to_entity_structure(doctypes_metadata):
    """
    Transforma os metadados de DocTypes e DocFields na estrutura de entidades desejada.

    Args:
        doctypes_metadata (dict): Dicionário onde as chaves são nomes de DocTypes
                                  e os valores são listas de dicionários DocField
                                  (ou None se houve erro ao buscar campos).
                                  Formato: {doctype_name: [{'fieldname': '...', 'label': '...', 'fieldtype': '...'}, ...]}

    Returns:
        dict or None: Um dicionário contendo a chave 'entities', cujo valor é uma lista
                      de entidades formatadas conforme a estrutura especificada.
                      Retorna None se a entrada for inválida.
    """
    if not isinstance(doctypes_metadata, dict):
        print("Erro: Entrada inválida para transform_to_entity_structure.")
        return None

    entities_list = []
    for doctype_name, fields in doctypes_metadata.items():
        if fields is None:
            # Pula DocTypes onde a busca de campos falhou
            print(f"Aviso: Pulando transformação para {doctype_name} devido a erro anterior na busca de campos.")
            continue

        attributes_list = []
        if isinstance(fields, list):
            for field in fields:
                # Verifica se o campo é um dicionário e tem as chaves esperadas
                if isinstance(field, dict) and all(k in field for k in ['fieldname', 'label', 'fieldtype']):
                    # Mapeia fieldtype para um tipo mais genérico se necessário (exemplo simples)
                    field_type = field.get('fieldtype', 'string') # Default para string
                    # Poderia adicionar mapeamentos mais complexos aqui
                    # if field_type in ['Int', 'Float', 'Currency']:
                    #     attribute_type = 'numeric'
                    # elif field_type == 'Date':
                    #     attribute_type = 'datetime'
                    # elif field_type == 'Check':
                    #      attribute_type = 'boolean'
                    # else:
                    #      attribute_type = 'string'

                    attribute_data = {
                        "key": field.get('fieldname'),
                        # "value": field.get('label'), # O valor real virá dos dados, não metadados
                        "type": field_type, # Usando o fieldtype original por enquanto
                        "description": field.get('label') # Usando label como descrição
                    }
                    attributes_list.append(attribute_data)
                else:
                    print(f"Aviso: Campo inválido encontrado para {doctype_name}: {field}")

        entity_data = {
            "type": doctype_name,
            "description": f"Entidade representando o DocType {doctype_name}", # Descrição genérica
            "attributes": attributes_list,
            "relationships": [] # Ignorando relacionamentos conforme solicitado
        }
        entities_list.append({"entity": entity_data})

    return {"entities": entities_list}
