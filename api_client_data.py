import requests
import json

def get_keys(api_base_url, api_token, doctype_name):
    """
    Busca as chaves de um DocType específico na API Arteris.
    Args:
        api_base_url (str): A URL base da API de recursos (ex: 'https://host/api/resource').
        api_token (str): O token de autorização no formato 'token key
        doctype_name (str): O nome do DocType do qual buscar as chaves (ex: 'Asset').
    Returns:
        list or None: Uma lista de strings contendo os valores das chaves do DocType.
                      Retorna None em caso de erro na requisição ou na decodificação JSON.
    """
    resource_url = f"{api_base_url}/{doctype_name}"
    params = {}
    headers = {"Authorization": api_token}

    try:
        print(f"Buscando chaves para DocType '{doctype_name}' em: {resource_url}")
        response = requests.get(resource_url, headers=headers, params=params, timeout=30)
        response.raise_for_status() # Lança HTTPError para respostas 4xx/5xx
        data = response.json()
        keys = [item["name"] for item in data.get("data", [])]
        print(f"Chaves para '{doctype_name}' recebidas com sucesso!\n{keys}")
        # Retorna a lista de chaves contida na chave 'data' da resposta JSON
        return keys
    except requests.exceptions.RequestException as e:
        # Captura erros de conexão, timeout, etc.
        print(f"Erro ao buscar chaves para {doctype_name}: {e}")
        return None
    except json.JSONDecodeError:
        # Captura erro se a resposta não for um JSON válido
        print(f"Erro ao decodificar a resposta JSON das chaves para {doctype_name}.")
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
