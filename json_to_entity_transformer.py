import json

def transform_json_to_entity_structure(json_data, doctypes_metadata):
    """
    Transforma dados JSON de um DocType em uma estrutura de entidades.
    
    Args:
        json_data (dict): Dados JSON do DocType
        doctypes_metadata (dict): Metadados dos campos dos DocTypes
        
    Returns:
        dict: Estrutura de entidades no formato especificado
    """
    # Extrair informações do DocType principal
    doctype_name, doctype_data = extract_doctype_info(json_data)
    
    # Verificar se temos metadados para este DocType
    if doctype_name not in doctypes_metadata:
        print(f"Aviso: DocType {doctype_name} não encontrado nos metadados.")
        fields_metadata = []
    else:
        fields_metadata = doctypes_metadata[doctype_name]
    
    # Criar entidade principal
    entity = create_entity(doctype_name, doctype_data, fields_metadata)
    
    # Lista para armazenar todas as entidades
    entities = [entity]
    
    # Processar campos do tipo Table (entidades filhas)
    child_entities, relationships = process_table_fields(entity, fields_metadata, json_data, doctypes_metadata)
    
    # Adicionar entidades filhas à lista de entidades
    entities.extend(child_entities)
    
    # Processar campos do tipo Link (relacionamentos)
    link_relationships = process_link_fields(entity, fields_metadata, doctypes_metadata)
    
    # Adicionar relacionamentos de Link à lista de relacionamentos
    relationships.extend(link_relationships)
    
    # Adicionar relacionamentos às entidades
    for i, entity_data in enumerate(entities):
        if entity_data["entity"]["type"] == doctype_name:
            entities[i]["entity"]["relationships"] = relationships
    
    # Retornar estrutura final
    return {"entities": entities}

def extract_doctype_info(json_data):
    """
    Extrai informações do DocType principal do JSON de entrada.
    
    Args:
        json_data (dict): Dados JSON do DocType
        
    Returns:
        tuple: (doctype_name, doctype_data)
    """
    # Verificar se o JSON tem a estrutura esperada
    if "data" not in json_data:
        raise ValueError("JSON inválido: chave 'data' não encontrada")
    
    data = json_data["data"]
    
    # Extrair nome do DocType
    if "doctype" not in data:
        raise ValueError("JSON inválido: chave 'doctype' não encontrada em 'data'")
    
    doctype_name = data["doctype"]
    
    return doctype_name, data

def create_entity(doctype_name, doctype_data, fields_metadata):
    """
    Cria uma entidade a partir dos dados do DocType.
    
    Args:
        doctype_name (str): Nome do DocType
        doctype_data (dict): Dados do DocType
        fields_metadata (list): Metadados dos campos do DocType
        
    Returns:
        dict: Entidade no formato especificado
    """
    # Processar atributos
    attributes = process_attributes(doctype_data, fields_metadata)
    
    # Criar estrutura da entidade
    entity = {
        "entity": {
            "type": doctype_name,
            "description": f"Entidade representando o DocType {doctype_name}",
            "attributes": attributes,
            "relationships": []
        }
    }
    
    return entity

def process_attributes(doctype_data, fields_metadata):
    """
    Processa os atributos da entidade.
    
    Args:
        doctype_data (dict): Dados do DocType
        fields_metadata (list): Metadados dos campos
        
    Returns:
        list: Lista de atributos processados
    """
    attributes = []
    
    # Criar um dicionário para acesso rápido aos metadados dos campos
    fields_dict = {}
    if fields_metadata:
        for field in fields_metadata:
            if "fieldname" in field:
                fields_dict[field["fieldname"]] = field
    
    # Processar cada campo nos dados
    for key, value in doctype_data.items():
        # Ignorar campos especiais e listas (serão tratados como relacionamentos)
        if key in ["doctype", "name", "parentfield", "parenttype"] or isinstance(value, list):
            continue
        
        # Verificar se temos metadados para este campo
        if key in fields_dict:
            field_metadata = fields_dict[key]
            field_type = field_metadata.get("fieldtype", "Data")
            description = field_metadata.get("label", key)
            
            # Mapear tipo de campo para tipo genérico
            generic_type = map_field_type(field_type, key)
            
            # Criar atributo
            attribute = {
                "key": key,
                "value": value if value is not None else None,
                "type": generic_type,
                "description": description
            }
            
            attributes.append(attribute)
        elif key == "parent":
            # Incluir o campo parent como atributo para relacionamento
            field_type = "Link"
            description = "Parent DocType"
            
            # Mapear tipo de campo para tipo genérico
            generic_type = map_field_type(field_type, key)
            
            # Criar atributo
            attribute = {
                "key": key,
                "value": value if value is not None else None,
                "type": generic_type,
                "description": description
            }
            
            attributes.append(attribute)
        
    # Não precisamos do código aqui, pois já estamos criando os atributos acima
    
    return attributes

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
        "Table": "table",
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
        return "string"
    
    # Este código não será executado devido à modificação acima
    # Mantido apenas para referência
    return type_mapping.get(field_type, "string")

