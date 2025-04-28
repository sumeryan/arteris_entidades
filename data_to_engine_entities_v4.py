# data_to_entity_engine.py
import logging
from typing import Dict, List, Any, Tuple

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _extract_mappings_from_hierarchy(entities: List[Dict[str, Any]]) -> Tuple[Dict[Tuple[str, str], str], Dict[Tuple[str, str], str]]:
    """
    Extrai recursivamente mapeamentos da estrutura hierárquica:
    1. Tipos de atributos: (entity_key, fieldname) -> attribute_type
    2. Labels de atributos: (entity_key, fieldname) -> attribute_label (key da hierarquia)

    Args:
        entities (List[Dict[str, Any]]): Lista de definições de entidades.

    Returns:
        Tuple[Dict[Tuple[str, str], str], Dict[Tuple[str, str], str]]:
            - Mapa de tipos de atributos.
            - Mapa de labels de atributos.
    """
    attribute_type_map = {}
    fieldname_to_label_map = {}

    for entity_def in entities:
        entity_key = entity_def.get('key')
        if not entity_key:
            continue

        logger.debug(f"Extracting mappings for entity: {entity_key}")
        for child_attr in entity_def.get('children', []):
            child_fieldname = child_attr.get('fieldname')
            child_type = child_attr.get('type')
            child_label = child_attr.get('key') # Usar 'key' da hierarquia como label

            if child_fieldname and child_label: # Precisa de ambos para mapear
                if child_type != 'doctype':
                    # É um atributo direto
                    attribute_type_map[(entity_key, child_fieldname)] = child_type
                    fieldname_to_label_map[(entity_key, child_fieldname)] = child_label
                    logger.debug(f"  Mapped attribute: ({entity_key}, {child_fieldname}) -> Type: {child_type}, Label: {child_label}")
                elif child_type == 'doctype' and 'children' in child_attr:
                    # É um doctype filho, chama recursivamente
                    logger.debug(f"  Found child doctype: {child_label}. Recursing.")
                    # Passa a definição do doctype filho em uma lista
                    nested_types, nested_labels = _extract_mappings_from_hierarchy([child_attr])
                    attribute_type_map.update(nested_types)
                    fieldname_to_label_map.update(nested_labels)

    return attribute_type_map, fieldname_to_label_map


