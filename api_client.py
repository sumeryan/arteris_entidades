import requests
import json
def get_arteris_doctypes(api_base_url, api_token):
    """
    Busca todos os DocTypes da API Arteris que pertencem ao módulo 'Arteris' e não são do tipo Child Item .

    Args:
        api_base_url (str): A URL base da API de recursos (ex: 'https://host/api/resource').
        api_token (str): O token de autorização no formato 'token key:secret'.

    Returns:
        list or None: Uma lista de dicionários, onde cada dicionário representa um DocType
                      encontrado (contendo pelo menos a chave 'name').
                      Retorna None em caso de erro na requisição ou na decodificação JSON.
    """
    doctype_url = f"{api_base_url}/DocType"
    params = {
        # Filtra para buscar apenas DocTypes do módulo específico 'Arteris' e que não são tabelas (Child Item)
        "filters": json.dumps([["module", "=", "Arteris"],["istable","!=","1"]])
        # Poderia adicionar 'fields' se precisasse de mais informações do DocType aqui
    }
    headers = {"Authorization": api_token}

    try:
        print(f"Buscando DocTypes em: {doctype_url}")
        response = requests.get(doctype_url, headers=headers, params=params, timeout=30)
        response.raise_for_status() # Lança HTTPError para respostas 4xx/5xx
        data = response.json()
        print("Lista de DocTypes recebida com sucesso!")
        # Retorna diretamente a lista contida na chave 'data' da resposta JSON
        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        # Captura erros de conexão, timeout, etc.
        print(f"Erro ao buscar DocTypes da API: {e}")
        return None
    except json.JSONDecodeError:
        # Captura erro se a resposta não for um JSON válido
        print("Erro ao decodificar a resposta JSON dos DocTypes.")
        return None
    
def get_arteris_doctypes_child(api_base_url, api_token):
    """
    Busca todos os DocTypes da API Arteris que pertencem ao módulo 'Arteris' do tipo Child Item .

    Args:
        api_base_url (str): A URL base da API de recursos (ex: 'https://host/api/resource').
        api_token (str): O token de autorização no formato 'token key:secret'.

    Returns:
        list or None: Uma lista de dicionários, onde cada dicionário representa um DocType
                      encontrado (contendo pelo menos a chave 'name').
                      Retorna None em caso de erro na requisição ou na decodificação JSON.
    """
    doctype_url = f"{api_base_url}/DocType"
    params = {
        # Filtra para buscar apenas DocTypes do módulo específico 'Arteris' e que não são tabelas (Child Item)
        "filters": json.dumps([["module", "=", "Arteris"],["istable","=","1"]])
        # Poderia adicionar 'fields' se precisasse de mais informações do DocType aqui
    }
    headers = {"Authorization": api_token}

    try:
        print(f"Buscando DocTypes em: {doctype_url}")
        response = requests.get(doctype_url, headers=headers, params=params, timeout=30)
        response.raise_for_status() # Lança HTTPError para respostas 4xx/5xx
        data = response.json()
        print("Lista de DocTypes recebida com sucesso!")
        # Retorna diretamente a lista contida na chave 'data' da resposta JSON
        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        # Captura erros de conexão, timeout, etc.
        print(f"Erro ao buscar DocTypes da API: {e}")
        return None
    except json.JSONDecodeError:
        # Captura erro se a resposta não for um JSON válido
        print("Erro ao decodificar a resposta JSON dos DocTypes.")
        return None    

