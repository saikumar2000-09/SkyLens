import os
from flask import Flask, redirect, request, render_template, send_from_directory 
from google.cloud import storage 

app = Flask(__name__) 
os.makedirs('files', exist_ok=True) 

bucket_name = 'skylens08'

storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

def upload_blob(bucket_name, file, destination_blob_name): 
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file) 

def sync_files():
    blobs = bucket.list_blobs()
    bucket_files = {blob.name for blob in blobs}
    local_files = set(os.listdir('./files'))
    for local_file in local_files:
        if local_file not in bucket_files:
            os.remove(os.path.join('./files', local_file))

@app.route('/') 
def index(): 
    sync_files()
    blobs = bucket.list_blobs()
    file_list = [blob.name for blob in blobs]
    
    return render_template('index.html', files=file_list) 

@app.route('/upload', methods=['POST']) 
def upload(): 
    file = request.files['form_file'] 
    filename = file.filename 
    file.save(os.path.join("./files", filename)) 
    file.seek(0) 
    upload_blob(bucket_name, file, filename) 
    return redirect('/') 

@app.route('/files/<filename>') 
def files(filename): 
    return send_from_directory('files', filename) 

if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))