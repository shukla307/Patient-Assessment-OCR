import os
import re
import json
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path
from datetime import datetime
from database import store_in_database

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_path):
    """Enhanced image preprocessing"""
    try:
        img = cv2.imread(image_path)
        if img is None or img.size == 0:
            raise ValueError(f"Could not read image: {image_path}")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        thresh = cv2.adaptiveThreshold(enhanced, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 31, 6)
        return thresh
    except Exception as e:
        print(f"Preprocessing error: {str(e)}")
        return None

def extract_text(image_path):
    """Text extraction with error handling"""
    try:
        if image_path.lower().endswith('.pdf'):
            images = convert_from_path(image_path)
            return '\n'.join([pytesseract.image_to_string(img) for img in images])
        else:
            processed_img = preprocess_image(image_path)
            if processed_img is not None and np.any(processed_img):
                return pytesseract.image_to_string(processed_img, config='--psm 6')
            return ""
    except Exception as e:
        print(f"Extraction error: {str(e)}")
        return ""

def parse_extracted_text(text):
    """Handle different medical report formats"""
    
    clean_text = re.sub(r'\s+', ' ', text).upper()
    
    data = {
      
        "patient_name": extract_field(clean_text, r'NAME:\s*([^\n]+?)\sADDRESS:'),
        
        
        "dob": extract_dob(clean_text),
        
        # Capture report date in various formats
        "date": extract_field(clean_text, 
            r'REPORT DATE:\s*([A-Z]+ \d{4}|\d{1,2}/\d{1,2}/\d{4})')
    }
    return data

def extract_dob(text):
    """Handle both date and age formats"""
 
    dob_date = extract_field(text, 
        r'DOB:\s*(\d{1,2}/\d{1,2}/\d{4}|[A-Z]+ \d{1,2}, \d{4})')
    if dob_date:
        return parse_date(dob_date)
    

    age = extract_field(text, r'DOB:\s*AGE\s*(\d+)')
    if age:
        return f"Age {age}"
    
    return None


def parse_date(date_str):
    """Handle non-standard date formats"""
  
    if re.search(r'MID \d{4}', date_str, re.IGNORECASE):
        year = re.search(r'\d{4}', date_str).group()
        return f"06/01/{year}"
    
    if re.search(r'EARLY \d{4}', date_str, re.IGNORECASE):
        year = re.search(r'\d{4}', date_str).group()
        return f"03/01/{year}"

    
    return None

def extract_field(text, pattern, group=1):
    """More flexible field extraction"""
    try:
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(group).strip() if match else None
    except:
        return None

def process_file(file_path):
    """Processing workflow"""
    try:
        print(f"\nProcessing {os.path.basename(file_path)}...")
        text = extract_text(file_path)
        
        if not text:
            print("No text extracted")
            return

        data = parse_extracted_text(text)
        
        output_path = os.path.join('output', f"result_{os.path.basename(file_path)}.json")
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"Saved results to {output_path}")

    except Exception as e:
        print(f"Processing error: {str(e)}")

if __name__ == "__main__":
    os.makedirs('output', exist_ok=True)
    for filename in os.listdir('data'):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')):
            process_file(os.path.join('data', filename))








