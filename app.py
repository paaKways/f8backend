import os

import PyPDF2 
import textract
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from flask import Flask, flash, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from flask import send_from_directory

UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTS = {'txt','pdf', 'jpg','png'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read(filename):
    #open allows you to read the file
    pdfFileObj = open(filename,'rb')

    #The pdfReader variable is a readable object that will be parsed
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    #discerning the number of pages will allow us to parse through all #the pages
    num_pages = pdfReader.numPages
    count = 0
    text = ""

    #The while loop will read each page
    while count < num_pages:
        pageObj = pdfReader.getPage(count)
        count +=1
        text += pageObj.extractText()

    #This if statement exists to check if the above library returned #words. It's done because PyPDF2 cannot read scanned files.
    if text != "":
        text = text

    #If the above returns as False, we run the OCR library textract to #convert scanned/image based PDF files into text
    else:
        text = textract.process(fileurl, method='tesseract', language='eng')
        # Now we have a text variable which contains all the text derived #from our PDF file. Type print(text) to see what it contains. It #likely contains a lot of spaces, possibly junk such as '\n' etc.
        # Now, we will clean our text variable, and return it as a list of keywords.

        #The word_tokenize() function will break our text phrases into #individual words
        tokens = word_tokenize(text)
        #we'll create a new list which contains punctuation we wish to clean
        punctuations = ['(',')',';',':','[',']',',']
        #We initialize the stopwords variable which is a list of words like #"The", "I", "and", etc. that don't hold much value as keywords
        stop_words = stopwords.words('english')
        #We create a list comprehension which only returns a list of words #that are NOT IN stop_words and NOT IN punctuations.
        keywords = [word for word in tokens if not word in stop_words and not word in punctuations]
        return keywords

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

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
            
            uploaded_file_url = url_for('uploaded_file',
                                    filename=filename)
            
            keywords = read(file)
            results = {'uploaded_file_url': uploaded_file_url, 'keywords': keywords}
            
            return jsonify(results)
            #return redirect(uploaded_file_url)

    else: return '<form action="/" method="POST" ><input type="file" name="file" /></form>';

is_prod = os.environ.get('dev', 'False')

if __name__ == '__main__':
    if is_prod == 'True': app.run(port = 8000, debug=True)