def transform_to_entity_engine(output_data: List[Dict[str, Any]], output_hierarchical: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Transforma os dados da API Arteris (formato output_data) para o formato
    entity_engine, utilizando a estrutura hierárquica (output_hierarchical)
    para mapear tipos de entidade e atributos.

    Args:
        output_data (List[Dict[str, Any]]): Lista de dicionários contendo os dados
                                             extraídos (similar a output_data.json).
        output_hierarchical (Dict[str, Any]): Dicionário contendo a estrutura hierárquica
                                              das entidades (similar a output_hierarchical.json).

    Returns:
        Dict[str, List[Dict[str, Any]]]: Dicionário no formato {"entities": [...]}.
    """
    logger.info("Iniciando transformação para formato entity_engine.")
    engine_entities = []

    if not isinstance(output_data, list):
        logger.error("Formato inválido para output_data. Esperava uma lista.")
        return {"entities": []}
    if not isinstance(output_hierarchical, dict) or 'entities' not in output_hierarchical:
        logger.error("Formato inválido para output_hierarchical. Esperava um dicionário com a chave 'entities'.")
        return {"entities": []}

    hierarchical_entities = output_hierarchical.get('entities', [])

    # --- Pré-processamento ---
    logger.info("Criando mapas de lookup a partir da estrutura hierárquica.")

    # 1. Mapa: Descrição do DocType -> Chave/Entity Type (ex: "Contract Measurement" -> "Contract_Measurement")
    doctype_description_to_key_map: Dict[str, str] = {}
    # 2. Mapa: (Entity Type Key, Field Name) -> Tipo do Atributo
    attribute_type_map: Dict[Tuple[str, str], str] = {}
    # 3. Mapa: (Entity Type Key, Field Name) -> Label do Atributo (key da hierarquia)
    fieldname_to_label_map: Dict[Tuple[str, str], str] = {}
    # 4. Mapa: ID do Item -> DocType (ex: "019678b6-..." -> "Contract Measurement")
    id_to_doctype_map: Dict[str, str] = {}
    # 5. Mapa: Chave/Entity Type -> Descrição do DocType (inverso do 1, para achar nome do pai)
    doctype_key_to_description_map: Dict[str, str] = {}


    # Preenche doctype_description_to_key_map e doctype_key_to_description_map
    entities_to_process = list(hierarchical_entities) # Copia para poder modificar
    processed_keys = set() # Para evitar loops infinitos em estruturas recursivas (se houver)

    while entities_to_process:
        entity_def = entities_to_process.pop(0)
        description = entity_def.get('description')
        key = entity_def.get('key')

        if key in processed_keys:
            continue
        processed_keys.add(key)

        if description and key:
            doctype_description_to_key_map[description] = key
            doctype_key_to_description_map[key] = description
            logger.debug(f"Mapeado doctype: '{description}' <-> '{key}'")

        # Adiciona filhos à lista para processamento
        children = entity_def.get('children', [])
        entities_to_process.extend([child for child in children if child.get('type') == 'doctype'])


    # Preenche attribute_type_map e fieldname_to_label_map usando a função auxiliar
    attribute_type_map, fieldname_to_label_map = _extract_mappings_from_hierarchy(hierarchical_entities)
    logger.info(f"Mapa de tipos de atributos: {attribute_type_map}")
    logger.info(f"Mapa de labels de atributos: {fieldname_to_label_map}")


    # Preenche id_to_doctype_map
    items_to_process = list(output_data)
    processed_item_ids = set()

    while items_to_process:
        item = items_to_process.pop(0)
        item_id = item.get('key') or item.get('data', {}).get('name')

        if not item_id or item_id in processed_item_ids:
            continue
        processed_item_ids.add(item_id)

        doctype = item.get('doctype')
        if doctype:
            id_to_doctype_map[item_id] = doctype
            logger.debug(f"Mapeado ID->Doctype: '{item_id}' -> '{doctype}'")

        # Processa também os itens dentro das tabelas filhas (listas de dicionários)
        item_data = item.get('data', {})
        for key, value in item_data.items():
            if isinstance(value, list):
                for sub_item in value:
                    if isinstance(sub_item, dict):
                        # Adiciona sub-item à lista para processamento completo
                        # Cria um item simulado no formato esperado
                        simulated_item = {
                            "doctype": sub_item.get("doctype"),
                            "key": sub_item.get("name"), # Usa 'name' como 'key' para filhos
                            "data": sub_item
                        }
                        # Adiciona apenas se tiver doctype e key/name
                        if simulated_item["doctype"] and simulated_item["key"]:
                             items_to_process.append(simulated_item)


    logger.info(f"Mapas criados: {len(doctype_description_to_key_map)} doctypes desc->key, {len(doctype_key_to_description_map)} doctypes key->desc, {len(attribute_type_map)} atributos tipados, {len(fieldname_to_label_map)} labels mapeados, {len(id_to_doctype_map)} IDs mapeados.")

    # --- Lógica de Transformação Principal ---
    logger.info("Iniciando processamento dos itens de dados.")

    processed_ids_main_loop = set() # Para evitar duplicatas se um item filho também estiver na lista raiz

    items_to_process_main = list(output_data) # Copia para iterar

    while items_to_process_main:
        item = items_to_process_main.pop(0)
        item_data = item.get('data', {})
        item_id = item.get('key') or item_data.get('name')
        doctype_desc = item.get('doctype') # Descrição como "Contract Measurement"

        if not item_id or not doctype_desc:
            logger.warning(f"Item ignorado por falta de ID ou doctype: {item}")
            continue

        if item_id in processed_ids_main_loop:
            continue # Já processado
        processed_ids_main_loop.add(item_id)

        # Obter a chave/entity_type (ex: "Contract_Measurement")
        entity_type = doctype_description_to_key_map.get(doctype_desc)
        if not entity_type:
            logger.warning(f"Não foi possível encontrar a chave para o doctype '{doctype_desc}'. Item ID: {item_id}")
            continue

        logger.debug(f"Processando item ID: {item_id}, Doctype: {doctype_desc}, Entity Type: {entity_type}")

        current_attributes = []

        # Verificar se é um filho (tem 'parent' nos dados)
        parent_id = item_data.get('parent')
        if parent_id:
            parent_doctype_desc = id_to_doctype_map.get(parent_id)
            if parent_doctype_desc:
                parent_entity_type = doctype_description_to_key_map.get(parent_doctype_desc)
                if parent_entity_type:
                    current_attributes.append({
                        "key": parent_entity_type, # Chave é o Entity Type do pai
                        "value": parent_id,
                        "type": "string" # Assume-se que IDs de relação são strings
                    })
                    logger.debug(f"  Adicionado atributo pai: {parent_entity_type} -> {parent_id}")
                else:
                    logger.warning(f"  Não foi possível encontrar a chave para o doctype pai '{parent_doctype_desc}' do item {item_id}")
            else:
                logger.warning(f"  Não foi possível encontrar o doctype para o parent ID '{parent_id}' do item {item_id}")

        # Iterar sobre os campos de dados para criar atributos
        for field_name, field_value in item_data.items():
            # Ignorar campos que não são atributos diretos
            if field_name in ['name', 'doctype', 'parent'] or isinstance(field_value, list):
                 # Listas são tratadas separadamente, pois seus itens são processados como entidades individuais
                continue

            # Determinar a chave (label) e o tipo do atributo
            attribute_type = "string" # Padrão
            attribute_key = field_name # Padrão é o fieldname

            lookup_key = (entity_type, field_name)

            # Buscar label no mapa
            if lookup_key in fieldname_to_label_map:
                attribute_key = fieldname_to_label_map[lookup_key]
                logger.debug(f"  Label para {lookup_key} encontrado: {attribute_key}")
            else:
                logger.debug(f"  Label para {lookup_key} não encontrado, usando fieldname: {field_name}")

            # Buscar tipo no mapa
            if lookup_key in attribute_type_map:
                attribute_type = attribute_type_map[lookup_key]
                # Ajustar tipos numéricos para "numeric" conforme solicitado
                if attribute_type in ['numeric', 'integer', 'float', 'currency', 'number']:
                     attribute_type = 'numeric'
                # Outros tipos ('date', 'datetime', 'boolean', 'string') mantidos
                logger.debug(f"  Tipo para {lookup_key} encontrado: {attribute_type_map[lookup_key]} (usado como: {attribute_type})")
            else:
                # Inferir tipo básico se não encontrado
                if isinstance(field_value, (int, float)):
                    attribute_type = "numeric"
                elif isinstance(field_value, bool):
                    attribute_type = "boolean"
                logger.debug(f"  Tipo para {lookup_key} não encontrado, inferido como {attribute_type}")


            current_attributes.append({
                "key": attribute_key, # Usar o label ou fieldname como chave
                "value": field_value,
                "type": attribute_type
            })
            logger.debug(f"  Adicionado atributo: {attribute_key} -> {field_value} (Tipo: {attribute_type})")

        # Criar a entidade final
        engine_entity = {
            "id": item_id,
            "entity_type": entity_type, # Usar a chave como entity_type
            "attributes": current_attributes
        }
        engine_entities.append(engine_entity)

        # Adicionar itens de listas filhas à fila de processamento principal
        for key, value in item_data.items():
             if isinstance(value, list):
                 for sub_item in value:
                     if isinstance(sub_item, dict):
                         simulated_item = {
                             "doctype": sub_item.get("doctype"),
                             "key": sub_item.get("name"),
                             "data": sub_item # Passa o sub_item como 'data'
                         }
                         if simulated_item["doctype"] and simulated_item["key"]:
                              # Adiciona no início da lista para processar filhos antes de irmãos distantes
                              items_to_process_main.insert(0, simulated_item)


    logger.info(f"Transformação para entity_engine concluída. {len(engine_entities)} entidades geradas.")
    return {"entities": engine_entities}