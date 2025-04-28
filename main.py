"""
Script principal para orquestrar a busca de metadados e dados da API Arteris.

Este script executa as seguintes etapas:
1. Carrega configurações da API do arquivo .env.
2. Busca a lista de DocTypes do módulo 'Arteris' usando api_client.
3. Para cada DocType, busca seus DocFields usando api_client.
4. Transforma os metadados coletados (DocTypes e DocFields) na estrutura
   de entidades JSON usando transformer.
5. Para cada DocType com DocFields, busca os dados reais correspondentes
   usando api_client.
6. Armazena os resultados em dicionários em memória e imprime exemplos.
"""

import os
import json
from dotenv import load_dotenv
from get_docktypes import process_arteris_doctypes
from api_client_data import get_keys, get_data_from_key
from json_to_entity_transformer import create_hierarchical_doctype_structure, process_fields_for_hierarchy
from data_to_engine_entities_v4 import transform_to_entity_engine


# Carrega variáveis de ambiente do arquivo .env na raiz do projeto
load_dotenv()

def main():
    """
    Função principal que orquestra as etapas de busca e transformação.
    """
    # Obtém a URL base e o token das variáveis de ambiente
    api_base_url = os.getenv("ARTERIS_API_BASE_URL")
    api_token = os.getenv("ARTERIS_API_TOKEN")

    # Validação inicial das configurações
    if not api_base_url or not api_token:
        print("Erro: Variáveis de ambiente ARTERIS_API_BASE_URL ou ARTERIS_API_TOKEN não definidas.")
        print("Certifique-se de que o arquivo .env existe na raiz do projeto e contém as variáveis.")
        return

    # --- Processar DocTypes, Fields e Dados ---
    print("\n--- Iniciando Mapeamento de de DocTypes e Fields---")
    all_doctypes, child_parent_mapping, doctypes_with_fields = process_arteris_doctypes(api_base_url, api_token)

    # --- Transformar DocTypes em estrutura hierárquica ---
    print("\n--- Criar estrutura hierarquica ---")
    entity_structure = create_hierarchical_doctype_structure(
        doctypes_with_fields,
        child_parent_mapping
    )
    print(f"Encontrados {len(entity_structure.get('entities', []))} DocTypes no módulo Arteris.")
    print(f"Entididades: \n{entity_structure}")
    # Salvar resultado 
    output_dir = "output"
    output_filename = "output_hierarchical.json"
    try:
        with open(os.path.join(output_dir, output_filename), "w", encoding="utf-8") as f:
            json.dump(entity_structure, f, indent=4, ensure_ascii=False)
        print(f"\n************************")    
        print(f"\nEstrutura hierarquica de entidades salva em {output_filename}")
        print(f"\n************************")    
    except IOError as e:
        print(f"\nErro ao salvar o arquivo {output_filename}: {e}")

    # --- Transformar DocTypes em estrutura de entidades hierarquica ---
    print("\n--- Criar estrutura de entidades hierarquica ---")
    hierarchical_entities = create_hierarchical_doctype_structure(
        doctypes_with_fields,
        child_parent_mapping)
    # Grava o resultado em um arquivo
    output_dir = "output"
    output_hierarchical_filename = "output_hierarchical_entities.json"
    try:
        with open(os.path.join(output_dir, output_hierarchical_filename), "w", encoding="utf-8") as f:
            json.dump(hierarchical_entities, f, indent=4, ensure_ascii=False)
        print(f"\n************************")    
        print(f"\nEstrutura hierárquica de entidades salva em {output_hierarchical_filename}")
        print(f"\n************************")
    except IOError as e:
        print(f"\nErro ao salvar o arquivo {output_hierarchical_filename}: {e}")
    
    # --- Carregar as chaves (name) por DocType ---
    print("\n--- Carregando as chaves (name) dos DocTypes ---")
    doctypes_with_keys = []
    # Percorre a lista de all_doctypes e obtém as chaves usando o método get_keys
    for doctype in all_doctypes:
        doctype_name = doctype.get("name")
        if doctype_name:
            keys = get_keys(api_base_url, api_token, doctype_name)
            doctypes_with_keys.append({"doctype": doctype_name, "keys": keys})
    print("\n--- DocTypes com suas respectivas chaves ---")
    print(json.dumps(doctypes_with_keys, indent=4, ensure_ascii=False))

    # --- Carregar dados dos DocTypes com base nas chaves ---
    print("\n--- Carregando dados dos DocTypes com base nas chaves ---")
    all_doctype_data = []
    for doctype in doctypes_with_keys:
        doctype_name = doctype.get("doctype")
        keys = doctype.get("keys")
        if keys:
            for key in keys:
                data = get_data_from_key(api_base_url, api_token, doctype_name, key)
                if data:
                    all_doctype_data.append({"doctype": doctype_name, "key": key, "data": data})
                else:
                    print(f"Erro ao buscar dados para {doctype_name} com chave {key}.")
        else:
            print(f"Aviso: Nenhuma chave encontrada para o DocType {doctype_name}.")
    # Salva os dados em um arquivo
    output_dir = "output"
    output_data_filename = "output_data.json"
    try:
        with open(os.path.join(output_dir, output_data_filename), "w", encoding="utf-8") as f:
            json.dump(all_doctype_data, f, indent=4, ensure_ascii=False)
        print(f"\n************************")    
        print(f"\nDados salvos em {output_data_filename}")
        print(f"\n************************")
    except IOError as e:
        print(f"\nErro ao salvar o arquivo {output_data_filename}: {e}")

    # --- Transformar dados para o formato engine_entities ---
    print("\n--- Iniciando transformação para formato engine_entities v2---")
    
    engine_data_v2 = transform_to_entity_engine(
        all_doctype_data, 
        hierarchical_entities)
    
    # Grava o resultado em um arquivo
    output_dir = "output"
    output_engine_data_filename = "engine_entities_data_v2.json"
    try:
        with open(os.path.join(output_dir, output_engine_data_filename), "w", encoding="utf-8") as f:
            json.dump(engine_data_v2, f, indent=4, ensure_ascii=False)
        print(f"\n************************")
        print(f"\nDados no formato engine_entities salvos em {output_engine_data_filename}")
        print(f"\n************************")
    except IOError as e:
        print(f"\nErro ao salvar o arquivo {output_engine_data_filename}: {e}")

    # --- Transformar dados para o formato engine_entities ---
    print("\n--- Iniciando transformação para formato engine_entities v3---")
    
    engine_data_v4 = transform_to_entity_engine(
        all_doctype_data, 
        hierarchical_entities)
    
    # Grava o resultado em um arquivo
    output_dir = "output"
    output_engine_data_filename = "engine_entities_data_v4.json"
    try:
        with open(os.path.join(output_dir, output_engine_data_filename), "w", encoding="utf-8") as f:
            json.dump(engine_data_v4, f, indent=4, ensure_ascii=False)
        print(f"\n************************")    
        print(f"\nDados no formato engine_entities salvos em {output_engine_data_filename}")
        print(f"\n************************")
    except IOError as e:
        print(f"\nErro ao salvar o arquivo {output_engine_data_filename}: {e}")        

    
    print(f"\n--- Fim da execução ---")


# Ponto de entrada do script
if __name__ == "__main__":
    main()