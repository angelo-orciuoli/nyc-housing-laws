# NYC Housing Maintenance Code PDF Chunking for LLM Chatbot

This repository provides a comprehensive solution for chunking the NYC Housing Maintenance Code (HMC) PDF into structured, searchable segments optimized for LLM chatbot applications.

## 📋 Overview

The NYC Housing Maintenance Code is a complex legal document with hierarchical structure:
- **Title 27, Chapter 2** of NYC Administrative Code
- **Subchapters** (major topic divisions)
- **Articles** (specific regulatory areas)
- **Sections** (individual regulations with § 27-XXXX format)

## 🚀 Quick Start

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Run PDF Chunker**
```bash
python3 pdf_chunker.py
```

3. **Test Chatbot Integration**
```bash
python3 chatbot_integration_example.py
```

## 📁 Project Structure

```
├── HousingMaintenanceCode.pdf          # Original NYC HMC PDF
├── pdf_chunker.py                      # Main chunking implementation
├── chatbot_integration_example.py      # Chatbot demo and integration guide
├── pdf_chunking_strategy.md            # Detailed chunking methodology
├── requirements.txt                    # Python dependencies
├── chunks/                             # Generated chunk outputs
│   ├── subchapters/                   # High-level topic chunks
│   ├── articles/                      # Medium-granularity chunks
│   ├── sections/                      # Specific regulation chunks
│   └── metadata/                      # Cross-references and structure
└── README.md                          # This file
```

## 🔧 Chunking Strategy

### Hierarchical Approach
The chunking system creates three levels of granularity:

1. **Section-level chunks** (100-800 tokens)
   - Individual regulations (§ 27-XXXX)
   - Most granular and precise
   - Perfect for specific legal queries

2. **Article-level chunks** (500-2,000 tokens)
   - Groups of related sections
   - Good for topical understanding
   - Balanced detail and context

3. **Subchapter-level chunks** (2,000-8,000 tokens)
   - Major topic areas
   - Comprehensive context
   - Ideal for broad explanations

### Metadata Structure
Each chunk includes rich metadata:

```json
{
  "chunk_id": "section_27_2004",
  "title": "§ 27-2004 - Definitions",
  "hierarchy": {
    "title": "27",
    "chapter": "2",
    "section": "27-2004"
  },
  "page_numbers": [15],
  "cross_references": ["27-2005", "27-2115"],
  "keywords": ["dwelling", "owner", "tenant"],
  "chunk_type": "section",
  "content_length": 1250,
  "token_estimate": 312
}
```

## 🤖 LLM Integration

### Retrieval-Augmented Generation (RAG)
The chunked data is optimized for RAG systems:

1. **Semantic Search**: Use embeddings to find relevant chunks
2. **Context Assembly**: Combine multiple chunks with cross-references
3. **Answer Generation**: Provide chunks to LLM for accurate responses
4. **Citation Tracking**: Maintain section references for legal accuracy

### Example Integration
```python
from chatbot_integration_example import HMCChatbot

chatbot = HMCChatbot()
response = chatbot.answer_question("What are owner responsibilities?")

print(response['answer'])
print(f"Sources: {response['sources']}")
print(f"Related: {response['related_sections']}")
```

## 📊 Features

### ✅ Implemented
- PDF text extraction (PyPDF2, pdfplumber support)
- Hierarchical structure detection
- Cross-reference mapping
- Keyword extraction
- Token estimation
- JSON output format
- Basic chatbot demo

### 🔄 Planned Enhancements
- Semantic embedding generation
- Vector database integration
- Advanced NLP processing
- Context overlap optimization
- Multi-language support
- Web interface

## 🛠️ Technical Details

### PDF Processing
The system supports multiple PDF extraction methods:
- **pdfplumber**: Preferred for layout-aware extraction
- **PyPDF2**: Fallback for basic text extraction
- **Manual extraction**: For environments without PDF libraries

### Structure Detection
Uses regex patterns to identify:
- Subchapter headings: `SUBCHAPTER \d+ - TITLE`
- Article headings: `ARTICLE \d+ - TITLE`
- Section numbers: `§ 27-\d{4} - TITLE`
- Cross-references: `§ 27-\d{4}` mentions

### Cross-Reference Mapping
Automatically builds bidirectional reference maps:
- Forward references: What sections does X reference?
- Backward references: What sections reference X?

## 📈 Usage Examples

### Legal Research
```python
# Find specific regulation
response = chatbot.answer_question("What is section 27-2004?")

# Research topic area
response = chatbot.answer_question("heating requirements apartments")

# Cross-reference navigation
related = chatbot.get_related_sections("2004")
```

### Tenant/Landlord Support
```python
# Owner obligations
response = chatbot.answer_question("owner maintenance responsibilities")

# Tenant rights
response = chatbot.answer_question("tenant repair requests")

# Violation procedures
response = chatbot.answer_question("housing code violations enforcement")
```

## 🔍 Quality Assurance

### Validation Checks
- Chunk completeness verification
- Cross-reference accuracy testing
- Token count validation
- Structure integrity checks

### Testing
```bash
# Run basic functionality tests
python3 -m pytest tests/

# Validate chunk integrity
python3 validate_chunks.py

# Performance benchmarks
python3 benchmark_search.py
```

## 📚 Integration Guide

### For RAG Systems
1. **Embed chunks** using sentence-transformers
2. **Store in vector DB** (Pinecone, Weaviate, Chroma)
3. **Implement semantic search** for query matching
4. **Combine with LLM** for answer generation

### For Fine-tuning
1. **Create Q&A pairs** from chunks
2. **Format for training** (instruction-following format)
3. **Include citations** in target responses
4. **Validate legal accuracy** before deployment

### Production Considerations
- **Error handling**: Graceful failures for missing chunks
- **Rate limiting**: Prevent API abuse
- **Legal disclaimers**: Not a substitute for legal advice
- **Updates**: Regular sync with HMC changes
- **Monitoring**: Track accuracy and user satisfaction

## 🚨 Important Notes

### Legal Disclaimer
This tool is for informational purposes only and does not constitute legal advice. Always consult with qualified legal professionals for specific housing law matters.

### Data Accuracy
The chunking system is designed to preserve legal document integrity, but users should verify critical information against the original PDF.

### Updates
The NYC Housing Maintenance Code may be updated periodically. Regenerate chunks when new versions are released.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure legal accuracy is maintained
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Resources

- [NYC Housing Maintenance Code](https://www1.nyc.gov/site/hpd/about/hmc.page)
- [NYC Administrative Code Title 27](https://codelibrary.amlegal.com/codes/newyorkcity/latest/NYCadmin/0-0-0-2394)
- [LangChain Documentation](https://python.langchain.com/docs/)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)

---

**Built for legal professionals, housing advocates, and developers creating AI-powered housing law assistance tools.**