#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste para o módulo data_to_engine_entities.py.

Este script carrega os dados de output_data.json e a estrutura de entidades de
output_entity_structure_from_metadata.json, chama a função transform_data_to_engine_entities
para transformar os dados e salva o resultado em engine_entities_output.json.
"""

import json
import os
import logging
from data_to_engine_entities import (
    load_data,
    load_entity_structure,
    transform_data_to_engine_entities,
    save_engine_entities
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_transform_data_to_engine_entities():
    """
    Função de teste para o módulo data_to_engine_entities.py.
    """
    # Definir caminhos dos arquivos
    data_file = "output_data.json"
    entity_structure_file = "output_entity_structure_from_metadata.json"
    output_file = "engine_entities_output.json"
    
    # Verificar se os arquivos de entrada existem
    if not os.path.exists(data_file):
        logger.error(f"Arquivo de dados não encontrado: {data_file}")
        return
    
    if not os.path.exists(entity_structure_file):
        logger.error(f"Arquivo de estrutura de entidades não encontrado: {entity_structure_file}")
        return
    
    try:
        # Carregar dados
        logger.info(f"Carregando dados de {data_file}")
        data = load_data(data_file)
        
        # Carregar estrutura de entidades
        logger.info(f"Carregando estrutura de entidades de {entity_structure_file}")
        entity_structure = load_entity_structure(entity_structure_file)
        
        # Transformar dados para o formato engine_entities
        logger.info("Transformando dados para o formato engine_entities")
        engine_entities = transform_data_to_engine_entities(data, entity_structure)
        
        # Salvar resultado
        logger.info(f"Salvando resultado em {output_file}")
        save_engine_entities(engine_entities, output_file)
        
        # Exibir estatísticas
        logger.info(f"Transformação concluída com sucesso")
        logger.info(f"Total de entidades de entrada: {len(data)}")
        logger.info(f"Total de entidades de saída: {len(engine_entities.get('entities', []))}")
        
        # Exibir exemplo da primeira entidade (se existir)
        if engine_entities.get('entities'):
            logger.info("Exemplo da primeira entidade transformada:")
            logger.info(json.dumps(engine_entities['entities'][0], indent=2, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
        raise

if __name__ == "__main__":
    test_transform_data_to_engine_entities()