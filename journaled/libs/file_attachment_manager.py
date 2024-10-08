import os
from PIL import Image
import logging
class FileAttachmentManager:
    def __init__(self,app, user):
        self.user = user
        self.app = app
        if os.path.exists(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}") == False:
            os.makedirs(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}")

    def save_file(self, file, entry_id):
        if os.path.exists(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}") == False:
            os.makedirs(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}")
            
        img_ext = ['jpg','jpeg','png','gif']
        if file.filename.split('.')[-1].lower() not in img_ext:
            logging.info(f"Saving file {file.filename}")
            file.save(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}/{file.filename}")
            return
        logging.info(f"Saving image {file.filename}")
        #resize image to 1024x1024
        image = Image.open(file)
        full_file_without_ext = file.filename.split('.')
        full_file_without_ext.pop()
        full_file_without_ext = '.'.join(full_file_without_ext)
        image.save(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}/{full_file_without_ext}.png")
        image.thumbnail((256,256))
        logging.info(f"Saving thumbnail {file.filename}")
        image.save(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}/{file.filename}.thumb.system.png")
        return file.filename

    def get_files(self, entry_id):
        files = []
        if os.path.exists(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}"):
            for file in os.listdir(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}"):
                files.append(file)
        return files
    def get_file_stream(self, entry_id, file_name):
        return open(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}/{file_name}", 'rb')
    
    def delete_file(self, entry_id, file_name):
        os.remove(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}/{file_name}")
        if len(os.listdir(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}")) == 0:
            os.rmdir(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}")
            
    def delete_all_files(self,entry_id):
        if not os.path.exists(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}"):
            return
        for file in os.listdir(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}"):
            os.remove(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}/{file}")
        os.rmdir(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}")