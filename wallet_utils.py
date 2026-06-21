# Contenido de wallet_utils.py
from ecdsa import SigningKey, SECP256k1
import base64

def generar_claves():
    priv_key = SigningKey.generate(curve=SECP256k1)
    pub_key = priv_key.verifying_key
    with open("private_key.pem", "wb") as f: f.write(priv_key.to_pem())
    with open("public_key.pem", "wb") as f: f.write(pub_key.to_pem())
    print("Claves guardadas como private_key.pem y public_key.pem")

def firmar_transaccion(monto, receptor):
    with open("private_key.pem", "rb") as f:
        priv_key = SigningKey.from_pem(f.read())
    
    mensaje = f"{monto}{receptor}"
    firma = priv_key.sign(mensaje.encode())
    return base64.b64encode(firma).decode('utf-8')

if __name__ == "__main__":
    generar_claves()
