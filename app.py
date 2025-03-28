from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime

# Carrega as variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuração da chave secreta
app.secret_key = os.getenv('SECRET_KEY', 'sua-chave-secreta-padrao')

# Configurações do Baserow
BASEROW_CONFIG = {
    'api_url': os.getenv('BASEROW_API_URL'),
    'api_token': os.getenv('BASEROW_API_TOKEN'),
    'database_id': os.getenv('BASEROW_DATABASE_ID'),
    'table_id': os.getenv('BASEROW_TABLE_ID')
}

# Mapeamento de categorias (letra -> nome completo)
CATEGORIAS = {
    'C': 'CONCESSIONARIA',
    'S': 'CORRETORA',
    'P': 'PLATAFORMA',
    'E': 'EMPRESA',
    'CONCESSIONARIA': 'CONCESSIONARIA',
    'CORRETORA': 'CORRETORA',
    'PLATAFORMA': 'PLATAFORMA',
    'EMPRESA': 'EMPRESA'
}

# Mapeamento de regras de comissão (código -> nome completo)
REGRAS_COMISSAO = {
    '40641669': 'COMISSAO 2022 PLATAFORMA',
    '40641885': 'COMISSAO 2022 CONCESSIONARIA',
    '40641970': 'COMISSAO 2022 CORRETORA SUSEP',
    '23798565': 'VENDA ADMINISTRATIVA',
    '40642032': 'COMISSAO 2022 SUSEP VITALICIO',
    '29745447': 'CONCESSIONARIA - PARTICIONAMENTO 2',
    'COMISSAO 2022 PLATAFORMA': 'COMISSAO 2022 PLATAFORMA',
    'COMISSAO 2022 CONCESSIONARIA': 'COMISSAO 2022 CONCESSIONARIA',
    'COMISSAO 2022 CORRETORA SUSEP': 'COMISSAO 2022 CORRETORA SUSEP',
    'VENDA ADMINISTRATIVA': 'VENDA ADMINISTRATIVA',
    'COMISSAO 2022 SUSEP VITALICIO': 'COMISSAO 2022 SUSEP VITALICIO',
    'CONCESSIONARIA - PARTICIONAMENTO 2': 'CONCESSIONARIA - PARTICIONAMENTO 2'
}

# Lista de plataformas válidas
PLATAFORMAS_VALIDAS = [
    'SUSEP', 'AGECOR 2', 'ABSOLUTA', 'CASA DE NEGOCIOS', 'UNITEDCLASS',
    'JC LUZ', 'SUN CORRETORA', 'ATACK', 'CASA DO CONSULTOR RJ', 'VISUAL',
    'DISKDESLTA', 'PROJETOS', 'ASSURE RIO', 'BLUE LIGHT', 'MS BUSINESS',
    'ROYAL', 'PRIMUM', 'MASTER SAUDE', 'NOVA CASA DO CONSULTOR'
]

def append_to_baserow(data):
    """Adiciona uma linha ao Baserow"""
    try:
        # Prepara os dados para o Baserow
        baserow_data = {
            'codigo': data.get('codigo', ''),
            'cnpj': data.get('cnpj', ''),
            'razao_social': data.get('razao_social', ''),
            'nome_fantasia': data.get('nome_fantasia', ''),
            'plataforma': data.get('plataforma', ''),
            'categoria': CATEGORIAS.get(data.get('categoria', ''), ''),
            'regra_comissao': REGRAS_COMISSAO.get(data.get('regra_comissao', ''), ''),
            'cep': data.get('cep', ''),
            'logradouro': data.get('logradouro', ''),
            'endereco': data.get('endereco', ''),
            'numero': data.get('numero', ''),
            'complemento': data.get('complemento', ''),
            'bairro': data.get('bairro', ''),
            'cidade': data.get('cidade', ''),
            'estado': data.get('estado', ''),
            'telefone': data.get('telefone', ''),
            'banco': data.get('banco', ''),
            'agencia': data.get('agencia', ''),
            'conta': data.get('conta', ''),
            'email': data.get('email', ''),
            'cpf_representante': data.get('cpf_representante', ''),
            'nome_representante': data.get('nome_representante', '')
        }

        # Monta a URL da API do Baserow
        url = f"{BASEROW_CONFIG['api_url']}/api/database/rows/table/{BASEROW_CONFIG['table_id']}/?user_field_names=true"
        
        print(f"URL da API: {url}")
        print(f"Dados sendo enviados: {json.dumps(baserow_data, indent=2)}")
        
        # Faz a requisição
        headers = {
            'Authorization': f'Token {BASEROW_CONFIG["api_token"]}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, json=baserow_data)
        print(f"Status code: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Erro ao salvar no Baserow: {str(e)}")
        return False

@app.route('/')
def index():
    return render_template('cadastro.html')

@app.route('/api/cadastro', methods=['POST'])
def cadastro():
    try:
        data = request.json
        print(f"Dados recebidos: {json.dumps(data, indent=2)}")
        
        # Valida campos obrigatórios
        required_fields = ['cnpj', 'razao_social', 'nome_fantasia', 'plataforma', 'categoria', 'regra_comissao']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Campo {field} é obrigatório'
                }), 400
        
        # Valida se a plataforma é válida
        if data.get('plataforma') not in PLATAFORMAS_VALIDAS:
            return jsonify({
                'success': False,
                'message': 'Plataforma inválida'
            }), 400
            
        # Valida se a categoria é válida
        categoria = data.get('categoria', '')
        if categoria not in CATEGORIAS:
            return jsonify({
                'success': False,
                'message': f'Categoria inválida: {categoria}'
            }), 400
            
        # Valida se a regra de comissão é válida
        regra = data.get('regra_comissao', '')
        if regra not in REGRAS_COMISSAO:
            return jsonify({
                'success': False,
                'message': f'Regra de comissão inválida: {regra}'
            }), 400
        
        # Tenta salvar no Baserow
        if append_to_baserow(data):
            return jsonify({
                'success': True,
                'message': 'Dados cadastrados com sucesso!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao salvar os dados'
            }), 500
            
    except Exception as e:
        print(f"Erro no cadastro: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao cadastrar dados: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 