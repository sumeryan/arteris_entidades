import json
import os

def data_to_engine_entities_v3(output_data, output_hierarchical):
    """
    Converte dados do formato output_data para o formato entity_engine,
    respeitando toda a estrutura hierárquica definida em output_hierarchical.
    
    Args:
        output_data (list): Lista de dados dos DocTypes
        output_hierarchical (dict): Dados hierárquicos dos DocTypes
        
    Returns:
        dict: Dados no formato entity_engine
    """
    result = {"entities": []}
    
    # Função auxiliar para obter o tipo de um campo baseado na estrutura hierárquica
    def get_field_type(field_name, entity_type_key):
        for entity in output_hierarchical.get("entities", []):
            if entity["key"] == entity_type_key:
                # Busca direta nos filhos da entidade
                for child in entity.get("children", []):
                    if child["fieldname"] == field_name:
                        return child["type"]
                
                # Busca recursiva nas entidades filhas
                for child in entity.get("children", []):
                    if child["type"] == "doctype":
                        result = get_field_type(field_name, child["key"])
                        if result:
                            return result
        return "string"  # Tipo padrão se não encontrado
    
    # Função auxiliar para obter o entity_type a partir de um doctype
    def get_entity_type(doctype):
        for entity in output_hierarchical.get("entities", []):
            if entity["description"] == doctype:
                return entity["key"]
            
            # Busca em entidades filhas
            for child in entity.get("children", []):
                if child["type"] == "doctype" and child["description"] == doctype:
                    return child["key"]
        
        # Se não encontrar, substitui espaços por underscores
        return doctype.replace(" ", "_")
    
    # Função auxiliar para processar entidades e criar relacionamentos
    def process_entity(data, doctype, entity_id, parent_entity=None, parent_field=None):
        entity_type = get_entity_type(doctype)
        
        # Cria a entidade
        entity = {
            "id": entity_id,
            "entity_type": entity_type,
            "attributes": []
        }
        
        # Se tiver um parent, adiciona como primeiro atributo
        if parent_entity and parent_field:
            entity["attributes"].append({
                "key": parent_field,
                "value": parent_entity,
                "type": "string"
            })
        
        # Adiciona os demais atributos da entidade
        for field_name, field_value in data.items():
            # Ignora campos especiais e tabelas filhas
            if field_name in ["name", "doctype", "parent"] or isinstance(field_value, list):
                continue
                
            # Determina o tipo do campo
            field_type = get_field_type(field_name, entity_type)
            
            # Adiciona o atributo
            entity["attributes"].append({
                "key": field_name,
                "value": field_value,
                "type": field_type
            })
        
        result["entities"].append(entity)
        
        # Processa tabelas filhas (relações)
        for field_name, field_value in data.items():
            if isinstance(field_value, list):
                for child_item in field_value:
                    if "doctype" in child_item and "name" in child_item:
                        child_doctype = child_item["doctype"]
                        child_id = child_item["name"]
                        
                        # Processo recursivamente a entidade filha
                        process_entity(
                            child_item, 
                            child_doctype, 
                            child_id, 
                            entity_id, 
                            entity_type
                        )
    
    # Processa cada documento principal
    for doc in output_data:
        doctype = doc["doctype"]
        key = doc["key"]
        data = doc["data"]
        
        # Processa a entidade principal e suas relações
        process_entity(data, doctype, key)
    
    return result

def get_doctype_mapping(hierarchical_data):
    """
    Cria um mapeamento entre nomes de DocType e suas chaves na hierarquia.
    
    Args:
        hierarchical_data (dict): Dados hierárquicos
        
    Returns:
        dict: Mapeamento de nomes de DocType para chaves
    """
    mapping = {}
    
    def process_entity(entity):
        if entity["type"] == "doctype":
            mapping[entity["description"]] = entity["key"]
        
        for child in entity.get("children", []):
            process_entity(child)
    
    for entity in hierarchical_data.get("entities", []):
        process_entity(entity)
    
    return mapping

