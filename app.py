import os
import json
import io
import sys
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
# import eventlet # REMOVIDO: Não usaremos eventlet por enquanto

# Garante que o eventlet seja usado
# eventlet.monkey_patch() # REMOVIDO: Monkey-patching pode causar o RecursionError

# Importa as funções dos módulos existentes
from get_docktypes import process_arteris_doctypes
from api_client_data import get_keys, get_data_from_key
from json_to_entity_transformer import transform_entity_structure

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'uma-chave-secreta-padrao') # Use uma chave secreta segura
# Mudando async_mode para 'threading' para evitar a necessidade de eventlet/gevent
socketio = SocketIO(app, async_mode='threading')

# Variável global para armazenar o JSON gerado
generated_json_data = None

# --- Captura de Logs ---
class SocketIOHandler:
    """Um manipulador para redirecionar prints para o Socket.IO."""
    def write(self, message):
        # Emite a mensagem apenas se não for uma string vazia ou apenas espaços/newlines
        if message.strip():
            socketio.emit('log_message', {'data': message.strip()})

    def flush(self):
        # Necessário pela interface de stream, mas não faz nada aqui
        pass

# Redireciona stdout para o nosso handler
original_stdout = sys.stdout
sys.stdout = SocketIOHandler()

# --- Rotas Flask ---
@app.route('/')
def index():
    """Renderiza a página inicial."""
    return render_template('index.html')

@app.route('/get_generated_json')
def get_generated_json():
    """Retorna o JSON gerado mais recentemente."""
    global generated_json_data
    if generated_json_data:
        # Retorna o JSON como uma resposta JSON para ser processado pelo JS
        return jsonify(generated_json_data)
    else:
        return jsonify({"error": "Nenhum JSON foi gerado ainda."}), 404

# --- Eventos Socket.IO ---
@socketio.on('connect')
def handle_connect():
    """Lida com novas conexões de clientes."""
    print("Cliente conectado") # Isso será enviado via Socket.IO
    emit('log_message', {'data': 'Conectado ao servidor.'})

@socketio.on('disconnect')
def handle_disconnect():
    """Lida com desconexões de clientes."""
    print("Cliente desconectado") # Isso também será enviado via Socket.IO

@socketio.on('start_generation')
def handle_start_generation(message):
    """Inicia o processo de geração de entidades."""
    global generated_json_data
    generated_json_data = None # Limpa o JSON anterior
    emit('generation_started')
    print("--- Iniciando Geração de Entidades ---") # Log inicial

    try:
        # Obtém a URL base e o token das variáveis de ambiente
        api_base_url = os.getenv("ARTERIS_API_BASE_URL")
        api_token = os.getenv("ARTERIS_API_TOKEN")

        if not api_base_url or not api_token:
            error_msg = "Erro: Variáveis de ambiente ARTERIS_API_BASE_URL ou ARTERIS_API_TOKEN não definidas."
            print(error_msg)
            emit('generation_error', {'error': error_msg})
            emit('generation_finished')
            return

        # --- Etapa 1: Processar DocTypes e Fields ---
        print("--- Buscando DocTypes e Fields ---")
        all_doctypes, child_parent_mapping, doctypes_with_fields = process_arteris_doctypes(api_base_url, api_token)

        if all_doctypes is None:
             error_msg = "Falha ao buscar DocTypes."
             print(error_msg)
             emit('generation_error', {'error': error_msg})
             emit('generation_finished')
             return

        print("\n--- Busca de Metadados concluída ---")

        # --- Etapa 2: Transformar em Entidades ---
        print("--- Transformando Metadados em Entidades ---")
        entity_structure = transform_entity_structure(
            doctypes_with_fields,
            child_parent_mapping
        )

        generated_json_data = entity_structure # Armazena o JSON gerado

        print(f"Encontrados {len(entity_structure.get('entities', []))} DocTypes no módulo Arteris.")
        # Não imprimir a estrutura inteira aqui, apenas confirmar
        print("Estrutura de entidades gerada com sucesso.")

        # --- Etapa 3: (Opcional) Buscar Dados Reais ---
        # Comentado para focar na geração da estrutura primeiro
        # print("\n--- Buscando Dados Reais (Exemplo) ---")
        # doctypes_with_keys = []
        # for doctype in all_doctypes[:5]: # Limita para exemplo
        #     doctype_name = doctype.get("name")
        #     if doctype_name:
        #         keys = get_keys(api_base_url, api_token, doctype_name)
        #         if keys:
        #             doctypes_with_keys.append({"doctype": doctype_name, "keys": keys[:3]}) # Limita chaves

        # all_doctype_data = []
        # for doctype_info in doctypes_with_keys:
        #     doctype_name = doctype_info.get("doctype")
        #     keys = doctype_info.get("keys")
        #     if keys:
        #         for key in keys:
        #             data = get_data_from_key(api_base_url, api_token, doctype_name, key)
        #             if data:
        #                 all_doctype_data.append({"doctype": doctype_name, "key": key, "data": data})
        #             else:
        #                 print(f"Erro ao buscar dados para {doctype_name} com chave {key}.")
        # print(f"Busca de dados reais (exemplo) concluída para {len(all_doctype_data)} registros.")

        print("\n--- Geração Concluída ---")
        emit('generation_complete', {'success': True})

    except Exception as e:
        error_msg = f"Erro durante a geração: {e}"
        print(error_msg)
        import traceback
        print(traceback.format_exc()) # Log completo do erro no servidor
        emit('generation_error', {'error': str(e)}) # Envia erro simplificado ao cliente
    finally:
        emit('generation_finished') # Sinaliza o fim, mesmo com erro

# --- Ponto de Entrada ---
if __name__ == '__main__':
    print("Iniciando servidor Flask com Socket.IO (modo threading)...")
    # Usa socketio.run, que agora usará o servidor de desenvolvimento do Flask/Werkzeug
    # com suporte a threading para SocketIO.
    # A porta 5001 foi mantida.
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True) # debug=True e allow_unsafe_werkzeug=True para desenvolvimento