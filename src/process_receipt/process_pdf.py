import io
import pdfplumber
import requests

from src.s3 import upload_to_s3
from src.utils import ist_datetime_current

def extract_text_from_pdf_binary(pdf_binary):
    text = ""
    with pdfplumber.open(io.BytesIO(pdf_binary)) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def pdf2png(id:int,pdf_binary):
    url="converter.beaglenetwork.com/pdf2png"
    response = requests.post(url, files={"file": pdf_binary})
    if response.status_code == 200:
        print("Conversion successful!")
        # You can save or process the converted image here
        with open("converted_image.png", "wb") as f:
            binary_image_data=response.content
            filename=f"{id}.png"
            image_path="processed_images/"+filename
            image_link='https://beaglebucket.s3.amazonaws.com/'+image_path
            upload_to_s3(binary_image_data,image_path)