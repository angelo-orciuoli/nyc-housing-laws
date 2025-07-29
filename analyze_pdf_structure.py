#!/usr/bin/env python3
"""
Analyze the actual HMC PDF structure to identify all subchapters, articles, and sections
"""

import re
import pdfplumber

def analyze_pdf_structure(pdf_path):
    """Analyze the PDF to find all structural elements"""
    
    print("📖 Analyzing PDF structure...")
    
    # Patterns for different structural elements
    patterns = {
        'subchapter': [
            re.compile(r'SUBCHAPTER\s+(\d+|[IVX]+)\s*[-–—]\s*(.+?)(?=\n|$)', re.IGNORECASE),
            re.compile(r'SUB-CHAPTER\s+(\d+|[IVX]+)\s*[-–—]\s*(.+?)(?=\n|$)', re.IGNORECASE),
            re.compile(r'SUBCHAPTER\s+(\d+|[IVX]+)\s*[.:]?\s*(.+?)(?=\n|$)', re.IGNORECASE),
        ],
        'article': [
            re.compile(r'ARTICLE\s+(\d+|[IVX]+|[A-Z]+)\s*[-–—]\s*(.+?)(?=\n|$)', re.IGNORECASE),
            re.compile(r'ARTICLE\s+(\d+|[IVX]+|[A-Z]+)\s*[.:]?\s*(.+?)(?=\n|$)', re.IGNORECASE),
        ],
        'section': [
            re.compile(r'§\s*27-(\d{4})\s*[-–—]?\s*(.+?)(?=\n|$)', re.IGNORECASE),
            re.compile(r'Section\s+27-(\d{4})\s*[-–—]?\s*(.+?)(?=\n|$)', re.IGNORECASE),
            re.compile(r'27-(\d{4})\s*[-–—]\s*(.+?)(?=\n|$)', re.IGNORECASE),
        ]
    }
    
    structure = {
        'subchapters': [],
        'articles': [],
        'sections': [],
        'total_pages': 0
    }
    
    with pdfplumber.open(pdf_path) as pdf:
        structure['total_pages'] = len(pdf.pages)
        
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if not text:
                continue
                
            lines = text.split('\n')
            
            for line_num, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # Check for subchapters
                for pattern in patterns['subchapter']:
                    match = pattern.search(line)
                    if match:
                        structure['subchapters'].append({
                            'number': match.group(1),
                            'title': match.group(2).strip(),
                            'page': page_num,
                            'line': line,
                            'full_match': match.group(0)
                        })
                        print(f"📚 Found Subchapter {match.group(1)}: {match.group(2).strip()[:50]}... (page {page_num})")
                        break
                
                # Check for articles
                for pattern in patterns['article']:
                    match = pattern.search(line)
                    if match:
                        structure['articles'].append({
                            'number': match.group(1),
                            'title': match.group(2).strip(),
                            'page': page_num,
                            'line': line,
                            'full_match': match.group(0)
                        })
                        print(f"📖 Found Article {match.group(1)}: {match.group(2).strip()[:50]}... (page {page_num})")
                        break
                
                # Check for sections
                for pattern in patterns['section']:
                    match = pattern.search(line)
                    if match:
                        structure['sections'].append({
                            'number': match.group(1),
                            'title': match.group(2).strip() if match.group(2) else "",
                            'page': page_num,
                            'line': line,
                            'full_match': match.group(0)
                        })
                        break
    
    return structure

def print_structure_summary(structure):
    """Print a summary of the found structure"""
    print(f"\n📊 STRUCTURE ANALYSIS SUMMARY")
    print("=" * 50)
    print(f"Total pages: {structure['total_pages']}")
    print(f"Subchapters found: {len(structure['subchapters'])}")
    print(f"Articles found: {len(structure['articles'])}")
    print(f"Sections found: {len(structure['sections'])}")
    
    if structure['subchapters']:
        print(f"\n📚 SUBCHAPTERS ({len(structure['subchapters'])} found):")
        for i, sub in enumerate(structure['subchapters'], 1):
            print(f"  {i}. Subchapter {sub['number']}: {sub['title'][:60]}... (page {sub['page']})")
    
    if structure['articles']:
        print(f"\n📖 ARTICLES ({len(structure['articles'])} found):")
        for i, art in enumerate(structure['articles'][:10], 1):  # Show first 10
            print(f"  {i}. Article {art['number']}: {art['title'][:60]}... (page {art['page']})")
        if len(structure['articles']) > 10:
            print(f"  ... and {len(structure['articles']) - 10} more articles")
    
    if structure['sections']:
        print(f"\n📝 SECTIONS ({len(structure['sections'])} found):")
        for i, sec in enumerate(structure['sections'][:15], 1):  # Show first 15
            print(f"  {i}. § 27-{sec['number']}: {sec['title'][:50]}... (page {sec['page']})")
        if len(structure['sections']) > 15:
            print(f"  ... and {len(structure['sections']) - 15} more sections")

def find_table_of_contents(pdf_path):
    """Try to find and extract table of contents"""
    print("\n🔍 Looking for Table of Contents...")
    
    toc_patterns = [
        re.compile(r'table\s+of\s+contents', re.IGNORECASE),
        re.compile(r'contents', re.IGNORECASE),
        re.compile(r'index', re.IGNORECASE),
    ]
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages[:10], 1):  # Check first 10 pages
            text = page.extract_text()
            if not text:
                continue
            
            for pattern in toc_patterns:
                if pattern.search(text):
                    print(f"📋 Possible TOC found on page {page_num}")
                    lines = text.split('\n')[:20]  # Show first 20 lines
                    for line in lines:
                        if line.strip():
                            print(f"    {line.strip()}")
                    return page_num
    
    print("❌ No clear table of contents found")
    return None

if __name__ == "__main__":
    pdf_path = "HousingMaintenanceCode.pdf"
    
    # Find table of contents
    find_table_of_contents(pdf_path)
    
    # Analyze structure
    structure = analyze_pdf_structure(pdf_path)
    
    # Print summary
    print_structure_summary(structure)
    
    # Save detailed results
    import json
    with open('pdf_structure_analysis.json', 'w') as f:
        json.dump(structure, f, indent=2)
    
    print(f"\n💾 Detailed analysis saved to 'pdf_structure_analysis.json'")