#!/usr/bin/env python3
"""
Examine sample pages from the PDF to understand the actual structure format
"""

import pdfplumber

def examine_sample_pages(pdf_path, pages_to_check=[1, 2, 3, 10, 20, 30, 50, 80, 100]):
    """Examine specific pages to understand formatting"""
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num in pages_to_check:
            if page_num <= len(pdf.pages):
                print(f"\n{'='*60}")
                print(f"PAGE {page_num}")
                print(f"{'='*60}")
                
                page = pdf.pages[page_num - 1]  # 0-indexed
                text = page.extract_text()
                
                if text:
                    lines = text.split('\n')
                    for i, line in enumerate(lines[:30], 1):  # Show first 30 lines
                        print(f"{i:2d}: {line}")
                else:
                    print("No text found on this page")

if __name__ == "__main__":
    examine_sample_pages("HousingMaintenanceCode.pdf")