import json

def map_field_type(field_type, key=None):
    """
    Mapeia tipos de campo do DocType para tipos genéricos.

    Args:
        field_type (str): Tipo de campo do DocType
        key (str, optional): Nome do campo, usado para campos especiais

    Returns:
        str: Tipo genérico (string, numeric, datetime, boolean, etc.)
    """
    # Mapeamento de tipos de campo para tipos genéricos
    type_mapping = {
        # Tipos de texto
        "Data": "string",
        "Small Text": "string",
        "Text": "string",
        "Text Editor": "string",
        "Code": "string",
        "Link": "string",
        "Select": "string",
        "Read Only": "string",

        # Tipos numéricos
        "Int": "numeric",
        "Float": "numeric",
        "Currency": "numeric",
        "Percent": "numeric",

        # Tipos de data/hora
        "Date": "datetime",
        "Datetime": "datetime",
        "Time": "datetime",

        # Tipos booleanos
        "Check": "boolean",

        # Outros tipos
        "Table": "table", # Mantido para referência, mas ignorado em process_attributes
        "Attach": "file",
        "Attach Image": "image",
        "Signature": "image",
        "Color": "string",
        "Geolocation": "geolocation"
    }

    # Campos especiais que têm tipos específicos
    special_fields = {
        "creation": "datetime",
        "modified": "datetime",
        "docstatus": "numeric",
        "idx": "numeric"
    }

    # Verificar se é um campo especial
    if field_type in type_mapping:
        return type_mapping[field_type]
    elif key in special_fields:
        return special_fields[key]
    else:
        # Retorna 'string' como padrão se o tipo não for mapeado
        return "string"

def process_attributes(fields_metadata, is_child=False):
    """
    Processa os atributos da entidade a partir dos metadados dos campos.

    Args:
        fields_metadata (list): Metadados dos campos
        is_child (bool): Indica se é uma entidade filha

    Returns:
        list: Lista de atributos processados (sem o campo 'value')
    """
    attributes = []

    # Processar cada campo nos metadados
    for field in fields_metadata:
        field_name = field.get("fieldname")
        field_type = field.get("fieldtype")

        # Ignorar campos do tipo Table (serão tratados como entidades separadas)
        if field_type == "Table":
            continue

        # Ignorar campos internos/específicos que não devem ser atributos diretos,
        # incluindo 'parent', que é tratado separadamente em create_entity.
        if field_name in ["name", "owner", "creation", "modified", "modified_by",
                          "docstatus", "idx", "parentfield", "parenttype", "doctype",
                          "parent"]: # Adicionado 'parent' à lista de ignorados
            continue

        # Mapear tipo de campo para tipo genérico
        generic_type = map_field_type(field_type, field_name)

        # Criar atributo sem o campo 'value'
        attribute = {
            "key": field_name,
            "type": generic_type,
            "description": field.get("label", field_name) # Usa label ou fieldname
        }

        # A lógica de adicionar 'parent' ao atributo foi movida para create_entity
        # if is_child and field.get("parent"):
        #     attribute["parent"] = field.get("parent") # Esta linha foi removida

        attributes.append(attribute)

    return attributes

