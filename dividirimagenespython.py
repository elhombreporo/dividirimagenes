import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Definir las credenciales de la cuenta de servicio
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'C:\Users\elhom\Documents\PYTHON\dividirimagenespython-a153c4364afe.json'
creds = None
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Definir las coordenadas de corte de las imágenes
partes_primera_imagen = 6
partes_resto_imagenes = 2
coordenadas = [(0,0,600,400), (600,0,1200,400), (1200,0,1800,400), (1800,0,2400,400), (2400,0,3000,400), (3000,0,3600,400), (0,400,600,800), (600,400,1200,800)]

# Definir la función que divide las imágenes y las guarda en otra carpeta
def dividir_imagenes(origen_id, destino_id):
    service = build('drive', 'v3', credentials=creds)
    query = "parents='" + origen_id + "' and mimeType contains 'image/'"
    results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    for item in items:
        nombre = item['name']
        archivo_id = item['id']
        # Obtener la información de la imagen
        file = service.files().get_media(fileId=archivo_id).execute()
        with open(nombre, 'wb') as f:
            f.write(file)
        # Dividir la imagen en partes
        if item == items[0]:
            partes = partes_primera_imagen
        else:
            partes = partes_resto_imagenes
        imagen = Image.open(nombre)
        i = 1
        for coordenada in coordenadas[:partes]:
            nombre_parte = f"{os.path.splitext(nombre)[0]}_{i}.png"
            imagen.crop(coordenada).save(nombre_parte)
            # Subir la imagen dividida a la carpeta destino
            file_metadata = {'name': nombre_parte, 'parents': [destino_id]}
            media = MediaFileUpload(nombre_parte, resumable=True)
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            i += 1
        os.remove(nombre)
