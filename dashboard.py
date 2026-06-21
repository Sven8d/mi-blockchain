import os
import shutil
import json
import plyvel

ORIGINAL_DB = 'blockchain_db/'
TEMP_DB = 'blockchain_db_dashboard/'

print("=== Dashboard del Nodo L1 ===")

try:
    # 1. Limpieza de procesos y cachés previas
    if os.path.exists(TEMP_DB):
        shutil.rmtree(TEMP_DB)

    # 2. Clonación instantánea saltándose el archivo LOCK de Docker
    shutil.copytree(
        ORIGINAL_DB, 
        TEMP_DB, 
        ignore=shutil.ignore_patterns('LOCK', '*.log', 'CURRENT.bak')
    )

    # 3. Apertura segura de la base de datos temporal
    db = plyvel.DB(TEMP_DB, create_if_missing=False)
    
    # 4. Lectura y renderizado de la estructura física del bloque
    bloques_encontrados = False
    for key, value in db.iterator():
        bloques_encontrados = True
        block = json.loads(value.decode())
        
        # Leemos las llaves reales registradas en tu almacenamiento físico
        timestamp = block.get('timestamp', 0)
        nonce = block.get('nonce', 'N/A')
        txs = block.get('txs', [])
        
        print(f"\n[Bloque detectado en disco]")
        print(f"  ID de Tiempo (Key): {key.decode()}")
        print(f"  Nonce de PoW:       {nonce}")
        print(f"  Transacciones:      {len(txs)}")

    if not bloques_encontrados:
        print("\nBase de datos inicializada pero sin bloques físicos asentados aún.")

    # 5. Cierre y liberación de archivos del sistema
    db.close()
    shutil.rmtree(TEMP_DB)

except Exception as e:
    print(f"Error al acceder al dashboard: {e}")
