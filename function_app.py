import azure.functions as func
import logging
import io
import fitz  # PyMuPDF
from PIL import Image

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="convertpdf2tiff")
def convertpdf2tiff(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('PDF to TIFF conversion function triggered.')

    try:
        # Get the PDF file from the request
        pdf_file = req.files.get('file')

        if not pdf_file:
            return func.HttpResponse(
                "Please upload a PDF file using 'file' parameter in multipart/form-data.",
                status_code=400
            )

        # Read PDF content
        pdf_bytes = pdf_file.read()

        # Open PDF with PyMuPDF
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

        # Convert each page to an image
        images = []
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            # Render page to an image (pixmap) at 300 DPI for good quality
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
            # Convert pixmap to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)

        pdf_document.close()

        # Create a BytesIO object to store the TIFF
        tiff_io = io.BytesIO()

        # If multi-page PDF, save as multi-page TIFF
        if len(images) > 1:
            images[0].save(
                tiff_io,
                format='TIFF',
                save_all=True,
                append_images=images[1:],
                compression='tiff_deflate'
            )
        else:
            # Single page PDF
            images[0].save(tiff_io, format='TIFF', compression='tiff_deflate')

        tiff_io.seek(0)
        tiff_bytes = tiff_io.getvalue()

        logging.info(f'Successfully converted PDF with {len(images)} page(s) to TIFF.')

        # Return the TIFF file
        return func.HttpResponse(
            body=tiff_bytes,
            mimetype='image/tiff',
            status_code=200,
            headers={
                'Content-Disposition': 'attachment; filename="converted.tiff"'
            }
        )

    except Exception as e:
        logging.error(f'Error converting PDF to TIFF: {str(e)}')
        return func.HttpResponse(
            f"Error converting PDF to TIFF: {str(e)}",
            status_code=500
        )