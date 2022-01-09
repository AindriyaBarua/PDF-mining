# -*- coding: utf-8 -*-

from os import listdir
from os.path import join
import time
import pandas
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfparser import PDFSyntaxError
import subprocess


import io

from multiprocessing import Pool


PDFS_PATH = path = "PDF_files"
PDF_EXT = ".pdf"
FAILED = []
PAGEWISE_FOLDER = "pagewise_folder"


def page_wise_extract(pdf_file, path):
    corrupt = False
    pages = []
    '''
    read_pdf = PyPDF2.PdfFileReader(join(path, pdf_file))
    number_of_pages = read_pdf.getNumPages()
    for page_number in range(number_of_pages):
        page = read_pdf.getPage(page_number).extractText()
        pages.append(page)
    '''
    print(">>>>", pdf_file)
    fp = open(join(path, pdf_file), 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = io.BytesIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    try:
        for pageNumber, page in enumerate(PDFPage.get_pages(fp)):
            interpreter.process_page(page)
            text = retstr.getvalue()
            text = text.decode('utf-8', errors='ignore').strip()
            pages.append(text)
            retstr.truncate(0)
            retstr.seek(0)
        print("DONE:", file)
    except PDFSyntaxError:
        print("CORRUPT:", file)
        corrupt = True
        FAILED.append(file)

    return pages, corrupt


def get_filenames(folder_path, ext):
    files = [f for f in listdir(folder_path) if f.endswith(ext)]
    return files


def main(file, PDFS_PATH):
    pages, corrupt = page_wise_extract(file, PDFS_PATH)
    if not corrupt:
        # fp = open(join(PAGEWISE, file.strip(".pdf")+".txt"), "w")
        print(len(pages))
        filepath = join(PAGEWISE_FOLDER, file.strip(".pdf") + ".csv")
        try:
            df = pandas.DataFrame(data={"page_text": pages})
            df.to_csv(filepath, sep=',', encoding='utf-8', escapechar='\\')
        except:
            FAILED.append(file)


if __name__ == '__main__':
    files = get_filenames(PDFS_PATH, PDF_EXT)
    print (files)
    done_files = get_filenames("pagewise_folder", "csv")
    print(done_files)
    start = time.time()
    for file in files:
        if file.strip(".pdf")+".csv" not in done_files:
            main(file, PDFS_PATH)

    end = time.time()
    print("Time taken: ", end - start)
    with open('corrupted_files.txt', 'w') as f:
        for item in FAILED:
            f.write("%s\n" % item)