def get_docfields_for_doctype(api_base_url, api_token, doctype_name):
    """
    Busca os DocFields (metadados dos campos) para um DocType específico.

    Filtra para excluir campos do tipo 'Section Break' e 'Column Break' e
    seleciona apenas 'fieldname', 'label' e 'fieldtype'.

    Args:
        api_base_url (str): A URL base da API de recursos.
        api_token (str): O token de autorização.
        doctype_name (str): O nome do DocType para o qual buscar os campos.

    Returns:
        list or None: Uma lista de dicionários, onde cada dicionário representa um DocField
                      (contendo 'fieldname', 'label', 'fieldtype').
                      Retorna None em caso de erro na requisição ou na decodificação JSON.
                      Retorna uma lista vazia se nenhum campo for encontrado após os filtros.
    """
    docfield_url = f"{api_base_url}/DocField"
    params = {
        # Define quais campos do DocField queremos retornar
        "fields": json.dumps(["fieldname", "label", "fieldtype", "options"]),
        # Define os filtros:
        "filters": json.dumps([
            ["parent", "=", doctype_name],          # Campo pertence ao DocType pai especificado
            ["fieldtype", "!=", "Section Break"], # Exclui quebras de seção
            ["fieldtype", "!=", "Column Break"],  # Exclui quebras de coluna
            ["fieldtype", "!=", "Tab Break"],   # Exclui quebras de aba
        ]),
        # Parâmetro 'parent' parece ser necessário pela API DocField,
        # mesmo já filtrando por 'parent' em 'filters'.
        "parent": "DocType"
    }
    headers = {"Authorization": api_token}

    try:
        print(f"Buscando DocFields para: {doctype_name}")
        response = requests.get(docfield_url, headers=headers, params=params, timeout=30)
        response.raise_for_status() # Lança HTTPError para respostas 4xx/5xx
        data = response.json()
        print(f"DocFields para {doctype_name} recebidos com sucesso!")
        # Retorna a lista de campos da chave 'data'
        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        # Captura erros de conexão, timeout, etc.
        print(f"Erro ao buscar DocFields para {doctype_name}: {e}")
        return None
    except json.JSONDecodeError:
        # Captura erro se a resposta não for um JSON válido
        print(f"Erro ao decodificar a resposta JSON dos DocFields para {doctype_name}.")
        return None

def get_data_for_doctype(api_base_url, api_token, doctype_name, fieldnames, parent_name=None):
    """
    Busca dados para um DocType específico, selecionando os campos desejados.
    Permite filtrar por um DocType pai, se aplicável (para Child Doctypes).

    Args:
        api_base_url (str): A URL base da API de recursos (ex: 'https://host/api/resource').
        api_token (str): O token de autorização no formato 'token key:secret'.
        doctype_name (str): O nome do DocType do qual buscar os dados (ex: 'Asset').
        fieldnames (list): Uma lista de strings contendo os nomes dos campos a serem retornados.
        parent_name (str, optional): O nome do registro pai para filtrar os dados (usado para Child Doctypes).
                                     Defaults to None.

    Returns:
        list or None: Uma lista de dicionários, onde cada dicionário representa um registro
                      do DocType com os campos solicitados.
                      Retorna None em caso de erro na requisição ou na decodificação JSON.
                      Retorna uma lista vazia se nenhum dado for encontrado.
    """
    resource_url = f"{api_base_url}/{doctype_name}"
    params = {
        # Converte a lista de fieldnames para uma string JSON para o parâmetro 'fields'
        "fields": json.dumps(fieldnames)
        # Poderíamos adicionar 'filters' aqui se necessário no futuro
        # "filters": json.dumps([["campo", "operador", "valor"]])
        # Poderíamos adicionar 'limit_page_length' se precisássemos de paginação
        # "limit_page_length": 1000 # Ou outro valor, ou None para o padrão da API
    }
    # Adiciona o filtro de parent se fornecido
    if parent_name:
        params["parent"] = parent_name
        print(f"Filtrando por parent: {parent_name}")

    headers = {"Authorization": api_token}

    try:
        print(f"Buscando dados para DocType '{doctype_name}' em: {resource_url}")
        print(f"Campos solicitados: {fieldnames}")
        # Define um timeout maior, pois a busca de dados pode demorar mais
        response = requests.get(resource_url, headers=headers, params=params, timeout=60)
        response.raise_for_status() # Lança HTTPError para respostas 4xx/5xx
        data = response.json()
        print(f"Dados para '{doctype_name}' recebidos com sucesso!")
        # Retorna a lista de dados contida na chave 'data' da resposta JSON
        return data.get("data", [])
    except requests.exceptions.Timeout:
        print(f"Erro: Timeout ao buscar dados para {doctype_name}.")
        return None
    except requests.exceptions.RequestException as e:
        # Captura outros erros de conexão, status HTTP, etc.
        print(f"Erro ao buscar dados para {doctype_name}: {e}")
        # Imprime a resposta se houver erro para depuração
        if hasattr(e, 'response') and e.response is not None:
            print(f"Resposta da API (Status {e.response.status_code}): {e.response.text}")
        return None
    except json.JSONDecodeError:
        # Captura erro se a resposta não for um JSON válido
        print(f"Erro ao decodificar a resposta JSON dos dados para {doctype_name}.")
        # Imprime a resposta bruta para depuração
        if 'response' in locals() and response is not None:
             print(f"Resposta bruta da API: {response.text}")
        return None
