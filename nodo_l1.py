import hashlib, time, plyvel, json, ecdsa, requests
from flask import Flask, request, jsonify

app = Flask(__name__)
db = plyvel.DB('blockchain_db/', create_if_missing=True)
mempool = []
PEERS = set() # Nodos conectados

# --- LÓGICA CORE ---
def get_last_block():
    last_block = None
    for _, value in db.iterator():
        last_block = json.loads(value.decode())
    return last_block

def calculate_hash(block):
    # Aseguramos que el JSON se ordene para que el hash sea determinista
    block_copy = {k: v for k, v in block.items() if k in ["timestamp", "txs", "nonce"]}
    return hashlib.sha256(json.dumps(block_copy, sort_keys=True).encode()).hexdigest()

# --- 1. SEGURIDAD ---
def verify_signature(pub_key_hex, sig_hex, message):
    try:
        key = ecdsa.VerifyingKey.from_string(bytes.fromhex(pub_key_hex), curve=ecdsa.SECP256k1)
        return key.verify(bytes.fromhex(sig_hex), message.encode())
    except: 
        return False

# --- 2. CONTABILIDAD ---
def get_balance(pub_key):
    balance = 1000 # Saldo base inicial
    for _, value in db.iterator():
        block = json.loads(value.decode())
        for tx in block.get('txs', []):
            if tx.get('sender') == pub_key: balance -= tx.get('amount', 0)
            if tx.get('receiver') == pub_key: balance += tx.get('amount', 0)
    return balance

# --- 3. ENDPOINTS PÚBLICOS ---
@app.route('/tx/new', methods=['POST'])
def new_tx():
    data = request.get_json()
    if not verify_signature(data['pub_key'], data['signature'], data['message']):
        return jsonify({"error": "Firma inválida"}), 401
    
    # Validar fondos
    if get_balance(data['pub_key']) < data['amount']:
        return jsonify({"error": "Fondos insuficientes"}), 400
        
    mempool.append(data)
    return jsonify({"status": "Transacción en Mempool"}), 201

@app.route('/mine', methods=['POST'])
def mine():
    last_block = get_last_block()
    index = (last_block.get('index', 0) + 1) if last_block else 1
    
    # Mantenemos tu estructura exacta de bloque detectada en la base de datos
    block = {
        "timestamp": time.time(),
        "txs": list(mempool), # Copia las transacciones actuales de la mempool
        "nonce": request.get_json().get('nonce')
    }
    
    # Validar PoW (4 ceros al inicio del hash del nonce)
    if hashlib.sha256(str(block['nonce']).encode()).hexdigest().startswith("0000"):
        db.put(str(block['timestamp']).encode(), json.dumps(block).encode())
        mempool.clear() # Limpia la sala de espera
        return jsonify({"message": "Bloque minado", "index": index}), 201
    return jsonify({"error": "PoW inválido"}), 400

@app.route('/nodes/register', methods=['POST'])
def register_node():
    node = request.get_json().get('url')
    PEERS.add(node)
    return jsonify({"message": "Nodo agregado", "peers": list(PEERS)}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
