import requests
import os
import ecdsa

# URL de tu nodo central en Docker
NODE_URL = "http://localhost:5000"

def cargar_o_crear_llaves():
    """Carga las llaves guardadas en disco o genera unas nuevas si no existen."""
    if os.path.exists("private_key.pem") and os.path.exists("public_key.pem"):
        with open("private_key.pem", "r") as f:
            priv_hex = f.read().strip()
        with open("public_key.pem", "r") as f:
            pub_hex = f.read().strip()
        print("\n[🔑] Llaves criptográficas cargadas con éxito desde el disco.")
        return priv_hex, pub_hex
    else:
        print("\n[🆕] No se encontraron llaves. Generando nuevo par de llaves SECP256k1...")
        
        # Criptografía nativa de la red (Curva SECP256k1)
        private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        public_key = private_key.get_verifying_key()
        
        priv_hex = private_key.to_string().hex()
        pub_hex = public_key.to_string().hex()
        
        with open("private_key.pem", "w") as f:
            f.write(priv_hex)
        with open("public_key.pem", "w") as f:
            f.write(pub_hex)
            
        print("[💾] Tus llaves reales se han guardado de forma segura en 'private_key.pem' y 'public_key.pem'.")
        return priv_hex, pub_hex

def consultar_saldo(pub_hex):
    """Muestra la información de la billetera."""
    print("\n--- 💰 ESTADO DE LA BILLETERA ---")
    print(f"Tu Dirección Pública (Hex):\n{pub_hex}")
    # Tu nodo asigna un balance base de 1000 a cualquier llave nueva en la función get_balance()
    print("\nSaldo Base Inicial en Red: 1000 tokens")

def realizar_transferencia(priv_hex, pub_hex):
    """Crea, firma con criptografía real y transmite una transacción a la mempool."""
    print("\n--- 💸 NUEVA TRANSFERENCIA ---")
    receptor = input("Introduce la Dirección Pública del receptor (Hex): ").strip()
    try:
        monto = int(input("Introduce el monto a enviar: "))
    except ValueError:
        print("❌ Monto inválido.")
        return

    if not receptor:
        print("❌ El receptor no puede estar vacío.")
        return

    # Creamos el mensaje dinámico de la transacción
    mensaje_a_firmar = f"Enviar {monto} tokens a {receptor}"

    print("\nFirmando transacción con tu clave privada...")
    try:
        # Reconstruimos la llave privada desde su formato Hex
        priv_key_obj = ecdsa.SigningKey.from_string(bytes.fromhex(priv_hex), curve=ecdsa.SECP256k1)
        
        # Firmamos el mensaje digitalmente
        firma_bytes = priv_key_obj.sign(mensaje_a_firmar.encode())
        firma_hex = firma_bytes.hex()
        
        # Armamos el payload idéntico a lo que pide tu nodo_l1.py
        payload = {
            "pub_key": pub_hex,
            "signature": firma_hex,
            "message": mensaje_a_firmar,
            "amount": monto
        }
        
        print("Transmitiendo transacción firmada al nodo Docker...")
        resp = requests.post(f"{NODE_URL}/tx/new", json=payload)
        
        if resp.status_code == 201:
            print(f"✅ ¡Éxito! Transacción aceptada en la Mempool de la red: {resp.json()}")
        else:
            print(f"❌ Transacción rechazada por el Nodo ({resp.status_code}): {resp.json()}")
            
    except Exception as e:
        print(f"❌ Error crítico en el firmado o envío: {e}")

def menu():
    priv_hex, pub_hex = cargar_o_crear_llaves()
    
    while True:
        print("\n==============================")
        print("📱 CLIENTE OFICIAL BLOCKCHAIN L1")
        print("==============================")
        print("1. Ver mi Dirección Pública y Saldo")
        print("2. Enviar Tokens (Transferencia)")
        print("3. Salir")
        
        opcion = input("Selecciona una opción (1-3): ").strip()
        
        if opcion == "1":
            consultar_saldo(pub_hex)
        elif opcion == "2":
            realizar_transferencia(priv_hex, pub_hex)
        elif opcion == "3":
            print("Saliendo del cliente. ¡Buen viaje!")
            break
        else:
            print("❌ Opción no válida.")

if __name__ == "__main__":
    menu()
