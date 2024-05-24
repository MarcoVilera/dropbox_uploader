import os
import platform
from time import sleep
import datetime
import re
from watchdog.events import FileSystemEvent, FileSystemEventHandler
import dropbox
from utils import Cloud, log,constants,jsonReader

class OnUploadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        #TODO optimizar CODIGO
        file_done = False
        file_size = -1
        file_path = event.src_path
        if platform.system() == 'Windows':
            file_name = event.src_path.split('\\')[-1] # Windows
        else:
            file_name = event.src_path.split('/')[-1] # Linux
        while file_size != os.path.getsize(file_path):
        #Comprueba iterativamente el tamaño del archivo hasta que sea del mismo tamaño
            file_size = os.path.getsize(file_path)
            sleep(1)
            
        while not file_done:
        #Verifica si el archivo esta en uso (En transferencia)
            try:
                #Intenta renombrar el archivo, si no se puede, es porque esta en uso
                os.rename(file_path, file_path)
                file_done = True

            except:
                return True  
            
        #A este punto el archivo ya fue transferido completamente
        #SUBIDA DE DATOS A DROPBOX
        dbx = dropbox.Dropbox(app_key = constants.APP_KEY, app_secret = constants.APP_SECRET, oauth2_refresh_token = constants.REFRESH_TOKEN)
        result = dbx.files_list_folder(constants.DESTINATION_FOLDER, recursive=True)
        result.entries.pop(0) # Elimina el primer elemento que es el directorio raiz
        files_on_cloud = [file.name for file in result.entries]
        Cloud.upload(file_path,files_on_cloud)
        # file_extension = os.path.splitext(file_name)[1]
        # if file_extension in constants.ALLOWED_EXTENSIONS:

        #     dbx = dropbox.Dropbox(app_key = constants.APP_KEY, app_secret = constants.APP_SECRET, oauth2_refresh_token = constants.REFRESH_TOKEN)
        #     result = dbx.files_list_folder(constants.DESTINATION_FOLDER, recursive=True)
        #     result.entries.pop(0) # Elimina el primer elemento que es el directorio raiz
        #     files_on_cloud = [file.name for file in result.entries]

        #     configData = jsonReader.read_json('settings.json')
        #     dest_path = configData["DestinationFolder"]+"/"+file_name
        #     if file_extension == '.bak':
        #         print("Ingresando bak")
        #         file_size = os.path.getsize(file_path)
        #         regex = r'^(.*?)_(\d{4}\d{2})(01|30|31|28)_(\d{6})\.bak$'
        #         match = re.match(regex, file_name)
        #         try:
        #             year = int(match.group(2)[:4])
        #             month = int(match.group(2)[4:])
        #             day = int(match.group(3))
        #         except:
        #             print("Match Invalido")
        #             month = 0
        #             day = 0

        #         if month == 2 and (day == 28 or day == 1):
        #             valid_bak = True
        #             print("fecha valida")
        #             Cloud.update_bak_files(year,month)
        #         elif month in [1,3,4,5,6,7,8,9,10,11,12] and (day == 30 or day == 1):
        #             valid_bak = True
        #             print("fecha valida")
        #             Cloud.update_bak_files(year,month)
        #         else:
        #             print(month, day)
        #             print("fecha invalida")
        #             valid_bak = False
        #     else:
        #         valid_bak = True
            
        #     if file_name not in files_on_cloud and valid_bak:
                
        #         with open(event.src_path, 'rb') as f: #Lectura binaria para dividir el archivo en partes

        #             try:

        #                 file_size = os.path.getsize(event.src_path)
        #                 output = f"Subiendo archivo a la nube : {file_name} - {file_size} bytes"
        #                 print(output)
                        
        #                 if file_size < constants.CHUNK_SIZE:
        #                     #Finaliza la subida del archivo
        #                     dbx.files_upload(f.read(), dest_path, mode=dropbox.files.WriteMode.overwrite)
        #                     sleep(1)
        #                     output = f'Archivo guardado en la nube correctamente : {file_name}'
        #                     print(output)
        #                     log.write(output)

        #                 else:
        #                     #Subida por partes
        #                     session_start_result = dbx.files_upload_session_start(f.read(constants.CHUNK_SIZE))
        #                     cursor = dropbox.files.UploadSessionCursor(session_id=session_start_result.session_id, offset=f.tell())
        #                     commit = dropbox.files.CommitInfo(path=dest_path, mode=dropbox.files.WriteMode.overwrite)

        #                     while f.tell() < file_size:

        #                         percent_uploaded = round((f.tell() / file_size) * 100,0)
        #                         print(f'\rPorcentaje subido : {percent_uploaded}%', end='')

        #                         if (file_size - f.tell()) <= constants.CHUNK_SIZE:
        #                             dbx.files_upload_session_finish(f.read(constants.CHUNK_SIZE), cursor, commit)
        #                             print('\n', end="")
        #                             output = f'Archivo guardado en la nube correctamente : {file_name}'
        #                             print(output)
        #                             log.write(output)
        #                         else:
        #                             dbx.files_upload_session_append_v2(f.read(constants.CHUNK_SIZE), cursor)
        #                             cursor.offset = f.tell()

        #             except Exception as e:
        #                 output = f'Error subiendo el archivo : {file_name} - {e}'
        #                 print(output)
        #                 log.write(output)
        #                 return False
        #     elif valid_bak == False:
        #         output = f'Archivo no válido para la subida, guardado en local : {file_name}'
        #         print("prueba")
        #         print(output)
        #         log.write(output)
        # else:
        #     output = f'Archivo no válido para la subida, guardado en local : {file_name}'
        #     print(output)
        #     log.write(output)    

    def on_deleted(self, event):
        file_name = event.src_path.split('\\')[-1]
        output = f'Archivo eliminado : {file_name}'
        print(output)
        log.write(output)
        

class OnRecieveHandler(FileSystemEventHandler):
    def on_created(self, event):
        file_name = event.src_path.split('\\')[-1] # Windows

        output = f'Archivo recibido : {file_name} - {os.path.getsize(event.src_path)} bytes'
        print(output)
        log.write(output)