#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para transformar dados da API Arteris em uma estrutura de entidades
compatível com o formato do arquivo engine_entities.js.

Este módulo recebe:
1. Dados de get_data_from_key (exemplo em output_data.json)
2. Lista de entidades de transform_entity_structure (exemplo em output_entity_structure_from_metadata.json)

E cria uma nova lista de entidades conforme o exemplo do arquivo engine_entities.js, seguindo as regras:
- Id = name (Chave)
- A primeira linha de atributos da entidade quando do tipo Child é o valor de parent
"""

import json
import os
import logging
from typing import Dict, List, Any, Tuple, Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Carrega os dados de output_data.json.

    Args:
        file_path (str): Caminho para o arquivo de dados.

    Returns:
        List[Dict[str, Any]]: Lista de objetos com doctype, key e data.

    Raises:
        FileNotFoundError: Se o arquivo não existir.
        json.JSONDecodeError: Se o arquivo não contiver um JSON válido.
    """
    try:
        logger.info(f"Carregando dados de {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        if not isinstance(data, list):
            logger.warning(f"Formato de dados inesperado em {file_path}. Esperava uma lista.")
            return []
        
        logger.info(f"Dados carregados com sucesso: {len(data)} itens")
        return data
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Erro ao decodificar JSON do arquivo: {file_path}")
        raise

def load_entity_structure(file_path: str) -> Dict[str, Any]:
    """
    Carrega a estrutura de entidades de output_entity_structure_from_metadata.json.

    Args:
        file_path (str): Caminho para o arquivo de estrutura de entidades.

    Returns:
        Dict[str, Any]: Objeto com a lista de entidades.

    Raises:
        FileNotFoundError: Se o arquivo não existir.
        json.JSONDecodeError: Se o arquivo não contiver um JSON válido.
    """
    try:
        logger.info(f"Carregando estrutura de entidades de {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            entity_structure = json.load(file)
        
        if not isinstance(entity_structure, dict) or 'entities' not in entity_structure:
            logger.warning(f"Formato de estrutura de entidades inesperado em {file_path}")
            return {'entities': []}
        
        logger.info(f"Estrutura de entidades carregada com sucesso: {len(entity_structure['entities'])} entidades")
        return entity_structure
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Erro ao decodificar JSON do arquivo: {file_path}")
        raise

def identify_entity_relationships(entity_structure: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Analisa o campo "relationships" de cada entidade na estrutura para identificar entidades Child.

    Args:
        entity_structure (Dict[str, Any]): Estrutura de entidades carregada.

    Returns:
        Tuple[Dict[str, str], Dict[str, str]]: 
            - Mapeamento de tipos de entidade para "Parent" ou "Child"
            - Mapeamento de entidades Child para suas entidades Parent
    """
    logger.info("Identificando relacionamentos entre entidades")
    
    # Dicionários para armazenar os mapeamentos
    entity_types = {}  # Tipo de entidade -> "Parent" ou "Child"
    child_to_parent = {}  # Entidade Child -> Entidade Parent
    
    # Conjunto para rastrear todas as entidades
    all_entities = set()
    
    # Primeiro passo: identificar todas as entidades
    for entity_item in entity_structure.get('entities', []):
        entity = entity_item.get('entity', {})
        entity_type = entity.get('type')
        if entity_type:
            all_entities.add(entity_type)
    
    # Segundo passo: analisar relacionamentos para identificar entidades Child
    for entity_item in entity_structure.get('entities', []):
        entity = entity_item.get('entity', {})
        entity_type = entity.get('type')
        relationships = entity.get('relationships', [])
        
        # Verificar se a entidade tem um relacionamento onde o sourceKey é "parent"
        is_child = False
        parent_entity = None
        
        for relationship in relationships:
            source_key = relationship.get('sourceKey')
            destination_entity = relationship.get('destinationEntity')
            
            if source_key == 'parent' and destination_entity:
                is_child = True
                parent_entity = destination_entity
                break
        
        # Definir o tipo da entidade com base nos relacionamentos
        if is_child and parent_entity:
            entity_types[entity_type] = "Child"
            child_to_parent[entity_type] = parent_entity
        else:
            entity_types[entity_type] = "Parent"
    
    # Adicionar tratamento especial para "Contract Item"
    if "Contract Item" in all_entities and "Contract" in all_entities:
        entity_types["Contract Item"] = "Child"
        child_to_parent["Contract Item"] = "Contract"
        logger.info(f"Adicionado tratamento especial para 'Contract Item' como Child de 'Contract'")
    
    logger.info(f"Identificados {len(entity_types)} tipos de entidades")
    logger.info(f"Entidades Child: {list(child_to_parent.keys())}")
    
    return entity_types, child_to_parent

def transform_to_engine_format(
    data: List[Dict[str, Any]], 
    entity_structure: Dict[str, Any], 
    relationships: Tuple[Dict[str, str], Dict[str, str]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Transforma os dados e a estrutura de entidades no formato do engine_entities.js.

    Args:
        data (List[Dict[str, Any]]): Dados carregados.
        entity_structure (Dict[str, Any]): Estrutura de entidades carregada.
        relationships (Tuple[Dict[str, str], Dict[str, str]]): 
            - Mapeamento de tipos de entidade para "Parent" ou "Child"
            - Mapeamento de entidades Child para suas entidades Parent

    Returns:
        Dict[str, List[Dict[str, Any]]]: Objeto no formato {"entities": [...]}.
    """
    logger.info("Transformando dados para o formato engine_entities")
    
    entity_types, child_to_parent = relationships
    engine_entities = []
    
    # Criar um dicionário para mapear tipos de entidade para suas definições
    entity_definitions = {}
    for entity_item in entity_structure.get('entities', []):
        entity = entity_item.get('entity', {})
        entity_type = entity.get('type')
        if entity_type:
            entity_definitions[entity_type] = entity
    
    # Criar um mapeamento de entidades Child para seus campos de array nos pais
    child_array_fields = {}
    for child_type, parent_type in child_to_parent.items():
        # Mapear "Asset Operator" para "operadoresoumotoristas"
        if child_type == "Asset Operator":
            child_array_fields[child_type] = "operadoresoumotoristas"
        else:
            # Convenção: o nome do campo de array é o tipo da entidade Child em minúsculas e no plural
            # Por exemplo, "Asset Operator" -> "assetoperators"
            field_name = child_type.lower().replace(' ', '') + 's'
            child_array_fields[child_type] = field_name
    
    # Processar cada item de dados
    for item in data:
        doctype = item.get('doctype')
        key = item.get('key')
        item_data = item.get('data', {})
        
        # Verificar se temos a definição da entidade
        if doctype not in entity_definitions:
            logger.warning(f"Definição de entidade não encontrada para doctype: {doctype}")
            continue
        
        # Obter a definição da entidade
        entity_definition = entity_definitions[doctype]
        
        # Determinar o tipo da entidade (Parent ou Child)
        entity_type_value = entity_types.get(doctype, "Parent")
        
        # Criar a entidade no formato engine_entities.js
        engine_entity = {
            "id": key,
            "entity_type": [doctype],  # Usar o tipo real da entidade (doctype)
            "attributes": []
        }
        
        # Se for uma entidade Child, o primeiro atributo deve ser o valor de parent
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
        
        # Adicionar os demais atributos
        for attr_def in entity_definition.get('attributes', []):
            attr_key = attr_def.get('key')
            attr_type = attr_def.get('type', 'string')
            
            # Pular o atributo parent para entidades Child (já foi adicionado como primeiro atributo)
            if entity_type_value == "Child" and attr_key == 'parent':
                continue
                
            # Pular o atributo contrato para Contract Item (já foi adicionado como parentId)
            if doctype == "Contract Item" and attr_key == 'contrato':
                continue
            
            # Pular o atributo name (já foi usado como id)
            if attr_key == 'name':
                continue
            
            # Obter o valor do atributo dos dados
            attr_value = item_data.get(attr_key)
            
            # Adicionar o atributo apenas se tiver um valor
            if attr_value is not None:
                # Converter o tipo se necessário
                if attr_type == 'numeric' and isinstance(attr_value, (int, float)):
                    attr_type = 'number'
                    # Converter para string para manter consistência com o formato do engine_entities.js
                    attr_value = str(attr_value)
                
                engine_entity["attributes"].append({
                    "key": attr_key,
                    "value": attr_value,
                    "type": attr_type
                })
        
        # Adicionar a entidade à lista
        engine_entities.append(engine_entity)
        
        # Processar arrays aninhados que podem conter entidades Child
        for child_type, array_field in child_array_fields.items():
            # Verificar se o campo de array existe nos dados
            if array_field in item_data and isinstance(item_data[array_field], list):
                # Verificar se temos a definição da entidade Child
                if child_type not in entity_definitions:
                    logger.warning(f"Definição de entidade Child não encontrada: {child_type}")
                    continue
                
                # Obter a definição da entidade Child
                child_entity_definition = entity_definitions[child_type]
                
                # Processar cada item do array como uma entidade Child
                for child_item in item_data[array_field]:
                    # Verificar se o item tem um campo 'name'
                    if 'name' not in child_item:
                        logger.warning(f"Campo 'name' não encontrado em item de {array_field}")
                        continue
                    
                    # Criar a entidade Child
                    child_entity = {
                        "id": child_item['name'],
                        "entity_type": [child_type],  # Usar o tipo real da entidade Child
                        "attributes": []
                    }
                    
                    # Adicionar o atributo parent como o primeiro atributo
                    child_entity["attributes"].append({
                        "key": "parentId",
                        "value": key,  # ID da entidade pai
                        "type": "string"
                    })
                    
                    # Adicionar os demais atributos
                    for attr_def in child_entity_definition.get('attributes', []):
                        attr_key = attr_def.get('key')
                        attr_type = attr_def.get('type', 'string')
                        
                        # Pular o atributo parent (já foi adicionado como primeiro atributo)
                        if attr_key == 'parent':
                            continue
                        
                        # Pular o atributo name (já foi usado como id)
                        if attr_key == 'name':
                            continue
                        
                        # Obter o valor do atributo dos dados
                        attr_value = child_item.get(attr_key)
                        
                        # Adicionar o atributo apenas se tiver um valor
                        if attr_value is not None:
                            # Converter o tipo se necessário
                            if attr_type == 'numeric' and isinstance(attr_value, (int, float)):
                                attr_type = 'number'
                                # Converter para string para manter consistência com o formato do engine_entities.js
                                attr_value = str(attr_value)
                            
                            child_entity["attributes"].append({
                                "key": attr_key,
                                "value": attr_value,
                                "type": attr_type
                            })
                    
                    # Adicionar a entidade Child à lista
                    engine_entities.append(child_entity)
    
    logger.info(f"Transformação concluída: {len(engine_entities)} entidades geradas")
    
    return {"entities": engine_entities}

def save_engine_entities(engine_entities: Dict[str, List[Dict[str, Any]]], file_path: str) -> None:
    """
    Salva o resultado no formato JSON em um arquivo.

    Args:
        engine_entities (Dict[str, List[Dict[str, Any]]]): Objeto de entidades transformado.
        file_path (str): Caminho para o arquivo de saída.

    Raises:
        IOError: Se houver um erro ao salvar o arquivo.
    """
    try:
        logger.info(f"Salvando entidades no formato engine em {file_path}")
        
        # Garantir que o diretório existe
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(engine_entities, file, indent=4, ensure_ascii=False)
        
        logger.info(f"Entidades salvas com sucesso em {file_path}")
    except IOError as e:
        logger.error(f"Erro ao salvar o arquivo {file_path}: {e}")
        raise

def transform_data_to_engine_entities(
    data: List[Dict[str, Any]], 
    entity_structure: Dict[str, Any]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Função de alto nível que combina as funções acima.

    Args:
        data (List[Dict[str, Any]]): Dados a serem transformados.
        entity_structure (Dict[str, Any]): Estrutura de entidades.

    Returns:
        Dict[str, List[Dict[str, Any]]]: Objeto de entidades transformado.
    """
    logger.info("Iniciando transformação de dados para o formato engine_entities")
    
    # Identificar relacionamentos entre entidades
    relationships = identify_entity_relationships(entity_structure)
    
    # Transformar para o formato engine
    engine_entities = transform_to_engine_format(data, entity_structure, relationships)
    
    logger.info("Transformação concluída")
    
    return engine_entities

def main(
    data_file: Optional[str] = None, 
    entity_structure_file: Optional[str] = None, 
    output_file: Optional[str] = None
) -> None:
    """
    Função principal que orquestra o processo.

    Args:
        data_file (Optional[str]): Caminho para o arquivo de dados (padrão: "output_data.json").
        entity_structure_file (Optional[str]): Caminho para o arquivo de estrutura de entidades 
                                              (padrão: "output_entity_structure_from_metadata.json").
        output_file (Optional[str]): Caminho para o arquivo de saída (padrão: "engine_entities_output.json").
    """
    # Definir valores padrão
    data_file = data_file or "output_data.json"
    entity_structure_file = entity_structure_file or "output_entity_structure_from_metadata.json"
    output_file = output_file or "engine_entities_output.json"
    
    logger.info("Iniciando processamento")
    
    try:
        # Carregar dados
        data = load_data(data_file)
        
        # Carregar estrutura de entidades
        entity_structure = load_entity_structure(entity_structure_file)
        
        # Transformar dados para o formato engine_entities
        engine_entities = transform_data_to_engine_entities(data, entity_structure)
        
        # Salvar resultado
        save_engine_entities(engine_entities, output_file)
        
        logger.info("Processamento concluído com sucesso")
    except Exception as e:
        logger.error(f"Erro durante o processamento: {e}")
        raise

if __name__ == "__main__":
    main()