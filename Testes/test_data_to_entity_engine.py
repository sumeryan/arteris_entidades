#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste para o módulo data_to_entity_engine.py.

Este script carrega os dados de output_data.json e a estrutura hierárquica de
output_hierarchical.json, chama a função transform_to_entity_engine
para transformar os dados e salva o resultado em entity_engine_resultado.json.
"""

import json
import os
import logging
import sys

# Adicionar o diretório raiz ao path para importar o módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_to_engine_entities_v4 import transform_to_entity_engine

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_transform_to_entity_engine():
    """
    Função de teste para o módulo data_to_entity_engine.py.
    """
    # Definir caminhos dos arquivos
    data_file = os.path.join("output", "output_data.json")
    hierarchical_file = os.path.join("output", "output_hierarchical.json")
    output_file = os.path.join("output", "entity_engine_resultado.json")
    
    # Verificar se os arquivos de entrada existem
    if not os.path.exists(data_file):
        logger.error(f"Arquivo de dados não encontrado: {data_file}")
        return
    
    if not os.path.exists(hierarchical_file):
        logger.error(f"Arquivo de estrutura hierárquica não encontrado: {hierarchical_file}")
        return
    
    try:
        # Carregar dados
        logger.info(f"Carregando dados de {data_file}")
        with open(data_file, 'r', encoding='utf-8') as f:
            output_data = json.load(f)
        
        # Carregar estrutura hierárquica
        logger.info(f"Carregando estrutura hierárquica de {hierarchical_file}")
        with open(hierarchical_file, 'r', encoding='utf-8') as f:
            output_hierarchical = json.load(f)
        
        # Transformar dados para o formato entity_engine
        logger.info("Transformando dados para o formato entity_engine")
        entity_engine_result = transform_to_entity_engine(output_data, output_hierarchical)
        
        # Salvar resultado
        logger.info(f"Salvando resultado em {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(entity_engine_result, f, indent=4, ensure_ascii=False)
        
        # Exibir estatísticas
        logger.info(f"Transformação concluída com sucesso")
        logger.info(f"Total de entidades de entrada: {len(output_data)}")
        logger.info(f"Total de entidades de saída: {len(entity_engine_result.get('entities', []))}")
        
        # Exibir exemplo da primeira entidade (se existir)
        if entity_engine_result.get('entities'):
            logger.info("Exemplo da primeira entidade transformada:")
            logger.info(json.dumps(entity_engine_result['entities'][0], indent=2, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
        raise

if __name__ == "__main__":
    test_transform_to_entity_engine()