import cv2
import numpy as np
import fitz
from PIL import Image
import os
import io

def extract_signatures(pdf_path):
    doc = fitz.open(pdf_path)
    last_page = doc[-1]
    page_rect = last_page.rect
    page_width = page_rect.width
    page_height = page_rect.height
    
    zoom_matrix = fitz.Matrix(4.0, 4.0)
    
    company_rect = fitz.Rect(
        page_width * 0.02,
        page_height * 0.4,
        page_width * 0.48,
        page_height * 0.98
    )
    
    counterparty_rect = fitz.Rect(
        page_width * 0.52,
        page_height * 0.4,
        page_width * 0.98,
        page_height * 0.98
    )
    
    company_pix = last_page.get_pixmap(matrix=zoom_matrix, clip=company_rect)
    img_data = company_pix.tobytes("png")
    pil_img = Image.open(io.BytesIO(img_data))
    company_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    counterparty_pix = last_page.get_pixmap(matrix=zoom_matrix, clip=counterparty_rect)
    img_data = counterparty_pix.tobytes("png")
    pil_img = Image.open(io.BytesIO(img_data))
    counterparty_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    company_cleaned = clean_signature(company_img)
    counterparty_cleaned = clean_signature(counterparty_img)
    
    cv2.imwrite("company_signature.png", company_cleaned, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    cv2.imwrite("counterparty_signature.png", counterparty_cleaned, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    
    doc.close()
    return True

def trim_white_borders(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)

    # Find contours again on the trimmed region
    coords = cv2.findNonZero(thresh)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        img = img[y:y+h, x:x+w]
    return img


def clean_signature(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 15, 8
    )

    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        filtered_contours = [c for c in contours if cv2.contourArea(c) > 100]

        if filtered_contours:
            all_points = np.concatenate(filtered_contours)
            x, y, w, h = cv2.boundingRect(all_points)

            signature_region = img[y:y+h, x:x+w]

            if signature_region.size > 0:
                # Final trimming of any extra white borders
                signature_region = trim_white_borders(signature_region)
                enhanced = cv2.convertScaleAbs(signature_region, alpha=1.1, beta=5)
                return enhanced

    return img



def main():
    pdf_files = ["Demo.pdf", "sample_contract.pdf", "document.pdf"]
    pdf_file = None
    
    for file in pdf_files:
        if os.path.exists(file):
            pdf_file = file
            break
    
    if not pdf_file:
        print("No PDF found")
        return
    
    print(f"Processing: {pdf_file}")
    
    success = extract_signatures(pdf_file)
    
    if success:
        print("Generated files:")
        print("- company_signature.png")
        print("- counterparty_signature.png")

if __name__ == "__main__":
    main()
