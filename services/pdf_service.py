# import os
# import fitz
# from fastapi import HTTPException, status
# from typing import Tuple
# import magic

# class PDFService:
#     MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
#     ALLOWED_MIME_TYPES = ['application/pdf']
    
#     @staticmethod
#     def validate_pdf(file_path: str) -> Tuple[bool, str]:
#         """
#         Validate PDF file
#         Returns: (is_valid, error_message)
#         """
#         # Check if file exists
#         if not os.path.exists(file_path):
#             return False, "File not found"
        
#         # Check file size
#         file_size = os.path.getsize(file_path)
#         if file_size > PDFService.MAX_FILE_SIZE:
#             return False, f"File size ({file_size/1024/1024:.2f}MB) exceeds 10MB limit"
        
#         # Basic PDF validation - try to open it
#         try:
#             with fitz.open(file_path) as doc:
#                 if not doc:
#                     return False, "Invalid PDF file - cannot be opened"
#                 # Optional: Check if PDF is encrypted/password protected
#                 if doc.needs_pass:
#                     return False, "PDF is password protected"
#         except Exception as e:
#             return False, f"Invalid PDF file: {str(e)}"
        
#         return True, "Valid PDF"
    
#     @staticmethod
#     def extract_text_from_pdf(file_path: str) -> str:
#         """
#         Extract text from PDF using PyMuPDF
#         """
#         try:
#             text = ""
#             with fitz.open(file_path) as doc:
#                 for page in doc:
#                     text += page.get_text()
#             return text.strip()
#         except Exception as e:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Failed to extract text from PDF: {str(e)}"
#             )


import os
import fitz  # PyMuPDF
from fastapi import HTTPException, status
from typing import Tuple

class PDFService:
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_MIME_TYPES = ['application/pdf']
    
    @staticmethod
    def validate_pdf(file_path: str) -> Tuple[bool, str]:
        """
        Validate PDF file
        Returns: (is_valid, error_message)
        """
        # Check if file exists
        if not os.path.exists(file_path):
            return False, "File not found"
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > PDFService.MAX_FILE_SIZE:
            return False, f"File size ({file_size/1024/1024:.2f}MB) exceeds 10MB limit"
        
        # Validate file extension
        if not file_path.lower().endswith('.pdf'):
            return False, "File must have .pdf extension"
        
        # Basic PDF validation - try to open it with PyMuPDF
        try:
            with fitz.open(file_path) as doc:
                if not doc:
                    return False, "Invalid PDF file - cannot be opened"
                # Check if PDF is encrypted/password protected
                if doc.needs_pass:
                    return False, "PDF is password protected"
                # Check if PDF has at least one page
                if doc.page_count == 0:
                    return False, "PDF file is empty"
        except Exception as e:
            return False, f"Invalid PDF file: {str(e)}"
        
        return True, "Valid PDF"
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """
        Extract text from PDF using PyMuPDF (fitz)
        """
        try:
            text = ""
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
            
            # Return stripped text or error if empty
            text = text.strip()
            if not text:
                raise ValueError("No text content found in PDF")
            
            return text
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to extract text from PDF: {str(e)}"
            )