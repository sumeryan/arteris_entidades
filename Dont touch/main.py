# """
# Script principal para orquestrar a busca de metadados e dados da API Arteris.

# Este script executa as seguintes etapas:
# 1. Carrega configurações da API do arquivo .env.
# 2. Busca a lista de DocTypes do módulo 'Arteris' usando api_client.
# 3. Para cada DocType, busca seus DocFields usando api_client.
# 4. Transforma os metadados coletados (DocTypes e DocFields) na estrutura
#    de entidades JSON usando transformer.
# 5. Para cada DocType com DocFields, busca os dados reais correspondentes
#    usando api_client.
# 6. Armazena os resultados em dicionários em memória e imprime exemplos.
# """

# import os
# import json
# from dotenv import load_dotenv

# # Importa as funções dos módulos refatorados
# from api_client import get_arteris_doctypes, get_docfields_for_doctype, get_data_for_doctype, get_arteris_doctypes_child
# from transformer import transform_to_entity_structure

# # Carrega variáveis de ambiente do arquivo .env na raiz do projeto
# load_dotenv()

# def main():
#     """
#     Função principal que orquestra as etapas de busca e transformação.
#     """
#     # Obtém a URL base e o token das variáveis de ambiente
#     api_base_url = os.getenv("ARTERIS_API_BASE_URL")
#     api_token = os.getenv("ARTERIS_API_TOKEN")

#     # Validação inicial das configurações
#     if not api_base_url or not api_token:
#         print("Erro: Variáveis de ambiente ARTERIS_API_BASE_URL ou ARTERIS_API_TOKEN não definidas.")
#         print("Certifique-se de que o arquivo .env existe na raiz do projeto e contém as variáveis.")
#         return

#     # --- Etapa 1: Buscar DocTypes ---
#     print("--- Etapa 1: Buscando DocTypes ---")
#     all_doctypes = get_arteris_doctypes(api_base_url, api_token)
#     if all_doctypes is None:
#         print("Não foi possível obter a lista de DocTypes. Encerrando.")
#         return
#     print(f"Encontrados {len(all_doctypes)} DocTypes no módulo Arteris.")

#     print("--- Etapa 1.1: Buscando DocTypes Child ---")
#     all_doctypes_child = get_arteris_doctypes_child(api_base_url, api_token)
#     if all_doctypes_child is None:
#         print("Não foi possível obter a lista de DocTypes. Encerrando.")
#         return
#     print(f"Encontrados {len(all_doctypes_child)} DocTypes no módulo Arteris.")    

#     # --- Etapa 2: Buscar DocFields para cada DocType ---
#     # Combinar as listas all_doctypes_child e all_doctypes
#     combined_doctypes = all_doctypes_child + all_doctypes  # Combina as duas listas

#     doctypes_with_fields = {}
#     for doc in combined_doctypes:
#         doctype_name = doc.get("name")
#         if doctype_name:
#             docfields = get_docfields_for_doctype(api_base_url, api_token, doctype_name)
#             if docfields is not None:
#                 doctypes_with_fields[doctype_name] = docfields
#             else:
#                 doctypes_with_fields[doctype_name] = None  # Marca erro
#         else:
#             print("Aviso: Encontrado DocType sem nome.")
#     print("Busca de DocFields concluída.")

#     # --- Etapa 3: Localizar os "Parents" ---
#     print("\n--- Etapa 4: Localizando os 'Parents' ---")
#     child_parent_mapping = [] # Dicionário para mapear child -> parent

#     # Itera sobre cada DocType que pode ser um "Parent"
#     for doctype_name, fields in doctypes_with_fields.items():
#         if fields is None:
#             print(f"Pulando busca de dados para {doctype_name} devido a erro anterior na busca de campos.")
#             all_doctype_data[doctype_name] = None
#             continue
#         if not fields:
#             print(f"Pulando busca de dados para {doctype_name} pois não foram encontrados campos (DocFields).")
#             all_doctype_data[doctype_name] = []
#             continue

