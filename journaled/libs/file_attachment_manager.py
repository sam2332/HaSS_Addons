import os
from PIL import Image
class FileAttachmentManager:
    def __init__(self,app, user):
        self.user = user
        self.app = app
        if os.path.exists(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}") == False:
            os.makedirs(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}")

    def save_file(self, file, entry_id):
        if os.path.exists(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}") == False:
            os.makedirs(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}")

        #resize image to 1024x1024
        image = Image.open(file)
        image.thumbnail((1024,1024))
        image.save(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}/{file.filename}.thumb.system.jpg")
        file.save(f"{self.app.filesystem_paths['UPLOAD_FOLDER']}/{self.user}/{entry_id}/{file.filename}")
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