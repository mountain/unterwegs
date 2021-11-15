from io import BytesIO, StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from PyPDF2 import PdfFileWriter, PdfFileReader


def pdf2meta(content):
    with BytesIO(content) as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)

    return doc.info[0]


def pdf2txt(content):
    txt = StringIO()
    with BytesIO(content) as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, txt, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)

    return str(txt.getvalue())


def pdf_pages(content):
    with BytesIO() as out_file:
        with BytesIO(content) as in_file:
            pdf = PdfFileReader(in_file)
            for i in range(pdf.numPages):
                output = PdfFileWriter()
                output.addPage(pdf.getPage(i))
                output.write(out_file)
                yield i, out_file.getvalue()
