import fitz
from PIL import Image
import cv2
import numpy as np
import pytesseract
import os
from groq import Groq

pytesseract.pytesseract.tesseract_cmd = r'D:\Program FilesSft\Tesseract\tesseract.exe'
client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)
def pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

def preprocess_image(img):
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    coords = np.column_stack(np.where(binary > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = gray.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(rotated, -1, kernel)

    return sharpened

def extract_text_from_image(img):
    text = pytesseract.image_to_string(img)
    return text

def extract_text_from_pdf(pdf_path):
    images = pdf_to_images(pdf_path)
    full_text = ""
    for img in images:
        preprocessed_img = preprocess_image(img)
        text = extract_text_from_image(preprocessed_img)
        full_text += text + "\n"

    return full_text

def correct_extracted_text(text):
    response = client.chat.completions.create(
    messages = [
        {"role": "system", "content": "You are a very helpful and assistant that is proficient in helping correct OCR text.",
        "role": "user", "content": f"""The following is a poorly extracted text from a PDF, which mainly has character recognition errors. 
        The entire PDF's are in English language, so you can try to translate the text to English and use your best judgement for the correction.
        Do keep in mind that the only fields you will face are namely 'English' 'Physics' 'Chemistry' 'Mathematics' 'Computer Science' 'Bengali' 'Hindi' 'Biology', which could also be represented in some pdf's as 'BNGA' for Bengali, 'ENGS' for English, 'BIOS' for Biology, 'CHEM' for Chemistry, 'PHYS' for Physics, etc, and 'MATH' for Mathematics.
        Try to adhere strictly to the format of the OCR table (I mean if the table has short forms in the name of the subjects, then and only then give short forms as output).
        I want you to give more emphasis on the NAME of the student, UNIQUE ID/ROLL NUMBER of the student/REGISTRATION NUMBER of the student, and the marks of the subjects. 
        Also, I want you to understand what the OCR output is, and give me what you feel the correct subjects with their appropriate marks are, with respect to the OCR. 
        Keep the original structure.
        Only give me the name of the student, subject names with their corresponding marks. 
        Do double check the characters which might look similar to another character (like K and R, 4 and 8, R and H).
        Do NOT add your personal NOTE at the end of the text.
        Give me an expected error factor considering the text you got. If you received 1 character that needed changing, give me 1, and keep on incrementing per change.\n\n{text}"""}

    ],
    model="llama3-8b-8192"
    )        
    print(response)
    return response.choices[0].message.content

# Main process
pdf_path = r"C:\CERTIFICATES\1b7dcdc5-c945-4e4c-9782-183de85f711e.pdf"
extracted_text = extract_text_from_pdf(pdf_path)

corrected_text = correct_extracted_text(extracted_text)

# Save corrected text
base_name = os.path.splitext(os.path.basename(pdf_path))[0]
output_file_path = os.path.join(os.path.dirname(pdf_path), f"{base_name}_corrected.txt")

with open(output_file_path, 'w', encoding='utf-8') as file:
    file.write(corrected_text)

print(f"Corrected text has been saved to {output_file_path}")
