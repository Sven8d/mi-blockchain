import requests, hashlib, time

NODE_URL = "http://127.0.0.1:5000"

def minar():
    print("Iniciando orquestador de minería automatizado...")
    while True:
        try:
            diff = 4 
            nonce = 0
            # Bucle de fuerza bruta para encontrar el Nonce válido
            while True:
                if hashlib.sha256(f"{nonce}".encode()).hexdigest().startswith('0' * diff):
                    break
                nonce += 1
            
            # Envío del bloque minado al nodo Flask
            resp = requests.post(f"{NODE_URL}/mine", json={"nonce": nonce})
            print(f"Respuesta del Nodo: {resp.json()}")
            
            # CALIBRACIÓN: Espera de 15 segundos entre bloques para acumular transacciones reales
            print("Bloque cerrado con éxito. Esperando 15 segundos para dar tiempo a la mempool...")
            time.sleep(15)
            
        except Exception as e:
            print("Esperando conexión con el nodo o resolviendo parámetros...")
            time.sleep(2)

if __name__ == "__main__":
    minar()
