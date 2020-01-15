"""

IDE: PyCharm
Project: ocr-api
Author: Robin
Filename: server.py
Date: 15.01.2020

"""
import json
import pytesseract
import uvicorn
import xmltodict
from fastapi import FastAPI, File, UploadFile
from starlette.responses import Response

app = FastAPI()


@app.get("/ocr-version")
def read_root():
    return pytesseract.get_tesseract_version()


@app.post("/api/extract/{mode}")
def extract_text(mode: str, file: UploadFile = File(...)):
    filepath = "temp/" + file.filename
    with file.file:
        with open(filepath, "wb") as temp_file:
            temp_file.write(file.file.read())

    if mode == "text":
        text = pytesseract.image_to_string(filepath)
        return Response(content=text, media_type="plain/text")
    elif mode == "text_with_positions":
        content = pytesseract.image_to_pdf_or_hocr(filepath, extension='hocr')
        content = json.dumps(xmltodict.parse(content))
        return Response(content=content, media_type="application/json")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
