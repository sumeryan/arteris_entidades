# exemplo_uso_entity_engine.py
import json
from data_to_engine_entities_v4 import transform_to_entity_engine

# Exemplo de como usar o módulo data_to_entity_engine.py

def carregar_dados_exemplo():
    """
    Carrega dados de exemplo dos arquivos para demonstração.
    Em um caso real, você receberia esses dados diretamente como parâmetros.
    """
    try:
        # Carregar dados de exemplo
        with open('output/output_data.json', 'r', encoding='utf-8') as f:
            output_data = json.load(f)
        
        with open('output/output_hierarchical.json', 'r', encoding='utf-8') as f:
            output_hierarchical = json.load(f)
        
        return output_data, output_hierarchical
    except Exception as e:
        print(f"Erro ao carregar dados de exemplo: {e}")
        return None, None

def exemplo_transformacao():
    """
    Demonstra como usar a função transform_to_entity_engine.
    """
    # Em um caso real, você receberia esses dados diretamente, sem carregar de arquivos
    output_data, output_hierarchical = carregar_dados_exemplo()
    
    if not output_data or not output_hierarchical:
        print("Não foi possível carregar os dados de exemplo.")
        return
    
    # Chamar a função de transformação
    resultado = transform_to_entity_engine(output_data, output_hierarchical)
    
    # Exibir algumas estatísticas do resultado
    num_entidades = len(resultado.get('entities', []))
    print(f"Transformação concluída. {num_entidades} entidades geradas.")
    
    # Opcional: Salvar o resultado em um arquivo
    with open('output/entity_engine_resultado.json', 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=4, ensure_ascii=False)
    print(f"Resultado salvo em 'output/entity_engine_resultado.json'")

if __name__ == "__main__":
    print("Iniciando exemplo de uso do módulo data_to_entity_engine.py")
    exemplo_transformacao()