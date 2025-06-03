import os
import pytesseract
from PIL import Image
import cv2
import numpy as np
import re
from django.conf import settings

# Try to import easyocr for enhanced OCR capabilities
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

class DocumentScanner:
    """Service for scanning and extracting text from documents"""
    
    @staticmethod
    def preprocess_image(image_path):
        """Preprocess the image for better OCR results"""
        # Read the image
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get black and white image
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        # Save the preprocessed image
        preprocessed_path = os.path.join(settings.MEDIA_ROOT, 'temp', 'preprocessed_' + os.path.basename(image_path))
        os.makedirs(os.path.dirname(preprocessed_path), exist_ok=True)
        cv2.imwrite(preprocessed_path, thresh)
        
        return preprocessed_path, img
    
    @staticmethod
    def extract_text(image_path):
        """Extract text from an image using OCR"""
        # Preprocess the image
        preprocessed_path, original_img = DocumentScanner.preprocess_image(image_path)
        
        # Try to use EasyOCR if available (better results)
        if EASYOCR_AVAILABLE:
            try:
                reader = easyocr.Reader(['en'])
                results = reader.readtext(preprocessed_path)
                text = '\n'.join([result[1] for result in results])
                return text
            except Exception as e:
                print(f"Error with EasyOCR: {e}, falling back to pytesseract")
                # Fall back to pytesseract if EasyOCR fails
        
        # Use pytesseract as fallback
        try:
            text = pytesseract.image_to_string(Image.open(preprocessed_path))
            return text
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
        finally:
            # Clean up the preprocessed image
            if os.path.exists(preprocessed_path):
                os.remove(preprocessed_path)
    
    @staticmethod
    def extract_passport_info(image_path):
        """Extract passport information from an image using advanced techniques"""
        text = DocumentScanner.extract_text(image_path)
        
        # Initialize passport info dictionary
        passport_info = {
            'passport_number': None,
            'full_name': None,
            'nationality': None,
            'date_of_birth': None,
            'expiry_date': None,
            'gender': None,
            'place_of_birth': None,
            'issue_date': None,
            'authority': None
        }
        
        # Extract passport number (various formats)
        passport_patterns = [
            r'[A-Z]\d{7,9}',  # Standard format
            r'Passport No[.:](\s*[A-Z0-9]+)',  # With label
            r'No\.?\s*([A-Z0-9]{7,10})',  # With No. prefix
            r'Document No\.?\s*([A-Z0-9]{7,10})'  # Document number
        ]
        
        for pattern in passport_patterns:
            match = re.search(pattern, text)
            if match:
                # If the pattern has a group, use it, otherwise use the whole match
                passport_info['passport_number'] = match.group(1) if len(match.groups()) > 0 else match.group(0)
                break
        
        # Extract full name
        name_patterns = [
            r'(?:Name|Full Name|Surname and given names)\s*[.:](\s*[A-Za-z\s]+)',
            r'(?:Given names|First name)\s*[.:](\s*[A-Za-z\s]+)',
            r'(?:Surname|Last name)\s*[.:](\s*[A-Za-z\s]+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.group(1).strip():
                passport_info['full_name'] = match.group(1).strip()
                break
        
        # Extract nationality
        nationality_patterns = [
            r'(?:Nationality|Nationalité)\s*[.:](\s*[A-Za-z\s]+)',
            r'(?:Country|Nation)\s*[.:](\s*[A-Za-z\s]+)'
        ]
        
        for pattern in nationality_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.group(1).strip():
                passport_info['nationality'] = match.group(1).strip()
                break
        
        # Extract date of birth
        dob_patterns = [
            r'(?:Date of Birth|Birth Date|DOB)\s*[.:](\s*\d{1,2}[\s./-]\d{1,2}[\s./-]\d{2,4})',
            r'(?:Born|Birth)\s*[.:](\s*\d{1,2}[\s./-]\d{1,2}[\s./-]\d{2,4})'
        ]
        
        for pattern in dob_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.group(1).strip():
                passport_info['date_of_birth'] = match.group(1).strip()
                break
        
        # Extract gender
        gender_patterns = [
            r'(?:Sex|Gender)\s*[.:](\s*[MF]\s*)',
            r'(?:Sex|Gender)\s*[.:](\s*(?:MALE|FEMALE)\s*)'
        ]
        
        for pattern in gender_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.group(1).strip():
                gender_value = match.group(1).strip().upper()
                if gender_value in ['M', 'MALE']:
                    passport_info['gender'] = 'Male'
                elif gender_value in ['F', 'FEMALE']:
                    passport_info['gender'] = 'Female'
                break
        
        # Extract expiry date
        expiry_patterns = [
            r'(?:Date of Expiry|Expiry Date|Expiration|Expires)\s*[.:](\s*\d{1,2}[\s./-]\d{1,2}[\s./-]\d{2,4})',
            r'(?:Valid until|Valid to)\s*[.:](\s*\d{1,2}[\s./-]\d{1,2}[\s./-]\d{2,4})'
        ]
        
        for pattern in expiry_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.group(1).strip():
                passport_info['expiry_date'] = match.group(1).strip()
                break
        
        return passport_info