def create_entity(doctype_name, fields_metadata, is_child=False, parent_doctype=None):
    """
    Cria uma entidade a partir dos metadados dos campos.

    Args:
        doctype_name (str): Nome do DocType
        fields_metadata (list): Metadados dos campos do DocType
        is_child (bool): Indica se é uma entidade filha
        parent_doctype (str): Nome do DocType pai, se for uma entidade filha

    Returns:
        dict: Entidade no formato especificado
    """
    # Processar atributos (sem valores)
    attributes = process_attributes(fields_metadata, is_child)

    # Adicionar atributo 'parent' explicitamente para entidades filhas
    if is_child and parent_doctype:
        # Verifica se o atributo 'parent' já existe (caso venha dos metadados)
        parent_attr_exists = any(attr['key'] == 'parent' for attr in attributes)
        if not parent_attr_exists:
             attributes.append({
                 "key": "parent",
                 "type": "string", # Assumindo que a referência ao pai é uma string (ID/nome)
                 "description": "Parent DocType"
             })

    # Criar relacionamentos (apenas para entidades filhas, apontando para o pai)
    relationships = []
    if is_child and parent_doctype:
        relationships.append({
            "sourceKey": "parent", # A chave na entidade filha que aponta para o pai
            "destinationEntity": parent_doctype, # O tipo da entidade pai
            "destinationKey": "name" # A chave na entidade pai (geralmente 'name')
        })

    # Criar estrutura da entidade
    entity = {
        "entity": {
            "type": doctype_name,
            "description": f"Entidade representando o DocType {doctype_name}",
            "attributes": attributes,
            "relationships": relationships
        }
    }

    return entity

def transform_entity_structure(doctypes_with_fields, child_parent_mapping):
    """
    Transforma metadados de DocTypes em uma estrutura de entidades,
    baseado apenas nos metadados e no mapeamento child-parent.

    Args:
        doctypes_with_fields (dict): Dicionário onde as chaves são nomes de DocTypes
                                     e os valores são listas de metadados de campos.
        child_parent_mapping (list): Lista de dicionários, cada um com chaves 'child'
                                     e 'parent', representando relacionamentos Table.

    Returns:
        dict: Estrutura de entidades no formato {"entities": [...]}.
    """
    entities = []

    # 1. Criar um dicionário para mapear child -> parent para acesso rápido
    child_to_parent = {}
    if child_parent_mapping:
        for mapping in child_parent_mapping:
            child = mapping.get("child")
            parent = mapping.get("parent")
            if child and parent:
                child_to_parent[child] = parent

    # 2. Processar cada DocType presente nos metadados
    processed_doctypes = set() # Para evitar duplicatas se um DocType aparecer como pai e filho
    for doctype_name, fields_metadata in doctypes_with_fields.items():
        # Ignorar DocTypes sem metadados de campos válidos
        if not fields_metadata or not isinstance(fields_metadata, list):
            print(f"Aviso: Metadados inválidos ou vazios para DocType {doctype_name}. Ignorando.")
            continue

        # Verificar se este DocType é um child
        is_child = doctype_name in child_to_parent
        parent_doctype = child_to_parent.get(doctype_name) if is_child else None

        # Criar a entidade
        entity_data = create_entity(doctype_name, fields_metadata, is_child, parent_doctype)

        # Adicionar a entidade à lista
        entities.append(entity_data)
        processed_doctypes.add(doctype_name)

    # 3. Garantir que todos os DocTypes (pais e filhos) foram incluídos
    #    Esta etapa pode não ser necessária se doctypes_with_fields já contém todos.
    #    Mas é uma verificação extra.
    all_involved_doctypes = set(doctypes_with_fields.keys())
    if child_parent_mapping:
        for mapping in child_parent_mapping:
            all_involved_doctypes.add(mapping.get("child"))
            all_involved_doctypes.add(mapping.get("parent"))

    for doctype_name in all_involved_doctypes:
        if doctype_name and doctype_name not in processed_doctypes:
            # Se um DocType (provavelmente um pai que não tem filhos diretos listados
            # ou um filho sem metadados) não foi processado, processa agora.
            fields_metadata = doctypes_with_fields.get(doctype_name, []) # Pega metadados ou lista vazia
            if not fields_metadata:
                 print(f"Aviso: DocType {doctype_name} mencionado em mapeamento mas sem metadados de campos. Criando entidade vazia.")

            is_child = doctype_name in child_to_parent
            parent_doctype = child_to_parent.get(doctype_name) if is_child else None

            entity_data = create_entity(doctype_name, fields_metadata, is_child, parent_doctype)
            entities.append(entity_data)
            processed_doctypes.add(doctype_name)


    # Retornar estrutura final
    return {"entities": entities}
