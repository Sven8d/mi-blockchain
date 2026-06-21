import ecdsa, json, requests

def create_wallet():
    # Generar llave privada
    private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    # Generar llave pública
    public_key = private_key.get_verifying_key()
    
    return private_key, public_key

def sign_transaction(private_key, message):
    signature = private_key.sign(message.encode())
    return signature.hex()

# Ejemplo de uso:
priv, pub = create_wallet()
msg = "Enviar 10 tokens a dirección_destino"
sig = sign_transaction(priv, msg)

print(f"Tu Dirección Pública: {pub.to_string().hex()}")
print(f"Firma de la transacción: {sig}")
