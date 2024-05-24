import os
import time
from watchdog.observers import Observer
from Handlers import OnUploadHandler, OnRecieveHandler
from utils import Cloud, log, jsonReader

if __name__ == "__main__":

    # path = sys.argv[1] if len(sys.argv) > 1 else '.'
    try:
        json_data = jsonReader.read_json('settings.json')
        path = json_data['Folder']
    except KeyError:
        print('No se pudo leer la ruta de settings.json, se usara el directorio actual como ruta de observacion')
        path = '.'

    log.existsFolder()
    output = f'Observando el directorio : {path}'
    print(output)
    log.write(output)
    Cloud.checkOnCloud(path)

    event_handlers = [OnUploadHandler(), OnRecieveHandler()]
    observer = Observer()

    observer.schedule(event_handlers[0], path, recursive=False)
    observer.schedule(event_handlers[1], path, recursive=False)
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        
        output = f'Dejando de observar el directorio : {path}, salida de manera manual'
        print(output)
        log.write(output)
        print("Registro guardado")
        print(os.path.abspath(jsonReader.read_json('settings.json')['logDirectory']))
        observer.stop()
        observer.join()
    except Exception as e:
        
        output = f'Error inesperado : {e} - Salida Inesperada'
        print(output)
        log.write(output)
        print("Registro guardado")
        print(os.path.abspath(jsonReader.read_json('settings.json')['logDirectory']))
        observer.stop()
        observer.join()