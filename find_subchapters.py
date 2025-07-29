#!/usr/bin/env python3
"""
Search for all subchapter headings in the PDF
"""

import pdfplumber
import re

def find_all_subchapters(pdf_path):
    """Search through all pages for subchapter headings"""
    
    subchapter_pattern = re.compile(r'^SUBCHAPTER\s+(\d+|[IVX]+)\s*$', re.IGNORECASE)
    
    subchapters = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if not text:
                continue
                
            lines = text.split('\n')
            
            for line_num, line in enumerate(lines):
                line = line.strip()
                
                # Check for exact subchapter heading
                match = subchapter_pattern.match(line)
                if match:
                    # Get the next line for the title
                    title = ""
                    if line_num + 1 < len(lines):
                        title = lines[line_num + 1].strip()
                    
                    subchapters.append({
                        'number': match.group(1),
                        'title': title,
                        'page': page_num,
                        'line': line,
                        'context': lines[max(0, line_num-2):line_num+5]  # Show context
                    })
                    
                    print(f"📚 Found SUBCHAPTER {match.group(1)} on page {page_num}")
                    print(f"    Title: {title}")
                    print(f"    Context:")
                    for i, ctx_line in enumerate(lines[max(0, line_num-2):line_num+5]):
                        marker = ">>> " if i == min(2, line_num) else "    "
                        print(f"    {marker}{ctx_line}")
                    print()
    
    return subchapters

def search_for_likely_subchapters(pdf_path):
    """Search for patterns that might be subchapter headings"""
    
    patterns = [
        re.compile(r'SUBCHAPTER\s+(\d+)', re.IGNORECASE),
        re.compile(r'SUB-CHAPTER\s+(\d+)', re.IGNORECASE),
        re.compile(r'CHAPTER\s+(\d+)', re.IGNORECASE),
        re.compile(r'PART\s+(\d+)', re.IGNORECASE),
    ]
    
    found_patterns = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if not text:
                continue
                
            lines = text.split('\n')
            
            for line_num, line in enumerate(lines):
                line_clean = line.strip()
                
                for pattern in patterns:
                    matches = pattern.findall(line_clean)
                    if matches:
                        found_patterns.append({
                            'pattern': pattern.pattern,
                            'matches': matches,
                            'page': page_num,
                            'line': line_clean,
                            'context': lines[max(0, line_num-1):line_num+3]
                        })
    
    return found_patterns

if __name__ == "__main__":
    pdf_path = "HousingMaintenanceCode.pdf"
    
    print("🔍 Searching for exact SUBCHAPTER headings...")
    subchapters = find_all_subchapters(pdf_path)
    
    print(f"\n📊 Found {len(subchapters)} exact subchapter headings")
    
    if len(subchapters) < 5:
        print("\n🔍 Searching for other potential patterns...")
        patterns = search_for_likely_subchapters(pdf_path)
        
        print(f"\n📊 Found {len(patterns)} potential patterns:")
        for pattern in patterns[:20]:  # Show first 20
            print(f"  Page {pattern['page']}: {pattern['line']}")
    
    print(f"\n✅ Analysis complete. Found {len(subchapters)} confirmed subchapters.")