def get_data_engine_full_hierarquical(output_data, output_hierarchical):
    """
    Versão melhorada do data_to_engine_entities que processa entidades
    respeitando completamente a estrutura hierárquica.
    
    Args:
        output_data (list): Lista de dados dos DocTypes
        output_hierarchical (dict): Dados hierárquicos dos DocTypes
        
    Returns:
        dict: Dados no formato entity_engine
    """
    result = {"entities": []}
    doctype_mapping = get_doctype_mapping(output_hierarchical)

    # Criar um mapa da hierarquia: { entity_key: { attribute_key: {"fieldname": fieldname, "type": type} } }
    hierarchy_map = {}

    def build_hierarchy_map_recursive(entity, current_map): # Renomeado para build_hierarchy_map_recursive
        entity_key = entity.get("key")
        if not entity_key: return

        if entity_key not in current_map:
            current_map[entity_key] = {}

        for child in entity.get("children", []):
            attribute_key = child.get("key")
            fieldname = child.get("fieldname")
            # Mapeia a 'key' do atributo para seu 'fieldname' e 'type'
            if attribute_key and fieldname:
                current_map[entity_key][attribute_key] = {
                    "fieldname": fieldname,
                    "type": child.get("type", "string")
                }
            # Processa recursivamente as definições de doctypes aninhados
            if child.get("type") == "doctype":
                build_hierarchy_map_recursive(child, current_map) # Chamada recursiva correta

    # Constrói o mapa da hierarquia usando a função correta e a variável correta
    for top_level_entity in output_hierarchical.get("entities", []):
        build_hierarchy_map_recursive(top_level_entity, hierarchy_map) # Chama build_hierarchy_map_recursive com hierarchy_map

    # Função interna para processar cada entidade
    def process_entity(data, parent_info=None):
        """
        Processa uma entidade e suas relações.
        
        Args:
            data (dict): Dados da entidade
            parent_info (tuple, optional): Informações do parent (id, type). Defaults to None.
        """
        doctype = data.get("doctype")
        entity_id = data.get("name")
        
        if not doctype or not entity_id:
            return
        
        # Obtém o entity_type a partir do doctype
        entity_type = doctype_mapping.get(doctype, doctype.replace(" ", "_"))
        
        # Cria a entidade
        entity = {
            "id": entity_id,
            "entity_type": entity_type,
            "attributes": []
        }
        
        # Se tiver parent, adiciona como primeiro atributo
        if parent_info:
            parent_id, parent_type = parent_info
            entity["attributes"].append({
                "key": parent_type,
                "value": parent_id,
                "type": "string"
            })
        
        # Obtém as definições de atributos da hierarquia para este entity_type
        entity_hierarchy_def = hierarchy_map.get(entity_type, {}) # Usa hierarchy_map

        # Itera sobre os atributos definidos na HIERARQUIA para este entity_type
        for attribute_key, field_info in entity_hierarchy_def.items():
            fieldname = field_info.get("fieldname")
            attribute_type = field_info.get("type", "string")

            # --- Debug Print ---
            # print(f"--- Debug ---")
            # print(f"Entity Type: {entity_type}, Entity ID: {entity_id}")
            # print(f"Attribute Key (Hierarchy): {attribute_key}")
            # print(f"Fieldname (Hierarchy): {fieldname}")
            # print(f"Fieldname in data? {fieldname in data if fieldname else 'N/A'}")
            # print(f"Data keys: {list(data.keys())}")
            # --- End Debug Print ---

            # Verifica se o fieldname existe e se o campo correspondente está nos DADOS de entrada
            if fieldname and fieldname in data:
                field_value = data[fieldname]
                # print(f"Field Value Found: {field_value}") # Debug

                # Ignora apenas listas (tratadas na seção "Processa relações")
                # Processa atributos do tipo doctype como links (strings)
                if isinstance(field_value, list):
                    continue

                # Define o tipo do atributo de saída. Se for doctype na hierarquia, usa "string" no output.
                output_attribute_type = "string" if attribute_type == "doctype" else attribute_type

                # Adiciona o atributo usando a key da HIERARQUIA, value dos DADOS e o tipo ajustado
                entity["attributes"].append({
                    "key": attribute_key, # Chave da hierarquia
                    "value": field_value, # Valor dos dados (ID do doctype vinculado)
                    "type": output_attribute_type # Tipo ajustado para saída
                })
            # else: O campo definido na hierarquia não foi encontrado nos dados de entrada, ou falta fieldname no mapa. Ignora.
        
        result["entities"].append(entity)
        
        # Processa relações
        for field_name, field_value in data.items():
            if isinstance(field_value, list):
                for child_item in field_value:
                    if isinstance(child_item, dict) and "doctype" in child_item:
                        process_entity(child_item, (entity_id, entity_type))
    
    # Processa cada documento principal
    for doc in output_data:
        if isinstance(doc.get("data"), dict):
            process_entity(doc["data"])
    
    return result

def main():
    """
    Função principal para testar o módulo data_to_engine_entities_v3.py
    usando os arquivos de exemplo.
    """
    # Diretório para saída dos resultados
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Carrega os arquivos de exemplo
    try:
        with open(os.path.join(output_dir, 'output_data.json'), 'r', encoding='utf-8') as f:
            output_data = json.load(f)
        
        # Carrega o arquivo de hierarquia correto
        hierarchical_file_path = os.path.join(output_dir, 'output_hierarchical_entities.json')
        print(f"Carregando hierarquia de: {hierarchical_file_path}") # Debug
        with open(hierarchical_file_path, 'r', encoding='utf-8') as f:
            output_hierarchical = json.load(f)
        
        print("Arquivos de exemplo carregados com sucesso.")

        # Processa usando a função data_to_engine_entities_v3
        result_v3 = data_to_engine_entities_v3(output_data, output_hierarchical)
        
        # Salva o resultado em um arquivo JSON
        with open(os.path.join(output_dir, 'engine_entities_output_v3'), 'w', encoding='utf-8') as f:
            json.dump(result_v3, f, indent=2, ensure_ascii=False)
        
        print(f"Resultado da função data_to_engine_entities_v3 salvo em {os.path.join(output_dir, 'engine_entities_output_v3')}")
        
        # Processa usando a função process_entities_with_hierarchy
        result_hierarchy = get_data_engine_full_hierarquical(output_data, output_hierarchical)
        
        # Salva o resultado em um arquivo JSON
        with open(os.path.join(output_dir, 'result_hierarchy.json'), 'w', encoding='utf-8') as f:
            json.dump(result_hierarchy, f, indent=2, ensure_ascii=False)
        
        print(f"Resultado da função process_entities_with_hierarchy salvo em {os.path.join(output_dir, 'result_hierarchy.json')}")
        
        # Imprime estatísticas
        print("\nEstatísticas dos resultados:")
        print(f"data_to_engine_entities_v3: {len(result_v3['entities'])} entidades")
        print(f"process_entities_with_hierarchy: {len(result_hierarchy['entities'])} entidades")
        
    except FileNotFoundError as e:
        print(f"Erro ao carregar arquivos: {e}")
        print("Certifique-se de que os arquivos output_data.json e output_hierarchical.json estão no mesmo diretório deste script.")
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        print("Verifique se os arquivos JSON estão formatados corretamente.")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()