# NYC Housing Maintenance Code PDF Chunking Strategy for LLM Chatbot

## Overview
The NYC Housing Maintenance Code (HMC) is structured hierarchically as:
- **Title 27, Chapter 2** of NYC Administrative Code
- **Subchapters** (major topic divisions)
- **Articles** (specific regulatory areas within subchapters)
- **Sections** (individual regulations)

## Recommended Chunking Strategy

### 1. Hierarchical Structure-Based Chunking
This approach preserves the legal document's natural organization:

#### Primary Chunks: Subchapters
- Each subchapter becomes a major chunk
- Maintains legal context and thematic coherence
- Typical size: 2,000-8,000 tokens per subchapter

#### Secondary Chunks: Articles
- Articles within subchapters become sub-chunks
- Ideal for specific topic queries
- Typical size: 500-2,000 tokens per article

#### Tertiary Chunks: Sections
- Individual sections for granular reference
- Perfect for specific regulation lookup
- Typical size: 100-800 tokens per section

### 2. Metadata-Rich Chunking
Each chunk should include comprehensive metadata:

```json
{
  "chunk_id": "hmc_subchapter_1_article_3_section_27-2013",
  "hierarchy": {
    "title": "27",
    "chapter": "2", 
    "subchapter": "1",
    "article": "3",
    "section": "27-2013"
  },
  "title": "General Provisions - Definitions - Owner",
  "content": "...",
  "page_numbers": [15, 16],
  "cross_references": ["27-2004", "27-2017"],
  "keywords": ["owner", "responsibility", "maintenance"],
  "chunk_type": "section",
  "parent_chunks": ["subchapter_1", "article_3"]
}
```

### 3. Overlapping Context Windows
- Include 100-200 tokens from previous/next chunks
- Preserves context across chunk boundaries
- Helps with regulatory flow and dependencies

### 4. Cross-Reference Mapping
- Extract all section references (e.g., "§ 27-2013")
- Create bidirectional reference map
- Enable chatbot to navigate related regulations

## Implementation Approach

### Phase 1: Structure Extraction
1. **Parse PDF structure** using table of contents
2. **Identify hierarchical markers**:
   - Subchapter headings (usually larger font, numbered)
   - Article headings (medium font, lettered/numbered)
   - Section numbers (§ 27-XXXX format)
3. **Extract page boundaries** for each structural element

### Phase 2: Content Chunking
1. **Primary chunking** by subchapter
2. **Secondary chunking** by article
3. **Tertiary chunking** by section
4. **Add overlapping context** (100-200 tokens)

### Phase 3: Metadata Enhancement
1. **Extract cross-references** (§ references, "see also")
2. **Identify key terms** and definitions
3. **Map enforcement provisions** to violations
4. **Create topic tags** (safety, maintenance, violations, etc.)

### Phase 4: Quality Assurance
1. **Validate chunk completeness** (no missing sections)
2. **Check cross-reference accuracy**
3. **Ensure proper context preservation**
4. **Test with sample queries**

## Optimal Chunk Sizes for LLM Chatbot

### For Retrieval (RAG)
- **Primary chunks**: 1,500-3,000 tokens
- **Secondary chunks**: 500-1,500 tokens  
- **Context overlap**: 100-200 tokens

### For Fine-tuning Data
- **Training examples**: 2,000-4,000 tokens
- **Include question-answer pairs** based on regulations
- **Maintain legal precision** in responses

## Special Considerations

### Legal Document Integrity
- **Never split mid-sentence** or mid-regulation
- **Preserve legal numbering** and formatting
- **Maintain definitional context** (definitions must stay with usage)

### NYC-Specific Elements
- **Building classifications** (Class A, B, etc.)
- **Violation categories** and penalties
- **Inspection procedures** and timelines
- **Owner vs. tenant responsibilities**

### Search Optimization
- **Include common synonyms** in metadata
- **Tag practical applications** (e.g., "heat complaints", "pest control")
- **Map to common tenant/landlord scenarios**

## Technical Implementation Tools

### Recommended Libraries
```python
# PDF Processing
import PyPDF2          # Basic PDF text extraction
import pdfplumber      # Advanced layout-aware extraction
import fitz            # PyMuPDF for detailed document analysis

# Text Processing  
import spacy           # NLP for structure detection
import nltk            # Text segmentation and analysis
import regex           # Advanced pattern matching for legal citations

# Chunking and Embedding
import langchain       # Document chunking utilities
import tiktoken        # Token counting for OpenAI models
import sentence_transformers  # For semantic similarity
```

### Processing Pipeline
```python
def process_hmc_pdf(pdf_path):
    # 1. Extract raw text with layout information
    # 2. Identify structural markers (headings, sections)
    # 3. Parse hierarchical organization
    # 4. Create primary chunks (subchapters)
    # 5. Create secondary chunks (articles) 
    # 6. Create tertiary chunks (sections)
    # 7. Add metadata and cross-references
    # 8. Validate and export chunks
    pass
```

## Expected Output Structure

```
chunks/
├── subchapters/
│   ├── subchapter_1_general_provisions.json
│   ├── subchapter_2_occupancy.json
│   └── ...
├── articles/
│   ├── article_1_1_definitions.json
│   ├── article_1_2_scope.json
│   └── ...
├── sections/
│   ├── section_27_2004.json
│   ├── section_27_2005.json
│   └── ...
└── metadata/
    ├── cross_references.json
    ├── definitions.json
    └── structure_map.json
```

This chunking strategy will enable your LLM chatbot to:
- Answer specific regulatory questions with proper citations
- Navigate complex cross-references between sections
- Provide context-aware responses about tenant/landlord rights
- Maintain legal accuracy while being conversational
- Handle both general inquiries and specific violation lookups