#!/usr/bin/env python3
"""
NYC Housing Maintenance Code PDF Chunker
A practical implementation for chunking the HMC PDF for LLM chatbot use.
"""

import re
import json
import os
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict

@dataclass
class ChunkMetadata:
    """Metadata for each chunk"""
    chunk_id: str
    title: str
    hierarchy: Dict[str, str]
    page_numbers: List[int]
    cross_references: List[str]
    keywords: List[str]
    chunk_type: str  # 'subchapter', 'article', 'section'
    parent_chunks: List[str]
    content_length: int
    token_estimate: int

class HMCChunker:
    """Main class for chunking the NYC Housing Maintenance Code PDF"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.raw_text = ""
        self.chunks = []
        self.structure_map = {}
        self.cross_references = {}
        
        # Regex patterns for identifying structure
        self.patterns = {
            'subchapter': re.compile(r'^SUBCHAPTER\s+(\d+|[IVX]+)\s*$', re.IGNORECASE),
            'article': re.compile(r'^ARTICLE\s+(\d+|[A-Z]+)\s*$', re.IGNORECASE),
            'section': re.compile(r'^§27–(\d{4})\s+(.+?)(?:\.|$)', re.IGNORECASE),
            'cross_ref': re.compile(r'§?\s*27-(\d{4})', re.IGNORECASE),
            'page_break': re.compile(r'\f|\n\s*\d+\s*\n'),
        }
    
    def extract_text_basic(self) -> str:
        """
        Basic text extraction method that can be enhanced with proper PDF libraries.
        For now, this is a placeholder that would need actual PDF processing.
        """
        print("⚠️  Note: This implementation requires PDF processing libraries.")
        print("   Install with: pip install PyPDF2 pdfplumber")
        print("   For now, you'll need to manually extract text from the PDF.")
        
        # Placeholder - in real implementation, this would extract PDF text
        sample_text = """
        SUBCHAPTER 1 - GENERAL PROVISIONS
        
        ARTICLE 1 - DEFINITIONS
        
        § 27-2004 - Definitions
        When used in this subchapter, the following terms shall have the meanings hereinafter set forth:
        
        DWELLING. Any building or structure or portion thereof which is occupied in whole or in part as the home, residence or sleeping place of one or more human beings.
        
        OWNER. The person or entity having legal title to premises; a mortgagee or vendee in possession; a trustee; a receiver; or any other person, firm or corporation directly or indirectly in control of a dwelling or dwelling unit.
        
        § 27-2005 - Scope and application
        The provisions of this code shall apply to all dwellings, as defined in section 27-2004, except as otherwise specifically provided.
        
        ARTICLE 2 - ADMINISTRATION AND ENFORCEMENT
        
        § 27-2115 - Powers and duties of the department
        The department shall have the power and duty to enforce the provisions of this code.
        """
        
        return sample_text
    
    def extract_text_with_pypdf2(self) -> str:
        """Extract text using PyPDF2 library"""
        try:
            import PyPDF2
            text = ""
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += f"\n--- PAGE {page_num + 1} ---\n{page_text}\n"
            return text
        except ImportError:
            return self.extract_text_basic()
    
    def extract_text_with_pdfplumber(self) -> str:
        """Extract text using pdfplumber library (preferred for layout preservation)"""
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- PAGE {page_num + 1} ---\n{page_text}\n"
            return text
        except ImportError:
            return self.extract_text_with_pypdf2()
    
    def extract_text(self) -> str:
        """Main text extraction method - tries best available option"""
        return self.extract_text_with_pdfplumber()
    
    def identify_structure(self, text: str) -> Dict[str, List[Dict]]:
        """Identify the hierarchical structure of the document"""
        structure = {
            'subchapters': [],
            'articles': [],
            'sections': []
        }
        
        lines = text.split('\n')
        current_page = 1
        
        for i, line in enumerate(lines):
            # Track page numbers
            if '--- PAGE' in line:
                try:
                    current_page = int(re.search(r'PAGE (\d+)', line).group(1))
                except:
                    pass
                continue
            
            # Find subchapters
            subchapter_match = self.patterns['subchapter'].search(line)
            if subchapter_match:
                # Title is on the next line
                title = ""
                if i + 1 < len(lines):
                    title = lines[i + 1].strip()
                structure['subchapters'].append({
                    'number': subchapter_match.group(1),
                    'title': title,
                    'line_number': i,
                    'page': current_page
                })
            
            # Find articles
            article_match = self.patterns['article'].search(line)
            if article_match:
                # Title is on the next line
                title = ""
                if i + 1 < len(lines):
                    title = lines[i + 1].strip()
                structure['articles'].append({
                    'number': article_match.group(1),
                    'title': title,
                    'line_number': i,
                    'page': current_page
                })
            
            # Find sections
            section_match = self.patterns['section'].search(line)
            if section_match:
                structure['sections'].append({
                    'number': section_match.group(1),
                    'title': section_match.group(2).strip() if len(section_match.groups()) > 1 and section_match.group(2) else "",
                    'line_number': i,
                    'page': current_page
                })
        
        return structure
    
    def extract_cross_references(self, text: str) -> Dict[str, List[str]]:
        """Extract cross-references between sections"""
        references = {}
        sections = self.patterns['section'].findall(text)
        
        for section_num, _ in sections:
            section_text = self.get_section_text(text, section_num)
            refs = self.patterns['cross_ref'].findall(section_text)
            # Remove self-references
            refs = [ref for ref in refs if ref != section_num]
            if refs:
                references[section_num] = list(set(refs))
        
        return references
    
    def get_section_text(self, text: str, section_num: str) -> str:
        """Extract the full text of a specific section"""
        pattern = re.compile(
            rf'§?\s*27-{section_num}\s*[-–]?\s*(.+?)(?=\n\s*§?\s*27-\d{{4}}|\n\s*ARTICLE|\n\s*SUBCHAPTER|$)',
            re.DOTALL | re.IGNORECASE
        )
        match = pattern.search(text)
        return match.group(0) if match else ""
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (1 token ≈ 4 characters for English)"""
        return len(text) // 4
    
    def create_chunks(self, text: str, structure: Dict) -> List[ChunkMetadata]:
        """Create chunks based on the identified structure"""
        chunks = []
        lines = text.split('\n')
        
        # Create section-level chunks (most granular)
        for section in structure['sections']:
            section_num = section['number']
            section_text = self.get_section_text(text, section_num)
            
            if section_text.strip():
                # Extract keywords from title and content
                keywords = self.extract_keywords(section['title'] + " " + section_text)
                
                chunk = ChunkMetadata(
                    chunk_id=f"section_27_{section_num}",
                    title=f"§ 27-{section_num} - {section['title']}",
                    hierarchy={
                        'title': '27',
                        'chapter': '2',
                        'section': f"27-{section_num}"
                    },
                    page_numbers=[section['page']],
                    cross_references=self.cross_references.get(section_num, []),
                    keywords=keywords,
                    chunk_type='section',
                    parent_chunks=[],
                    content_length=len(section_text),
                    token_estimate=self.estimate_tokens(section_text)
                )
                chunks.append(chunk)
        
        # Create article-level chunks (medium granularity)
        for i, article in enumerate(structure['articles']):
            start_line = article['line_number']
            end_line = structure['articles'][i + 1]['line_number'] if i + 1 < len(structure['articles']) else len(lines)
            
            article_text = '\n'.join(lines[start_line:end_line])
            keywords = self.extract_keywords(article['title'] + " " + article_text)
            
            chunk = ChunkMetadata(
                chunk_id=f"article_{article['number']}",
                title=f"Article {article['number']} - {article['title']}",
                hierarchy={
                    'title': '27',
                    'chapter': '2',
                    'article': article['number']
                },
                page_numbers=[article['page']],
                cross_references=[],
                keywords=keywords,
                chunk_type='article',
                parent_chunks=[],
                content_length=len(article_text),
                token_estimate=self.estimate_tokens(article_text)
            )
            chunks.append(chunk)
        
        # Create subchapter-level chunks (highest level)
        for i, subchapter in enumerate(structure['subchapters']):
            start_line = subchapter['line_number']
            end_line = structure['subchapters'][i + 1]['line_number'] if i + 1 < len(structure['subchapters']) else len(lines)
            
            subchapter_text = '\n'.join(lines[start_line:end_line])
            keywords = self.extract_keywords(subchapter['title'] + " " + subchapter_text)
            
            chunk = ChunkMetadata(
                chunk_id=f"subchapter_{subchapter['number']}",
                title=f"Subchapter {subchapter['number']} - {subchapter['title']}",
                hierarchy={
                    'title': '27',
                    'chapter': '2',
                    'subchapter': subchapter['number']
                },
                page_numbers=[subchapter['page']],
                cross_references=[],
                keywords=keywords,
                chunk_type='subchapter',
                parent_chunks=[],
                content_length=len(subchapter_text),
                token_estimate=self.estimate_tokens(subchapter_text)
            )
            chunks.append(chunk)
        
        return chunks
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract key terms and concepts from text"""
        # Common HMC terms and concepts
        hmc_terms = [
            'dwelling', 'owner', 'tenant', 'occupant', 'building', 'premises',
            'violation', 'inspection', 'maintenance', 'repair', 'habitability',
            'safety', 'health', 'sanitary', 'ventilation', 'heat', 'hot water',
            'pest', 'rodent', 'lead', 'mold', 'fire', 'emergency', 'access',
            'common area', 'apartment', 'room', 'bathroom', 'kitchen'
        ]
        
        text_lower = text.lower()
        found_keywords = [term for term in hmc_terms if term in text_lower]
        
        # Add any section numbers mentioned
        section_refs = self.patterns['cross_ref'].findall(text)
        found_keywords.extend([f"section-27-{ref}" for ref in section_refs])
        
        return list(set(found_keywords))
    
    def add_context_overlap(self, chunks: List[ChunkMetadata], overlap_tokens: int = 150) -> List[ChunkMetadata]:
        """Add overlapping context between adjacent chunks"""
        # This would be implemented to add context from adjacent chunks
        # For now, returning chunks as-is
        return chunks
    
    def process(self) -> Dict[str, Any]:
        """Main processing method"""
        print("🔄 Extracting text from PDF...")
        self.raw_text = self.extract_text()
        
        print("🔍 Identifying document structure...")
        structure = self.identify_structure(self.raw_text)
        
        print("🔗 Extracting cross-references...")
        self.cross_references = self.extract_cross_references(self.raw_text)
        
        print("📝 Creating chunks...")
        self.chunks = self.create_chunks(self.raw_text, structure)
        
        print("🎯 Adding context overlap...")
        self.chunks = self.add_context_overlap(self.chunks)
        
        return {
            'chunks': [asdict(chunk) for chunk in self.chunks],
            'structure': structure,
            'cross_references': self.cross_references,
            'stats': {
                'total_chunks': len(self.chunks),
                'subchapters': len([c for c in self.chunks if c.chunk_type == 'subchapter']),
                'articles': len([c for c in self.chunks if c.chunk_type == 'article']),
                'sections': len([c for c in self.chunks if c.chunk_type == 'section']),
                'total_tokens': sum(c.token_estimate for c in self.chunks)
            }
        }
    
    def save_chunks(self, output_dir: str = 'chunks'):
        """Save chunks to organized directory structure"""
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/subchapters", exist_ok=True)
        os.makedirs(f"{output_dir}/articles", exist_ok=True)
        os.makedirs(f"{output_dir}/sections", exist_ok=True)
        os.makedirs(f"{output_dir}/metadata", exist_ok=True)
        
        # Save chunks by type
        for chunk in self.chunks:
            chunk_dict = asdict(chunk)
            filename = f"{output_dir}/{chunk.chunk_type}s/{chunk.chunk_id}.json"
            
            with open(filename, 'w') as f:
                json.dump(chunk_dict, f, indent=2)
        
        # Save metadata
        with open(f"{output_dir}/metadata/cross_references.json", 'w') as f:
            json.dump(self.cross_references, f, indent=2)
        
        with open(f"{output_dir}/metadata/structure_map.json", 'w') as f:
            json.dump(self.structure_map, f, indent=2)
        
        print(f"✅ Chunks saved to {output_dir}/")

def main():
    """Main execution function"""
    pdf_path = "HousingMaintenanceCode.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    print("🏢 NYC Housing Maintenance Code PDF Chunker")
    print("=" * 50)
    
    chunker = HMCChunker(pdf_path)
    results = chunker.process()
    
    print("\n📊 Processing Results:")
    print(f"   Total chunks: {results['stats']['total_chunks']}")
    print(f"   Subchapters: {results['stats']['subchapters']}")
    print(f"   Articles: {results['stats']['articles']}")
    print(f"   Sections: {results['stats']['sections']}")
    print(f"   Estimated tokens: {results['stats']['total_tokens']:,}")
    
    # Save chunks
    chunker.save_chunks()
    
    print("\n🎯 Next Steps:")
    print("1. Install PDF processing libraries: pip install PyPDF2 pdfplumber")
    print("2. Run this script again for full PDF processing")
    print("3. Review generated chunks in the 'chunks/' directory")
    print("4. Integrate chunks with your LLM chatbot system")
    print("5. Test with sample queries about NYC housing regulations")

if __name__ == "__main__":
    main()