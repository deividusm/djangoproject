import tensorflow as tf
from keras.utils import load_img, img_to_array
from keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
import numpy as np
import logging
from PIL import Image
import io 
# ... tus otras importaciones (tensorflow, keras, etc.)
# --- 1. DEFINE TUS PALABRAS CLAVE --- (Etiquetas aceptadas)
#
# ¡CAMBIO 1: ETIQUETAS CORREGIDAS!
# Estas son las etiquetas reales de ImageNet (con guiones bajos)
# que MobileNetV2 puede predecir.
#
PALABRAS_CLAVE_ACEPTADAS = {
    'ashcan', 'garbage_can',        # Para basureros
    'flowerpot', 'vase',           # Para macetas, floreros
    'potted_plant',                # ¡La más importante! (planta en maceta)
    'corn', 'broccoli', 'mushroom',"leaf", 'banana', # Alimentos que son plantas
}


# --- 2. CARGA GLOBAL DEL MODELO ---
try:
    print("Cargando modelo global de MobileNetV2...")
    MODELO_GLOBAL = tf.keras.applications.MobileNetV2(weights='imagenet')
    print("¡Modelo MobileNetV2 cargado exitosamente en memoria!")
except Exception as e:
    logging.error(f"Error fatal al cargar el modelo de TF: {e}")
    MODELO_GLOBAL = None

# --- 3. FUNCIÓN DE PROCESAMIENTO ---
def procesar_y_predecir(archivo_imagen):
    """
    Toma un archivo de imagen en memoria (UploadedFile de Django), 
    lo procesa y devuelve las 10 mejores predicciones.
    """
    if MODELO_GLOBAL is None:
        print("Error: El modelo global no está cargado.")
        return None

    try:
    
        # ¡CAMBIO! Envolvemos el archivo en io.BytesIO
        # Esto lee los bytes del archivo y los presenta en un formato que load_img entiende.
        img = load_img(io.BytesIO(archivo_imagen.read()), target_size=(224, 224))
        img_array = img_to_array(img)
# ...
        
        img_batch = np.expand_dims(img_array, axis=0)  # Añadimos una dimensión extra
        processed_img = preprocess_input(img_batch)  # Preprocesamos la imagen

        # Usar el modelo global para predecir la imagen
        predictions = MODELO_GLOBAL.predict(processed_img)

        # Decodificar las 10 mejores predicciones
        decoded_preds = decode_predictions(predictions, top=10)[0]

        print("\n--- Predicciones de la imagen: ---")
        for (_, etiqueta, score) in decoded_preds:
            print(f"   - Etiqueta: '{etiqueta}' (Confianza: {score * 100:.2f}%)")
        print("---------------------------------")
            
        return decoded_preds

    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
        return None

# --- 4. FUNCIÓN PRINCIPAL DE VALIDACIÓN ---
def es_imagen_relevante(archivo_imagen):
    """
    Función principal que combina todo.
    Recibe un archivo, lo predice y devuelve True o False.
    """
    
    # --- ¡CAMBIO 2: REINICIAR EL ARCHIVO! ---
    # Esto asegura que Keras lea el archivo desde el principio.
    try:
        archivo_imagen.seek(0)
    except Exception as e:
        print(f"Advertencia: No se pudo hacer seek(0) al archivo. {e}")
    
    predicciones = procesar_y_predecir(archivo_imagen)

    if predicciones is None:
        return False

    print("Analizando etiquetas encontradas:")
    for (id_imagenet, etiqueta, score) in predicciones:

        # La lógica de filtro: si alguna predicción está en las palabras clave aceptadas
        if etiqueta in PALABRAS_CLAVE_ACEPTADAS:
            print(f"   ¡COINCIDENCIA! '{etiqueta}' es aceptada.")
            return True  # Imagen aceptada

    # Si el bucle termina, no se encontró ninguna etiqueta relevante
    print("   No se encontraron etiquetas relevantes. Imagen rechazada.")
    
    return False  # Imagen rechazada