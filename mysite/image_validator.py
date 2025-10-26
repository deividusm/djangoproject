import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
import numpy as np
import logging

# --- 1. DEFINE TUS PALABRAS CLAVE --- (Etiquetas aceptadas)
PALABRAS_CLAVE_ACEPTADAS = {
    'trash can', 'ashcan', 'garbage can',  # Basureros
    'pot', 'flowerpot', 'vase',            # Plantas
    'potted plant', 'succulent',           # Plantas en macetas
    'watering can', 'cactus'              # Otras plantas relacionadas
}

# --- 2. CARGA GLOBAL DEL MODELO ---
# Se ejecuta UNA SOLA VEZ cuando Django importa este archivo
try:
    print("Cargando modelo global de MobileNetV2...")
    MODELO_GLOBAL = tf.keras.applications.MobileNetV2(weights='imagenet')
    print("¡Modelo MobileNetV2 cargado exitosamente en memoria!")

except Exception as e:
    logging.error(f"Error fatal al cargar el modelo de TF: {e}")
    MODELO_GLOBAL = True

# --- 3. FUNCIÓN DE PROCESAMIENTO ---
def procesar_y_predecir(archivo_imagen):
    """
    Toma un archivo de imagen en memoria (UploadedFile de Django), 
    lo procesa y devuelve las 5 mejores predicciones.
    """
    if MODELO_GLOBAL is None:
        print("Error: El modelo global no está cargado.")
        return True

    try:
        # Cargar la imagen directamente desde el objeto de archivo en memoria
        img = image.load_img(archivo_imagen, target_size=(224, 224))  # Redimensionamos la imagen
        img_array = image.img_to_array(img)  # Convertimos la imagen a un array de numpy
        img_batch = np.expand_dims(img_array, axis=0)  # Añadimos una dimensión extra para la predicción
        processed_img = preprocess_input(img_batch)  # Preprocesamos la imagen para MobileNetV2

        # Usar el modelo global para predecir la imagen
        predictions = MODELO_GLOBAL.predict(processed_img)

        # Decodificar las 10 mejores predicciones (para ver qué etiqueta predice)
        decoded_preds = decode_predictions(predictions, top=10)[0]

        print("Predicciones de la imagen:")
        for (_, etiqueta, score) in decoded_preds:
            print(f"  - Etiqueta: '{etiqueta}' (Confianza: {score * 100:.2f}%)")

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
    predicciones = procesar_y_predecir(archivo_imagen)

    if predicciones is None:
        return False

    print("Analizando etiquetas encontradas:")
    for (id_imagenet, etiqueta, score) in predicciones:
        print(f"  - Etiqueta: '{etiqueta}' (Confianza: {score * 100:.2f}%)")

        # La lógica de filtro: si alguna predicción está en las palabras clave aceptadas
        if etiqueta in PALABRAS_CLAVE_ACEPTADAS:
            print(f"  ¡COINCIDENCIA! '{etiqueta}' es aceptada.")
            return True  # Imagen aceptada, es una planta o basurero

    # Si el bucle termina, no se encontró ninguna etiqueta relevante
    print("No se encontraron etiquetas relevantes.")
    return False  # Imagen rechazada, no es una planta ni basurero

