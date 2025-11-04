import tensorflow as tf
from keras.utils import load_img, img_to_array
from keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
import numpy as np
import logging
import io 

# --- 1. IMPORTAR MODELOS DE DJANGO ---
# ¡CAMBIO 1: Importamos tu modelo 'Categorias'!
# La lista 'PALABRAS_CLAVE_ACEPTADAS' se elimina, ya no la necesitamos.
from ranking.models import Categorias

# --- 2. CARGA GLOBAL DEL MODELO ---
# (Esto no cambia, está perfecto)
try:
    print("Cargando modelo global de MobileNetV2...")
    MODELO_GLOBAL = tf.keras.applications.MobileNetV2(weights='imagenet')
    print("¡Modelo MobileNetV2 cargado exitosamente en memoria!")
except Exception as e:
    logging.error(f"Error fatal al cargar el modelo de TF: {e}")
    MODELO_GLOBAL = None

# --- 3. FUNCIÓN DE PROCESAMIENTO ---
# (Esto no cambia, está perfecto)
def procesar_y_predecir(archivo_imagen):
    """
    Toma un archivo de imagen en memoria (UploadedFile de Django), 
    lo procesa y devuelve las 10 mejores predicciones.
    """
    if MODELO_GLOBAL is None:
        print("Error: El modelo global no está cargado.")
        return None

    try:
        # Re-leemos el archivo desde el principio
        archivo_imagen.seek(0)
        img = load_img(io.BytesIO(archivo_imagen.read()), target_size=(224, 224))
        img_array = img_to_array(img)
        
        img_batch = np.expand_dims(img_array, axis=0)
        processed_img = preprocess_input(img_batch) 

        predictions = MODELO_GLOBAL.predict(processed_img)
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
# ¡CAMBIO 2: Lógica de validación actualizada!
def es_imagen_relevante(archivo_imagen):
    """
    Función principal que combina todo.
    Recibe un archivo, lo predice y lo compara con la BD.
    
    DEVUELVE:
    - El objeto 'Categorias' si hay coincidencia.
    - 'None' si no hay coincidencia o hay un error.
    """
    
    # 1. Obtener las predicciones del modelo de IA
    predicciones = procesar_y_predecir(archivo_imagen)

    if predicciones is None:
        return None  # Devuelve None, no False

    print("Analizando etiquetas encontradas y comparando con la BD:")
    
    # 2. Extraer solo las etiquetas de texto (ej. 'potted_plant', 'ashcan')
    etiquetas_predichas = [etiqueta for (_, etiqueta, _) in predicciones]
    
    # 3. Consultar la BD
    # Buscamos en la tabla 'Categorias' si 'Nombre_categoria'
    # coincide con ALGUNA de las etiquetas predichas.
    try:
        # Esta es una consulta eficiente:
        # "SELECT * FROM Categorias WHERE Nombre_categoria IN ('potted_plant', 'ashcan', ...)"
        categoria_encontrada = Categorias.objects.filter(
            Nombre_categoria__in=etiquetas_predichas
        ).first() # .first() = danos la primera que encuentres

        # 4. Devolver el resultado
        if categoria_encontrada:
            # ¡ÉXITO!
            print(f"   ¡COINCIDENCIA! '{categoria_encontrada.Nombre_categoria}' está en la BD.")
            return categoria_encontrada # <--- Devuelve el objeto Categoria completo
        
        else:
            # No se encontró ninguna
            print("   No se encontraron etiquetas relevantes en la BD. Imagen rechazada.")
            return None # <--- Devuelve None
            
    except Exception as e:
         print(f"Error al consultar la BD en el validador: {e}")
         return None # Si hay error de BD, rechazar