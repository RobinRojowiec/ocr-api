"""

IDE: PyCharm
Project: ocr-api
Author: Robin
Filename: server.py
Date: 15.01.2020

"""
import os
from typing import List

import pytesseract
import uvicorn
import xmltodict
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from starlette.responses import PlainTextResponse

app = FastAPI()


class ExtractedWord(BaseModel):
    text: str = ""
    x1: int = 0
    y1: int = 0
    x2: int = 0
    y2: int = 0
    confidence: float = 0.0

    def set_values(self, text, x1, y1, x2, y2, confidence):
        self.text = text
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.confidence = confidence


class ExtractedSpan(BaseModel):
    text: str = ""
    x1: int = 0
    y1: int = 0
    x2: int = 0
    y2: int = 0
    words: List[ExtractedWord] = []

    def set_values(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def add_word(self, word):
        self.words.append(word)


class ExtractedPage(BaseModel):
    lang: str = "eng"
    spans: List[ExtractedSpan] = []

    def add_span(self, span):
        self.spans.append(span)


@app.get("/ocr-version")
def read_root():
    return pytesseract.get_tesseract_version()


def parse_bbox_args(args: str):
    args = args.split()

    if len(args) > 5:
        # x, y, x2, y2, conf
        return int(args[1]), int(args[2]), int(args[3]), int(args[4][:-1]), float(args[6]) / 100.0
    else:
        return int(args[1]), int(args[2]), int(args[3]), int(args[4])


def hocr_to_simple_json(hocr_dict: dict, lang: str):
    response = ExtractedPage()
    response.lang = lang

    page = hocr_dict['html']['body']['div']['div']
    if type(page) is not list:
        page = [page]
    for span in page:
        if type(span['p']) is not list:
            span['p'] = [span['p']]
        for span_area in span['p']:

            info = parse_bbox_args(span_area['@title'])
            span_area_item = ExtractedSpan()
            span_area_item.set_values(info[0], info[1], info[2], info[3])

            if type(span_area['span']) is not list:
                span_area['span'] = [span_area['span']]
            for span_word in span_area['span']:
                if '#text' in span_word['span']:
                    text = span_word['span']['#text']
                    info = parse_bbox_args(span_word['span']['@title'])
                    word = ExtractedWord()
                    word.set_values(text, info[0], info[1], info[2], info[3], info[4])

                    span_area_item.text += word.text + ' '
                    span_area_item.add_word(word)

            if len(span_area_item.words) > 0:
                span_area_item.text.strip()
                response.add_span(span_area_item)
    return response


@app.post("/api/extract", response_model=ExtractedPage, description="Extract text with positions from image")
def extract_text(file: UploadFile = File(...), lang: str = "eng", text_only: bool = False, custom_config: str = None):
    """
    :param file:
    :param lang: available: deu, eng
    :return:
    """
    filepath = "temp/" + file.filename
    with file.file:
        with open(filepath, "wb") as temp_file:
            temp_file.write(file.file.read())

    # preprocess_image(filepath)
    if custom_config is None:
        custom_config = '--oem 3'

    if text_only:
        output = bytes(pytesseract.image_to_string(filepath, lang=lang, config=custom_config), encoding="utf-8")
        response = PlainTextResponse(content=output)
    else:
        output = pytesseract.image_to_pdf_or_hocr(filepath, lang=lang, extension='hocr', config=custom_config)
        extracted = xmltodict.parse(output)
        response = hocr_to_simple_json(extracted, lang)

    os.remove(filepath)
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
