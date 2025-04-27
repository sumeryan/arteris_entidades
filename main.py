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

# Importa as funções dos módulos refatorados
#from transformer import transform_to_entity_structure
from get_docktypes import process_arteris_doctypes 
from api_client_data import get_keys, get_data_from_key
from json_to_entity_transformer import transform_entity_structure

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

    # --- Etapa 1: Processar DocTypes, Fields e Dados ---
    print("--- Iniciando processamento de DocTypes e Fields---")
    # Chama a função refatorada que encapsula a lógica de busca
    all_doctypes, child_parent_mapping, doctypes_with_fields = process_arteris_doctypes(api_base_url, api_token)

    print("\n--- Processamento de busca concluído ---")

    # --- Etapa 1: Processar DocTypes, Fields e Dados ---
    print("--- Iniciando processamento de Dados ---")

    # Lista para armazenar os DocTypes com suas respectivas chaves
    doctypes_with_keys = []

    # Percorre a lista de all_doctypes e obtém as chaves usando o método get_keys
    for doctype in all_doctypes:
        doctype_name = doctype.get("name")
        if doctype_name:
            keys = get_keys(api_base_url, api_token, doctype_name)
            doctypes_with_keys.append({"doctype": doctype_name, "keys": keys})

    #Transforma DocTypes em entidades
    print("--- Iniciando processamento de Entidades ---")

    # Transformar os metadados em estrutura de entidades
    # Usando a nova função e os novos dados de exemplo
    entity_structure = transform_entity_structure(
        doctypes_with_fields,
        child_parent_mapping
    )

    print(f"Encontrados {len(entity_structure.get('entities', []))} DocTypes no módulo Arteris.")
    print(f"Entididades: {entity_structure}")

    # Salvar resultado em um arquivo com novo nome
    output_filename = "output_entity_structure_from_metadata.json"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(entity_structure, f, indent=4, ensure_ascii=False)
        print(f"\nEstrutura de entidades salva em {output_filename}")
    except IOError as e:
        print(f"\nErro ao salvar o arquivo {output_filename}: {e}")

    print("\n--- DocTypes com suas respectivas chaves ---")
    print(json.dumps(doctypes_with_keys, indent=4, ensure_ascii=False))

    # Para cada DocType, busca os dados usando o método get_data_from_key
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

    print(f"\n--- Fim da execução ---")

    # Mensagem final opcional
    print(f"\nTotal de {len(all_doctype_data)} DocTypes tiveram seus dados buscados.")
    # if 'entity_structure' in locals() and entity_structure:
    #      print(f"Estrutura de entidades gerada para {len(entity_structure.get('entities', []))} DocTypes.")

# Ponto de entrada do script
if __name__ == "__main__":
    main()