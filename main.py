from flask import Flask,flash, request, url_for, Flask,redirect
from flask_pymongo import PyMongo
from flask import Flask, render_template, request
from flask import request, abort, make_response
from base64 import b64encode
from forms import UploadForm
import os
from werkzeug.utils import secure_filename
import pymongo
import platform
import socket
import subprocess
import shlex
import re
import requests
import datetime as date
import datetime
import random, threading, webbrowser
import smtplib
import hashlib as hasher
from flask import send_from_directory
from werkzeug.middleware.shared_data import SharedDataMiddleware
import cv2

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["testdb"]
mycol = mydb["Encrypt_data"]

UPLOAD_FOLDER = 'F:\\SnakeChain_Enc\\Data'
ALLOWED_EXTENSIONS = {'mp4'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY']='fshfhjdchbDAHC234GFGJHJ'

app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  app.config['UPLOAD_FOLDER']
})


class block:
    def __init__(self,index,timestamp,hash_):
        self.index = index
        self.timestamp = timestamp
        self.hash_=hash_
        

class Block:
  def __init__(self, index, timestamp, data, previous_hash):
    self.index = index
    self.timestamp = timestamp
    self.data = data
    self.previous_hash = previous_hash
    self.hash = self.hash_block()
  
  def hash_block(self):
    sha = hasher.sha256()
    sha.update((str(self.index) + 
               str(self.timestamp) + 
               str(self.data) + 
               str(self.previous_hash)).encode("utf8"))
    return sha.hexdigest()

def create_genesis_block():
  # Manually construct a block with
  # index zero and arbitrary previous hash
  return Block(0, date.datetime.now(), "Genesis Block", "0")

def next_block(last_block,image):
  this_index = last_block.index + 1
  this_timestamp = date.datetime.now()
  this_data = str(image) + str(this_index)
  this_hash = last_block.hash
  return Block(this_index, this_timestamp, this_data, this_hash)

def getFrame(sec,path):
    vidcap = cv2.VideoCapture(path)
    vidcap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
    hasFrames,image = vidcap.read()
    if hasFrames:
        cv2.imwrite("G:/Images/frame "+str(sec)+" sec.jpg", image)     # save frame as JPG file
    return hasFrames

def FrameCapture(path):
    sec = 0
    frameRate = 0.5
    success = getFrame(sec,path)
    while success:
        sec = sec + frameRate
        sec = round(sec, 2)
        success = getFrame(sec,path)

def find_images():
    l=[]
    for filename in os.listdir("G:\\Images\\"):
        if filename.endswith(".jpg"):
            l.append("G:\\Images\\"+filename)
            continue
        else:
            continue
    return l

def encrypt(l):
    msg=''
    blockchain = [create_genesis_block()]
    previous_block = blockchain[0]
    for files in l:
        image=cv2.imread(files)
        block_to_add = next_block(previous_block,image)
        blockchain.append(block_to_add)
        previous_block = block_to_add
##        msg+="Block #{} has been added to the blockchain!".format(block_to_add.index)
##        msg+="================================================================="
##        msg+="Index: {}\n".format(block_to_add.index)
##        msg+="Timestamp: {}\n".format(block_to_add.timestamp)
##        msg+="Data: {}\n".format(block_to_add.data)
##        msg+="Encrypted Output:\n"
##        msg+="Hash: {}\n".format(block_to_add.hash)
        d={"index":block_to_add.index,"timestamp":block_to_add.timestamp,"hash_key":block_to_add.hash}
        mycol.insert_one(d)
    return "successful"




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

@app.route('/encrypt/<filename>')
def processing(filename):
    file=UPLOAD_FOLDER+'\\'+filename
    print(file)
    FrameCapture(file)
    l=find_images()
    msg=encrypt(l)
    print(msg)
    return redirect(url_for('output'))

@app.route('/output')
def output():
    l=[]
    for x in mycol.find():
        bl=block(x['index'],x['timestamp'],x['hash_key'])
        l.append(bl)
    return render_template('output.html',l=l)
                 
        
    

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #return redirect(url_for('uploaded_file',
                                    #filename=filename))
            return redirect(url_for('processing',
                                    filename=filename))
    return '''
   <!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/css/bootstrap.min.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/js/bootstrap.min.js"></script>
<style>
.m
{
padding-left:30em;
padding-right:30em;
padding-top:10em;
}
</style>
</head>
<body>
<br>
<br>
<br>
<center>
<div class=m>
<h3>Video Encrypting using SnakeChain</h3>
<br>
<form method="POST"  class="form-group row" enctype="multipart/form-data">
<div class="col-xs-6"><input class="form-control" type=file name=file></div>
<div class="col-xs-6"><input class="btn btn-primary" type=submit value=Upload></div>
</form>
</div>
</center>
</body>
</html>
    '''
if __name__=='__main__':
    app.run(debug=True)
    
