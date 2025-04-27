# Plano para Ajustar o Método get_data_from_key

## Contexto Atual

Após analisar o código, identifiquei que:

1. O método `get_data_from_key` está localizado no arquivo `api_client_data.py`.
2. Este método é responsável por buscar dados de um DocType específico na API Arteris usando uma chave.
3. Atualmente, o método retorna todos os dados contidos na chave "data" da resposta JSON, sem filtrar nenhuma propriedade.
4. O método é utilizado no arquivo `main.py` para buscar dados para cada DocType e suas respectivas chaves.

## Propriedades a Serem Removidas

As propriedades que precisam ser removidas do JSON retornado são:
- 'owner'
- 'creation'
- 'modified'
- 'modified_by'
- 'docstatus'
- 'idx'

## Plano de Implementação

### 1. Modificação do Método `get_data_from_key`

Modificar o método `get_data_from_key` no arquivo `api_client_data.py` para:

1. Receber os dados da API como já faz atualmente
2. Antes de retornar os dados, remover as propriedades especificadas
3. Retornar os dados filtrados

A modificação será feita da seguinte forma:

```python
def get_data_from_key(api_base_url, api_token, doctype_name, key):
    """
    Busca os dados de um DocType específico na API Arteris usando uma chave.
    Args:
        api_base_url (str): A URL base da API de recursos (ex: 'https://host/api/resource').
        api_token (str): O token de autorização no formato 'token key
        doctype_name (str): O nome do DocType do qual buscar os dados (ex: 'Asset').
        key (str): A chave do DocType para buscar os dados.
    Returns:
        Um JSON contendo os dados do DocType ou None em caso de erro.
        As seguintes propriedades são removidas do JSON retornado:
        'owner', 'creation', 'modified', 'modified_by', 'docstatus', 'idx'
    """
    resource_url = f"{api_base_url}/{doctype_name}/{key}"
    params = {}
    headers = {"Authorization": api_token}

    try:
        print(f"Buscando dados para DocType '{doctype_name}' usando a chave '{key}' em: {resource_url}")
        response = requests.get(resource_url, headers=headers, params=params, timeout=30)
        response.raise_for_status() # Lança HTTPError para respostas 4xx/5xx
        data = response.json()
        # Verifica se a resposta contém dados
        if "data" in data:
            print(f"Dados para '{doctype_name}' com chave '{key}' recebidos com sucesso!")
            
            # Remove as propriedades especificadas
            data_filtered = data["data"]
            properties_to_remove = ['owner', 'creation', 'modified', 'modified_by', 'docstatus', 'idx']
            
            for prop in properties_to_remove:
                if prop in data_filtered:
                    del data_filtered[prop]
            
            return data_filtered
        else:
            print(f"Nenhum dado encontrado para '{doctype_name}' com chave '{key}'.")
            return None
    except requests.exceptions.RequestException as e:
        # Captura erros de conexão, timeout, etc.
        print(f"Erro ao buscar chaves para {doctype_name}: {e}")
        return None
    except json.JSONDecodeError:
        # Captura erro se a resposta não for um JSON válido
        print(f"Erro ao decodificar a resposta JSON das chaves para {doctype_name}.")
        return None
```

### 2. Verificação de Impacto

A modificação proposta não deve afetar o funcionamento de outras partes do código, pois:

1. A estrutura geral do método permanece a mesma
2. O tipo de retorno continua sendo um dicionário JSON ou None
3. Apenas algumas propriedades específicas são removidas do JSON retornado
4. O código que utiliza este método (como visto em `main.py`) não parece depender especificamente dessas propriedades

### 3. Testes Recomendados

Após implementar a modificação, recomendo testar:

1. Executar o script principal (`main.py`) para verificar se a aplicação continua funcionando corretamente
2. Verificar se as propriedades especificadas foram realmente removidas do JSON retornado
3. Verificar se não há efeitos colaterais em outras partes do código que possam depender dessas propriedades

## Diagrama da Solução

```mermaid
flowchart TD
    A[API Request] --> B[Receber dados da API]
    B --> C{Dados recebidos?}
    C -->|Sim| D[Filtrar propriedades]
    C -->|Não| E[Retornar None]
    D --> F[Retornar dados filtrados]
    
    subgraph "Filtrar propriedades"
    D1[Remover 'owner'] --> D2[Remover 'creation']
    D2 --> D3[Remover 'modified']
    D3 --> D4[Remover 'modified_by']
    D4 --> D5[Remover 'docstatus']
    D5 --> D6[Remover 'idx']
    end