#         # Percorre a lista de dicionários 'fields'
#         for f in fields:
#             # Verifica se o item tem um fieldname e se o fieldtype é "Table"
#             if f.get("fieldname") and f.get("fieldtype") == "Table":
#                 child_parent_mapping.append(
#                     {
#                         "child": f.get("options"),
#                         "parent": doctype_name
#                     }
#                 )    
#     # Criar um dicionário para mapeamento rápido de child para parent
#     child_to_parent = {mapping["child"]: mapping["parent"] for mapping in child_parent_mapping}

#     # --- Etapa 4: Buscar Dados Reais para cada DocType ---
#     print("\n--- Etapa 3: Buscando Dados Reais ---")
#     all_doctype_data = {}
#     for doctype_name, fields in doctypes_with_fields.items():

#         # Verificar se este doctype está em all_doctypes_child
#         is_child_doctype = any(doc.get("name") == doctype_name for doc in all_doctypes_child)

#         if fields is None:
#             print(f"Pulando busca de dados para {doctype_name} devido a erro anterior na busca de campos.")
#             all_doctype_data[doctype_name] = None
#             continue
#         if not fields:
#             print(f"Pulando busca de dados para {doctype_name} pois não foram encontrados campos (DocFields).")
#             all_doctype_data[doctype_name] = []
#             continue

#         # Extrai apenas os 'fieldname' da lista de dicionários 'fields'
#         fieldnames = [f.get("fieldname") for f in fields if f.get("fieldname") and f.get("fieldtype") not in ["Link", "Table"]]
#         if not fieldnames:
#              print(f"Aviso: Nenhum 'fieldname' válido encontrado para {doctype_name}. Buscando apenas 'name'.")

#         print(f"\nBuscando dados para {doctype_name} com os seguintes fieldnames {fieldnames}...")
#         # Se o doctype for um child, busca os dados do parent
#         if is_child_doctype:
#             # Obter o parent diretamente do dicionário (retorna None se não existir)
#             parent_name = child_to_parent.get(doctype_name)
#             print(f"Parent encontrado: {parent_name}")
#             doctype_data = get_data_for_doctype(api_base_url, api_token, doctype_name, fieldnames, parent_name)
#         else:
#             doctype_data = get_data_for_doctype(api_base_url, api_token, doctype_name, fieldnames)

#         if doctype_data is not None:
#             all_doctype_data[doctype_name] = doctype_data
#         else:
#             all_doctype_data[doctype_name] = None # Marca erro         

#     print("\nBusca de dados reais concluída.")

#     # Corrigido - iterando diretamente sobre a lista
#     print("\n--- Exibindo Mapeamento de Childs para Parents ---")
#     for mapping in child_parent_mapping:
#         print(f"Child: {mapping.get('child')}, Parent(s): {mapping.get('parent')}")

#     # --- Exibição de Exemplo dos Dados Coletados ---
#     print("\n--- Exemplo de Dados Coletados (Primeiro registro dos primeiros 3 DocTypes) ---")
#     count = 0
#     for doctype_name, data_list in all_doctype_data.items():
#         if count >= 3:
#             break
#         print(f"\nDocType: {doctype_name}")
#         if data_list is None:
#             print("  Erro ao buscar dados.")
#         elif not data_list:
#             print("  Nenhum registro encontrado.")
#         else:
#             print(f"  Total de registros: {len(data_list)}")
#             if data_list:
#                 print(f"  Primeiro registro: {data_list[0]}")
#             else:
#                 print("  Lista de dados está vazia.")
#         count += 1

#     # # Mensagem final
#     # print(f"\nTotal de {len(all_doctype_data)} DocTypes tiveram seus dados buscados e armazenados em memória.")
#     # if entity_structure and 'entities' in entity_structure:
#     #     print(f"Estrutura de entidades gerada para {len(entity_structure.get('entities', []))} DocTypes.")
#     # else:
#     #     print("Estrutura de entidades não foi gerada devido a erros anteriores.")

# # Ponto de entrada do script
# if __name__ == "__main__":
#     main()