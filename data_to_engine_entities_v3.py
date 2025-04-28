import json
import os

def data_to_engine_entities_v3(output_data, output_hierarchical):
    """
    Converte dados do formato output_data para o formato entity_engine,
    usando as chaves hierárquicas em output_hierarchical.
    
    Args:
        output_data (list): Lista de dados dos DocTypes
        output_hierarchical (dict): Dados hierárquicos dos DocTypes
        
    Returns:
        dict: Dados no formato entity_engine
    """
    result = {"entities": []}
    
    # Mapeamento de doctypes para seus entity_types
    doctype_entity_map = {}
    # Mapeamento de fieldname para key hierárquica
    field_key_map = {}
    
    # Constrói o mapeamento para entity_types e chaves de campos
    for entity in output_hierarchical.get("entities", []):
        doctype_entity_map[entity["description"]] = entity["key"]
        
        # Mapeia campos diretos
        for child in entity.get("children", []):
            if "fieldname" in child:
                field_key = f"{entity['key']}.{child['fieldname']}"
                field_key_map[field_key] = {
                    "key": child["key"],
                    "type": child["type"]
                }
            
            # Processa entidades filhas recursivamente
            if child.get("type") == "doctype":
                doctype_entity_map[child["description"]] = child["key"]
                
                # Mapeia campos da entidade filha
                for grandchild in child.get("children", []):
                    if "fieldname" in grandchild:
                        field_key = f"{child['key']}.{grandchild['fieldname']}"
                        field_key_map[field_key] = {
                            "key": grandchild["key"],
                            "type": grandchild["type"]
                        }
    
    # Função para obter entity_type a partir do doctype
    def get_entity_type(doctype):
        return doctype_entity_map.get(doctype, doctype.replace(" ", "_"))
    
    # Função para obter informações do campo (key e type)
    def get_field_info(entity_type, field_name):
        field_key = f"{entity_type}.{field_name}"
        field_info = field_key_map.get(field_key, None)
        
        if field_info:
            return field_info["key"], field_info["type"]
        
        # Se não encontrou, retorna o próprio nome do campo e tipo padrão
        return field_name, "string"
    
    # Função recursiva para processar entidades e suas relações
    def process_entity(data, parent_info=None):
        if not isinstance(data, dict) or "doctype" not in data or "name" not in data:
            return
        
        doctype = data["doctype"]
        entity_id = data["name"]
        entity_type = get_entity_type(doctype)
        
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
        
        # Adiciona atributos usando as chaves hierárquicas
        for field_name, field_value in data.items():
            # Ignora campos especiais e listas
            if field_name in ["name", "doctype", "parent"] or isinstance(field_value, list):
                continue
            
            # Obtém a chave hierárquica e o tipo do campo
            field_key, field_type = get_field_info(entity_type, field_name)
            
            # Adiciona o atributo
            entity["attributes"].append({
                "key": field_key,
                "value": field_value,
                "type": field_type
            })
        
        # Adiciona a entidade ao resultado
        result["entities"].append(entity)
        
        # Processa tabelas filhas (relações)
        for field_name, field_value in data.items():
            if isinstance(field_value, list):
                for child_item in field_value:
                    if isinstance(child_item, dict) and "doctype" in child_item and "name" in child_item:
                        # Processa recursivamente a entidade filha
                        process_entity(child_item, (entity_id, entity_type))
    
    # Processa cada entrada de dados
    for doc in output_data:
        if "data" in doc:
            process_entity(doc["data"])
        else:
            process_entity(doc)
    
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
        with open('output_data.json', 'r', encoding='utf-8') as f:
            output_data = json.load(f)
        
        with open('output_hierarchical_entities.json', 'r', encoding='utf-8') as f:
            output_hierarchical = json.load(f)
        
        print("Arquivos de exemplo carregados com sucesso.")

        # Processa os dados usando a função atualizada
        result = data_to_engine_entities_v3(output_data, output_hierarchical)
        
        # Salva o resultado em um arquivo JSON
        result_file = os.path.join(output_dir, 'result_entities_v3.json')
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"Resultado salvo em {result_file}")
        
        # Imprime estatísticas
        print("\nEstatísticas do resultado:")
        print(f"Total de entidades: {len(result['entities'])}")
        
        # Contagem por tipo de entidade
        entity_types = {}
        for entity in result["entities"]:
            entity_type = entity["entity_type"]
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        
        print("\nContagem por tipo de entidade:")
        for entity_type, count in entity_types.items():
            print(f"  {entity_type}: {count} entidades")
            
        # Verifica a cobertura dos nós na hierarquia
        print("\nVerificação de cobertura de nós:")
        
        hierarchy_keys = set()
        for entity in output_hierarchical.get("entities", []):
            hierarchy_keys.add(entity["key"])
            for child in entity.get("children", []):
                if child.get("type") == "doctype":
                    hierarchy_keys.add(child["key"])
        
        result_keys = set()
        for entity in result["entities"]:
            result_keys.add(entity["entity_type"])
        
        covered_keys = hierarchy_keys.intersection(result_keys)
        missing_keys = hierarchy_keys - result_keys
        
        print(f"  Nós na hierarquia: {len(hierarchy_keys)}")
        print(f"  Nós presentes no resultado: {len(covered_keys)}")
        print(f"  Nós faltantes: {len(missing_keys)}")
        
        if missing_keys:
            print("  Lista de nós faltantes:")
            for key in missing_keys:
                print(f"    - {key}")
        
    except FileNotFoundError as e:
        print(f"Erro ao carregar arquivos: {e}")
        print("Certifique-se de que os arquivos output_data.json e output_hierarchical_entities.json estão no mesmo diretório deste script.")
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        print("Verifique se os arquivos JSON estão formatados corretamente.")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()