def process_table_fields(entity, fields_metadata, json_data, doctypes_metadata):
    """
    Processa campos do tipo Table e cria entidades filhas.
    
    Args:
        entity (dict): Entidade principal
        fields_metadata (list): Metadados dos campos
        json_data (dict): Dados JSON completos
        doctypes_metadata (dict): Metadados de todos os DocTypes
        
    Returns:
        tuple: (entidades_filhas, relacionamentos)
    """
    child_entities = []
    relationships = []
    
    # Extrair nome do DocType principal
    doctype_name = entity["entity"]["type"]
    doctype_data = json_data["data"]
    
    # Identificar campos do tipo Table
    table_fields = []
    if fields_metadata:
        for field in fields_metadata:
            if field.get("fieldtype") == "Table" and field.get("fieldname") in doctype_data:
                table_fields.append(field)
    
    # Processar cada campo Table
    for field in table_fields:
        field_name = field.get("fieldname")
        child_doctype = field.get("options")
        
        # Verificar se temos dados para este campo
        if field_name not in doctype_data or not isinstance(doctype_data[field_name], list):
            continue
        
        # Verificar se temos metadados para o DocType filho
        if child_doctype not in doctypes_metadata:
            print(f"Aviso: DocType filho {child_doctype} não encontrado nos metadados.")
            child_fields_metadata = []
        else:
            child_fields_metadata = doctypes_metadata[child_doctype]
        
        # Processar cada item na lista
        for child_data in doctype_data[field_name]:
            # Criar entidade filha
            child_entity = create_entity(child_doctype, child_data, child_fields_metadata)
            
            # Adicionar relacionamento na entidade filha
            child_relationship = create_relationship(
                child_doctype,
                "parent",
                doctype_name,
                "name"
            )
            
            # Adicionar relacionamento à entidade filha
            if "relationships" not in child_entity["entity"]:
                child_entity["entity"]["relationships"] = []
            
            child_entity["entity"]["relationships"].append(child_relationship)
            
            child_entities.append(child_entity)
    
    # Retornamos apenas as entidades filhas, os relacionamentos já foram adicionados a elas
    return child_entities, []

def process_link_fields(entity, fields_metadata, doctypes_metadata):
    """
    Processa campos do tipo Link e cria relacionamentos.
    
    Args:
        entity (dict): Entidade principal
        fields_metadata (list): Metadados dos campos
        doctypes_metadata (dict): Metadados de todos os DocTypes
        
    Returns:
        list: Lista de relacionamentos
    """
    relationships = []
    
    # Extrair nome do DocType e atributos
    doctype_name = entity["entity"]["type"]
    attributes = entity["entity"]["attributes"]
    
    # Identificar campos do tipo Link
    link_fields = []
    if fields_metadata:
        for field in fields_metadata:
            if field.get("fieldtype") == "Link":
                link_fields.append(field)
    
    # Processar cada campo Link
    for field in link_fields:
        field_name = field.get("fieldname")
        linked_doctype = field.get("options")
        
        # Verificar se temos um atributo para este campo
        has_attribute = False
        for attr in attributes:
            if attr["key"] == field_name:
                has_attribute = True
                # Criar relacionamento
                relationship = create_relationship(
                    doctype_name,
                    field_name,
                    linked_doctype,
                    "name"
                )
                relationships.append(relationship)
                break
    
    return relationships

def create_relationship(source_entity, source_key, destination_entity, destination_key):
    """
    Cria um relacionamento entre entidades.
    
    Args:
        source_entity (str): Nome da entidade de origem
        source_key (str): Chave na entidade de origem
        destination_entity (str): Nome da entidade de destino
        destination_key (str): Chave na entidade de destino
        
    Returns:
        dict: Relacionamento no formato especificado
    """
    return {
        "sourceKey": source_key,
        "destinationEntity": destination_entity,
        "destinationKey": destination_key
    }

# Exemplo de uso (comentado)
"""
# Exemplo de como o módulo será usado
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
"""

if __name__ == "__main__":
    # Código de teste pode ser adicionado aqui
    pass