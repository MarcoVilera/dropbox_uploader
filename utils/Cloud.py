import os
import re
import platform
from time import sleep
import dropbox
from utils import constants, log

def checkOnCloud(path):
    """
    Checks if files in the given path exist on the cloud storage.
    if not, uploads them to the cloud storage.
    Args:
        path (str): The path to the local directory containing the files to check.
        
    Returns:
        None
    """
    
    files_on_cloud = []
    dbx = dropbox.Dropbox(app_key = constants.APP_KEY, app_secret = constants.APP_SECRET, oauth2_refresh_token = constants.REFRESH_TOKEN)
    result = dbx.files_list_folder(constants.DESTINATION_FOLDER, recursive=True)
    result.entries.pop(0) # Elimina el primer elemento que es el directorio raiz
    files_on_cloud = [file.name for file in result.entries]

    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        file_name = file

        if file_name not in files_on_cloud:
            upload(file_path, files_on_cloud)
    

def upload(path, files_on_cloud = []):
    
    file_path = path
    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_name)[1]
    
    if file_extension in constants.ALLOWED_EXTENSIONS and file_name not in files_on_cloud:

        dbx = dropbox.Dropbox(app_key = constants.APP_KEY, app_secret = constants.APP_SECRET, oauth2_refresh_token = constants.REFRESH_TOKEN)
        dest_path = constants.DESTINATION_FOLDER+"/"+file_name

        if file_extension == '.bak':
            file_name_regex = re.match(constants.REGEX, file_name)
            try:
                file_to_upload_name = file_name_regex.group(1)
                file_to_upload_year = int(file_name_regex.group(2)[:4])
                file_to_upload_month = int(file_name_regex.group(2)[4:])
                file_to_upload_day = int(file_name_regex.group(3))
            except:
                print("Match Invalido")
                file_to_upload_month = 0
                file_to_upload_day = 0

            if file_to_upload_month == 2 and (file_to_upload_day == 28 or file_to_upload_day == 1):
                valid_bak = True
                
            elif file_to_upload_month in [1,3,4,5,6,7,8,9,10,11,12] and (file_to_upload_day == 30 or file_to_upload_day == 1):
                valid_bak = True
                
            else:
                valid_bak = False
        else:
            valid_bak = True

        if valid_bak:
            if file_extension == ".bak":

                result = dbx.files_list_folder(constants.DESTINATION_FOLDER, recursive=True)
                result.entries.pop(0) # Elimina el primer elemento que es el directorio raiz
                files_on_cloud = [file.name for file in result.entries]

                for file_on_cloud in files_on_cloud:
                    file_extension = os.path.splitext(file_on_cloud)[1]
                    if file_extension == ".bak":
                        file_on_cloud_regex = re.match(constants.REGEX, file_on_cloud)

                        file_on_cloud_name = file_on_cloud_regex.group(1)
                        file_on_cloud_year = int(file_on_cloud_regex.group(2)[:4])
                        file_on_cloud_month = int(file_on_cloud_regex.group(2)[4:])
                        file_on_cloud_day = int(file_on_cloud_regex.group(3))

                        if file_to_upload_name == file_on_cloud_name:
                            if (file_on_cloud_year < file_to_upload_year) or (file_on_cloud_year == file_to_upload_year and file_on_cloud_month < file_to_upload_month) or (file_on_cloud_month == 2 and (file_on_cloud_month == 28 or file_on_cloud_month == 1) or (file_on_cloud_month == file_to_upload_month and file_to_upload_day > file_on_cloud_day)):
                                dbx.files_delete(constants.DESTINATION_FOLDER + '/' + file_on_cloud)
                                output = f'Archivo .bak del mes pasado eliminado - {file_on_cloud_name}, subiendo nuevo .bak del mes - {file_name}'
                                print(output)
                                log.write(output)
                                break


        if file_name not in files_on_cloud and valid_bak:

            with open(file_path, 'rb') as f: #Lectura binaria para dividir el archivo en partes

                try:
                    file_size = os.path.getsize(file_path)
                    output = f"Subiendo archivo a la nube : {file_name} - {file_size} bytes"
                    print(output)
                        
                    if file_size < constants.CHUNK_SIZE:
                        #Finaliza la subida del archivo
                        dbx.files_upload(f.read(), dest_path, mode=dropbox.files.WriteMode.overwrite)
                        sleep(1)
                        output = f'Archivo guardado en la nube correctamente : {file_name}'
                        print(output)
                        log.write(output)

                    else:
                        #Subida por partes
                        session_start_result = dbx.files_upload_session_start(f.read(constants.CHUNK_SIZE))
                        cursor = dropbox.files.UploadSessionCursor(session_id=session_start_result.session_id, offset=f.tell())
                        commit = dropbox.files.CommitInfo(path=dest_path, mode=dropbox.files.WriteMode.overwrite)

                        while f.tell() < file_size:

                            percent_uploaded = round((f.tell() / file_size) * 100,0)
                            print(f'\rPorcentaje subido : {percent_uploaded}%', end='')

                            if (file_size - f.tell()) <= constants.CHUNK_SIZE:
                                dbx.files_upload_session_finish(f.read(constants.CHUNK_SIZE), cursor, commit)
                                print('\n', end="")
                                output = f'Archivo guardado en la nube correctamente : {file_name}'
                                print(output)
                                log.write(output)
                            else:
                                dbx.files_upload_session_append_v2(f.read(constants.CHUNK_SIZE), cursor)
                                cursor.offset = f.tell()

                except Exception as e:
                    output = f'Error subiendo el archivo : {file_name} - {e}'
                    print(output)
                    log.write(output)

        else:
            output = f'Archivo no válido para la subida, guardado en local : {file_name}'
            print(output)
            log.write(output)
