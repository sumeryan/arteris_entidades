import api_client # Importa o módulo api_client

def process_arteris_doctypes(api_base_url, api_token): # Renomeia a função

    # --- Etapa 1: Buscar DocTypes ---
    print("--- Etapa 1: Buscando DocTypes ---")
    # Chama a função de api_client
    all_doctypes = api_client.get_arteris_doctypes(api_base_url, api_token)
    if all_doctypes is None:
        print("Não foi possível obter a lista de DocTypes. Encerrando.")
        return None, None, None # Retorna None para indicar falha
    print(f"Encontrados {len(all_doctypes)} DocTypes no módulo Arteris.")

    print("--- Etapa 1.1: Buscando DocTypes Child ---")
    # Chama a função de api_client
    all_doctypes_child = api_client.get_arteris_doctypes_child(api_base_url, api_token)
    if all_doctypes_child is None:
        print("Não foi possível obter a lista de DocTypes Child. Encerrando.")
        return None, None, None # Retorna None para indicar falha
    print(f"Encontrados {len(all_doctypes_child)} DocTypes Child no módulo Arteris.")

    # --- Etapa 2: Buscar DocFields para cada DocType ---
    print("\n--- Etapa 2: Buscando DocFields ---")
    combined_doctypes = all_doctypes + all_doctypes_child # Combina as duas listas
    doctypes_with_fields = {}
    for doc in combined_doctypes:
        doctype_name = doc.get("name")
        if doctype_name:
            # Chama a função de api_client
            docfields = api_client.get_docfields_for_doctype(api_base_url, api_token, doctype_name)
            if docfields is not None:
                doctypes_with_fields[doctype_name] = docfields
            else:
                print(f"Erro ao buscar DocFields para {doctype_name}. Marcando como None.")
                doctypes_with_fields[doctype_name] = None # Marca erro
        else:
            print("Aviso: Encontrado DocType sem nome.")
    print("Busca de DocFields concluída.")

    # --- Etapa 3: Localizar os "Parents" ---
    print("\n--- Etapa 3: Localizando os 'Parents' ---")
    child_parent_mapping = [] # Lista para mapear child -> parent

    # Itera sobre cada DocType que pode ser um "Parent"
    for doctype_name, fields in doctypes_with_fields.items():
        if fields is None:
            # Não precisa imprimir aqui, já foi impresso no erro anterior
            continue
        if not fields:
            # Não é um erro, apenas não tem campos de tabela
            continue

        # Percorre a lista de dicionários 'fields'
        for f in fields:
            # Verifica se o item tem um fieldname e se o fieldtype é "Table"
            if f.get("fieldname") and f.get("fieldtype") == "Table" and f.get("options"):
                child_parent_mapping.append(
                    {
                        "child": f.get("options"),
                        "parent": doctype_name
                    }
                )
    print("Mapeamento Child-Parent concluído.")
    # Criar um dicionário para mapeamento rápido de child para parent
    child_to_parent = {mapping["child"]: mapping["parent"] for mapping in child_parent_mapping}
    print(f"Mapeamento Child -> Parent: {child_to_parent}") # Log para depuração

    # --- Etapa 4: Buscar Dados Reais para cada DocType ---
    print("\n--- Etapa 4: Buscando Dados Reais ---")
    all_doctype_data = {}
    for doctype_name, fields in doctypes_with_fields.items():

        # Verificar se este doctype está em all_doctypes_child
        is_child_doctype = any(doc.get("name") == doctype_name for doc in all_doctypes_child)

        if fields is None:
            print(f"Pulando busca de dados para {doctype_name} devido a erro anterior na busca de campos.")
            all_doctype_data[doctype_name] = None
            continue
        # Não pular se não tiver fields, pode ser um DocType sem campos mas com dados (pelo menos 'name')
        # if not fields:
        #     print(f"Pulando busca de dados para {doctype_name} pois não foram encontrados campos (DocFields).")
        #     all_doctype_data[doctype_name] = []
        #     continue

        # Extrai apenas os 'fieldname' da lista de dicionários 'fields' que não são Link ou Table
        # Inclui 'name' por padrão, pois é a chave primária
        fieldnames = ["name"] + [
            f.get("fieldname") for f in fields
            if f.get("fieldname") and f.get("fieldtype") not in ["Link", "Table", "Read Only", "HTML", "Button", "Image"] # Adiciona mais tipos a ignorar se necessário
        ]
        # Remove duplicatas caso 'name' já esteja na lista de fields
        fieldnames = list(dict.fromkeys(fieldnames))

        if not fieldnames or len(fieldnames) == 1 and fieldnames[0] == 'name':
             print(f"Aviso: Nenhum 'fieldname' adicional válido encontrado para {doctype_name}. Buscando apenas 'name'.")
             fieldnames = ["name"] # Garante que pelo menos 'name' seja buscado

        print(f"\nBuscando dados para {doctype_name} com os seguintes fieldnames {fieldnames}...")
        parent_name_to_pass = None # Inicializa como None
        if is_child_doctype:
            # Obter o parent diretamente do dicionário
            parent_name_to_pass = child_to_parent.get(doctype_name)
            if parent_name_to_pass:
                 print(f"É um Child DocType. Parent encontrado no mapeamento: {parent_name_to_pass}")
            else:
                 print(f"Aviso: {doctype_name} é um Child DocType, mas seu Parent não foi encontrado no mapeamento. Tentando buscar diretamente.")

        # Chama a função de api_client
        doctype_data = api_client.get_data_for_doctype(api_base_url, api_token, doctype_name, fieldnames, parent_name_to_pass) # Removido parent_name_to_pass por enquanto

        if doctype_data is not None:
            all_doctype_data[doctype_name] = doctype_data
            print(f"Dados para {doctype_name} obtidos. Quantidade: {len(doctype_data)}")
        else:
            all_doctype_data[doctype_name] = None # Marca erro
            print(f"Erro ao buscar dados para {doctype_name}.")

    print("\nBusca de dados reais concluída.")

    # --- Exibição de Mapeamento ---
    print("\n--- Mapeamento de Childs para Parents ---")
    if child_parent_mapping:
        for mapping in child_parent_mapping:
            print(f"Child: {mapping.get('child')}, Parent: {mapping.get('parent')}")
    else:
        print("Nenhum mapeamento Child-Parent encontrado.")

    # --- Retorno dos Dados ---
    # Retorna os dados coletados e o mapeamento
    return doctypes_with_fields, all_doctype_data, child_parent_mapping

