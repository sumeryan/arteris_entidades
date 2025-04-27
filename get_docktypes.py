import api_client # Importa o módulo api_client

def process_arteris_doctypes(api_base_url, api_token): # Renomeia a função

    # Lista para armazenar os DocTypes e seus campos
    doctypes_with_fields = {}

    # --- Etapa 1: Buscar DocTypes ---
    print("--- Etapa 1: Buscando DocTypes ---")
    # Chama a função de api_client
    all_doctypes = api_client.get_arteris_doctypes(api_base_url, api_token)
    if all_doctypes is None:
        print("Não foi possível obter a lista de DocTypes. Encerrando.")
        return None, None, None # Retorna None para indicar falha
    print(f"Encontrados {len(all_doctypes)} DocTypes no módulo Arteris.")

    # --- Etapa 1.1: Buscar DocFields para cada DocType ---
    print("\n--- Etapa 2: Buscando DocFields ---")

    for doc in all_doctypes:
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

    print("--- Etapa 2: Buscando DocTypes Child ---")
    # Chama a função de api_client
    all_doctypes_child = api_client.get_arteris_doctypes_child(api_base_url, api_token)
    if all_doctypes_child is None:
        print("Não foi possível obter a lista de DocTypes Child. Encerrando.")
        return None, None, None # Retorna None para indicar falha
    print(f"Encontrados {len(all_doctypes_child)} DocTypes Child no módulo Arteris.")

    # --- Etapa 2.1: Buscar DocFields para cada DocType Child---
    print("\n--- Etapa 2: Buscando DocFields Child ---")
    for doc in all_doctypes_child:
        doctype_name = doc.get("name")
        if doctype_name:
            # Chama a função de api_client
            docfields = api_client.get_docfields_for_doctype(api_base_url, api_token, doctype_name, True)
            if docfields is not None:
                doctypes_with_fields[doctype_name] = docfields
            else:
                print(f"Erro ao buscar DocFields para {doctype_name}. Marcando como None.")
                doctypes_with_fields[doctype_name] = None # Marca erro
        else:
            print("Aviso: Encontrado DocType sem nome.")
    print("Busca de DocFields Child concluída.")    

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

    # Retorna os resultados
    return all_doctypes, child_parent_mapping, doctypes_with_fields
