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
from transformer import transform_to_entity_structure
from get_docktypes import process_arteris_doctypes # Importa a função refatorada

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
    print("--- Iniciando processamento de DocTypes, Fields e Dados ---")
    # Chama a função refatorada que encapsula a lógica de busca
    doctypes_with_fields, all_doctype_data, child_parent_mapping = process_arteris_doctypes(api_base_url, api_token)

    # Verifica se o processamento foi bem-sucedido
    if doctypes_with_fields is None or all_doctype_data is None or child_parent_mapping is None:
        print("Erro durante o processamento de DocTypes/Fields/Dados. Encerrando.")
        return

    print("\n--- Processamento de busca concluído ---")

    # --- Etapa 2: Transformar Metadados (Opcional, dependendo do objetivo) ---
    # Se a transformação ainda for necessária:
    print("\n--- Etapa 2: Transformando Metadados ---")
    entity_structure = transform_to_entity_structure(doctypes_with_fields)
    if entity_structure:
        print("Estrutura de entidades gerada com sucesso.")
        # Opcional: Salvar a estrutura em um arquivo JSON
        # try:
        #     with open("arteris_entity_structure.json", "w", encoding="utf-8") as f:
        #         json.dump(entity_structure, f, indent=4, ensure_ascii=False)
        #     print("Estrutura de entidades salva em arteris_entity_structure.json")
        # except IOError as e:
        #     print(f"Erro ao salvar a estrutura de entidades: {e}")
    else:
        print("Não foi possível gerar a estrutura de entidades.")

    # --- Etapa 3: Exibir Resultados ---
    # Exibe o mapeamento Child-Parent (já é feito dentro de process_arteris_doctypes, mas pode exibir aqui se preferir)
    print("\n--- Mapeamento de Childs para Parents ---")
    if child_parent_mapping:
        for mapping in child_parent_mapping:
            print(f"Child: {mapping.get('child')}, Parent: {mapping.get('parent')}")
    else:
        print("Nenhum mapeamento Child-Parent encontrado.")

    # Exibe exemplo dos dados coletados
    print("\n--- Exemplo de Dados Coletados (Primeiro registro dos primeiros 3 DocTypes com dados) ---")
    count = 0
    count = 0
    if all_doctype_data: # Verifica se o dicionário não está vazio
        for doctype_name, data_list in all_doctype_data.items():
            if count >= 3:
                break
            print(f"\nDocType: {doctype_name}")
            if data_list is None:
                print("  Erro ao buscar dados.")
            elif not data_list: # Verifica se a lista está vazia
                print("  Nenhum registro encontrado.")
            else:
                print(f"  Total de registros: {len(data_list)}")
                print(f"  Primeiro registro: {data_list[0]}") # Acessa o primeiro item diretamente
                count += 1 # Incrementa apenas se mostrou dados válidos
    else:
        print("Nenhum dado foi coletado ou houve erro em todas as buscas.")

    # --- Etapa 3: Montagem das entidades ---
    entity_structure = transform_to_entity_structure(doctypes_with_fields)
    if entity_structure:
        print("\nEstrutura de entidades gerada com sucesso.")
        # Opcional: Salvar a estrutura em um arquivo JSON
        try:
            #check if the file already exists
            if os.path.exists("arteris_entity_structure.json"):
                print("O arquivo arteris_entity_structure.json já existe. Deseja sobrescrever? (s/n)")
                choice = input().strip().lower()
                if choice == 's':
                    #excluir o arquivo
                    os.remove("arteris_entity_structure.json")

            with open("arteris_entity_structure.json", "w", encoding="utf-8") as f:
                json.dump(entity_structure, f, indent=4, ensure_ascii=False)

            print("Estrutura de entidades salva em arteris_entity_structure.json")

        except IOError as e:
            print(f"Erro ao salvar a estrutura de entidades: {e}")
    else:
        print("Não foi possível gerar a estrutura de entidades.")

    print(f"\n--- Fim da execução ---")
    # Mensagem final opcional
    print(f"\nTotal de {len(all_doctype_data)} DocTypes tiveram seus dados buscados.")
    # if 'entity_structure' in locals() and entity_structure:
    #      print(f"Estrutura de entidades gerada para {len(entity_structure.get('entities', []))} DocTypes.")

# Ponto de entrada do script
if __name__ == "__main__":
    main()