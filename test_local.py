"""
Local test script to verify PDF to TIFF conversion works
This runs the conversion logic without needing the Azure Functions runtime
"""
import io
import fitz  # PyMuPDF
from PIL import Image

def convert_pdf_to_tiff(pdf_path, output_path):
    """Convert a PDF file to TIFF and save it locally"""
    try:
        # Read the PDF file
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()

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

        # Save as TIFF
        if len(images) > 1:
            images[0].save(
                output_path,
                format='TIFF',
                save_all=True,
                append_images=images[1:],
                compression='tiff_deflate'
            )
        else:
            images[0].save(output_path, format='TIFF', compression='tiff_deflate')

        print(f"✓ Successfully converted {len(images)} page(s) to TIFF")
        print(f"✓ Output saved to: {output_path}")
        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python test_local.py <path_to_pdf>")
        print("Example: python test_local.py sample.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = "output.tiff"

    convert_pdf_to_tiff(pdf_path, output_path)
