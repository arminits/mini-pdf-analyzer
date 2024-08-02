import sys
import re
import os
from PyPDF2 import PdfReader
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO
from pdf2image import convert_from_path
from pyzbar.pyzbar import decode
from PIL import Image


def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        resource_manager = PDFResourceManager()
        stream = StringIO()
        laparams = LAParams()
        device = TextConverter(resource_manager, stream, laparams=laparams)
        interpreter = PDFPageInterpreter(resource_manager, device)

        with open(pdf_path, 'rb') as pdf_file:
            for page in PDFPage.get_pages(pdf_file, check_extractable=True):
                interpreter.process_page(page)
            text = stream.getvalue()

    except Exception as e:
        print("Error:", str(e))

    return text


def extract_metadata_from_pdf(pdf_path):
    metadata = {}
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            metadata['Title'] = pdf_reader.metadata.get('/Title')
            metadata['Author'] = pdf_reader.metadata.get('/Author')
            metadata['Subject'] = pdf_reader.metadata.get('/Subject')
            metadata['Producer'] = pdf_reader.metadata.get('/Producer')
            metadata['Created'] = pdf_reader.metadata.get('/CreationDate')
            metadata['Modified'] = pdf_reader.metadata.get('/ModDate')
            metadata['Number of Pages'] = len(pdf_reader.pages)

    except Exception as e:
        print("Error:", str(e))

    return metadata


def extract_images_from_pdf(pdf_path):
    images = []
    try:
        images = convert_from_path(pdf_path)
    except Exception as e:
        print("Error extracting images:", str(e))
    return images


def detect_qr_codes(images):
    for image in images:
        decoded_objects = decode(image)
        for obj in decoded_objects:
            if obj.type == 'QRCODE':
                print(f"QR-Code Link: {obj.data.decode('utf-8')}")


def analyze_pdf_file(pdf_path):
    try:

        print("Metadata:")
        metadata = extract_metadata_from_pdf(pdf_path)
        for key, value in metadata.items():
            print(f"{key}: {value}")
        print()


        print("Text Analysis:")
        text = extract_text_from_pdf(pdf_path)
        print("Extracted Text:")
        print(text)
        print()


        print("QR Code Detection:")
        images = extract_images_from_pdf(pdf_path)
        detect_qr_codes(images)
        print()


        print("Links Analysis:")
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        if urls:
            print("URLs found:")
            for url in urls:
                print(url)
        else:
            print("No direct URLs in the text were found.")
        print()

    except Exception as e:
        print("Error:", str(e))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_pdf.py <pdf_file_path>")
        sys.exit(1)

    pdf_file_path = sys.argv[1]
    analyze_pdf_file(pdf_file_path)