# Código de teste (opcional, pode ser removido ou comentado)
# if __name__ == '__main__':
#     # Substitua pelos seus valores reais de URL e Token
#     API_BASE_URL = "YOUR_API_BASE_URL/api/resource"
#     API_TOKEN = "token YOUR_API_KEY:YOUR_API_SECRET"
#
#     print("Iniciando o processo de busca de DocTypes e dados...")
#     fields_data, real_data, mapping = process_arteris_doctypes(API_BASE_URL, API_TOKEN)
#
#     if fields_data is not None and real_data is not None:
#         print("\n--- Processo Concluído ---")
#
#         # Exemplo de como acessar os dados (opcional)
#         print("\n--- Exemplo de Dados Coletados (Primeiro registro dos primeiros 3 DocTypes com dados) ---")
#         count = 0
#         for doctype_name, data_list in real_data.items():
#             if data_list and count < 3: # Mostra apenas se a lista não for None e não estiver vazia
#                 print(f"\nDocType: {doctype_name}")
#                 print(f"  Total de registros: {len(data_list)}")
#                 print(f"  Primeiro registro: {data_list[0]}")
#                 count += 1
#             elif data_list is None and count < 3:
#                  print(f"\nDocType: {doctype_name}")
#                  print("  Erro ao buscar dados.")
#                  # count += 1 # Não incrementa se for erro, para tentar mostrar 3 com dados
#             elif not data_list and count < 3:
#                  print(f"\nDocType: {doctype_name}")
#                  print("  Nenhum registro encontrado.")
#                  # count += 1 # Não incrementa se estiver vazio, para tentar mostrar 3 com dados
#
#         if count == 0:
#             print("\nNenhum dado encontrado ou houve erro em todos os DocTypes processados.")
#
#     else:
#         print("\n--- Processo Falhou ---")
#         print("Verifique os logs de erro acima.")
