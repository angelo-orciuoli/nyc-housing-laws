#!/usr/bin/env python3
"""
NYC Housing Maintenance Code Chatbot Integration Example
Demonstrates how to use the chunked HMC data with an LLM for answering housing law questions.
"""

import json
import os
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import re

@dataclass
class QueryResult:
    """Result from querying the HMC knowledge base"""
    chunk_id: str
    title: str
    content: str
    relevance_score: float
    chunk_type: str
    cross_references: List[str]
    keywords: List[str]

class HMCChatbot:
    """Chatbot for NYC Housing Maintenance Code queries"""
    
    def __init__(self, chunks_dir: str = "chunks"):
        self.chunks_dir = chunks_dir
        self.chunks = {}
        self.cross_references = {}
        self.load_chunks()
    
    def load_chunks(self):
        """Load all chunks and metadata"""
        print("📚 Loading HMC knowledge base...")
        
        # Load chunks from all categories
        for chunk_type in ['sections', 'articles', 'subchapters']:
            chunk_dir = os.path.join(self.chunks_dir, chunk_type)
            if os.path.exists(chunk_dir):
                for filename in os.listdir(chunk_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(chunk_dir, filename)
                        with open(filepath, 'r') as f:
                            chunk_data = json.load(f)
                            self.chunks[chunk_data['chunk_id']] = chunk_data
        
        # Load cross-references
        cross_ref_path = os.path.join(self.chunks_dir, 'metadata', 'cross_references.json')
        if os.path.exists(cross_ref_path):
            with open(cross_ref_path, 'r') as f:
                self.cross_references = json.load(f)
        
        print(f"✅ Loaded {len(self.chunks)} chunks")
    
    def simple_keyword_search(self, query: str, top_k: int = 5) -> List[QueryResult]:
        """
        Simple keyword-based search (can be enhanced with semantic search)
        """
        query_lower = query.lower()
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        
        results = []
        
        for chunk_id, chunk_data in self.chunks.items():
            # Calculate relevance score based on keyword matches
            score = 0
            
            # Check title matches (higher weight)
            title_words = set(re.findall(r'\b\w+\b', chunk_data['title'].lower()))
            title_matches = len(query_words.intersection(title_words))
            score += title_matches * 3
            
            # Check keyword matches
            chunk_keywords = [kw.lower() for kw in chunk_data.get('keywords', [])]
            for keyword in chunk_keywords:
                if any(word in keyword for word in query_words):
                    score += 2
            
            # Check if this is a section reference (e.g., "27-2004")
            section_pattern = r'27-(\d{4})'
            section_matches = re.findall(section_pattern, query)
            if section_matches:
                chunk_section = chunk_data.get('hierarchy', {}).get('section', '')
                if any(f"27-{match}" == chunk_section for match in section_matches):
                    score += 10  # High relevance for direct section matches
            
            if score > 0:
                results.append(QueryResult(
                    chunk_id=chunk_id,
                    title=chunk_data['title'],
                    content=f"[Content would be extracted from PDF - {chunk_data['content_length']} chars]",
                    relevance_score=score,
                    chunk_type=chunk_data['chunk_type'],
                    cross_references=chunk_data.get('cross_references', []),
                    keywords=chunk_data.get('keywords', [])
                ))
        
        # Sort by relevance score and return top results
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:top_k]
    
    def get_related_sections(self, section_num: str) -> List[str]:
        """Get sections that reference the given section"""
        related = []
        
        # Direct cross-references
        if section_num in self.cross_references:
            related.extend(self.cross_references[section_num])
        
        # Reverse lookup - sections that reference this one
        for ref_section, targets in self.cross_references.items():
            if section_num in targets:
                related.append(ref_section)
        
        return list(set(related))
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Main method to answer housing law questions
        """
        print(f"\n❓ Question: {question}")
        print("🔍 Searching HMC knowledge base...")
        
        # Search for relevant chunks
        results = self.simple_keyword_search(question)
        
        if not results:
            return {
                'answer': "I couldn't find specific information about that in the Housing Maintenance Code. Please try rephrasing your question or ask about specific topics like 'owner responsibilities', 'tenant rights', 'heating requirements', etc.",
                'sources': [],
                'related_sections': []
            }
        
        # Get the most relevant result
        primary_result = results[0]
        
        # Find related sections for additional context
        section_match = re.search(r'27-(\d{4})', primary_result.chunk_id)
        related_sections = []
        if section_match:
            section_num = section_match.group(1)
            related_sections = self.get_related_sections(section_num)
        
        # Construct answer (this would use an LLM in a real implementation)
        answer = self.construct_answer(question, results[:3])
        
        return {
            'answer': answer,
            'sources': [
                {
                    'title': result.title,
                    'chunk_id': result.chunk_id,
                    'relevance': result.relevance_score,
                    'type': result.chunk_type
                }
                for result in results[:3]
            ],
            'related_sections': related_sections,
            'cross_references': primary_result.cross_references
        }
    
    def construct_answer(self, question: str, results: List[QueryResult]) -> str:
        """
        Construct an answer based on search results
        (In a real implementation, this would use an LLM)
        """
        if not results:
            return "No relevant information found."
        
        primary = results[0]
        
        # Basic answer construction based on chunk type and keywords
        if 'owner' in question.lower():
            if 'definition' in primary.keywords or 'owner' in primary.keywords:
                return f"According to {primary.title}, the Housing Maintenance Code defines owner responsibilities and requirements. The specific regulations can be found in the referenced section, which covers legal obligations for property owners in NYC."
        
        elif 'tenant' in question.lower():
            return f"Based on {primary.title}, tenant rights and protections are outlined in the Housing Maintenance Code. This section addresses tenant-related provisions and may reference additional sections for comprehensive coverage."
        
        elif 'heat' in question.lower() or 'heating' in question.lower():
            return f"Heating requirements are covered under {primary.title}. The Housing Maintenance Code establishes minimum heating standards that property owners must maintain for tenant safety and comfort."
        
        elif 'violation' in question.lower():
            return f"Housing violations are addressed in {primary.title}. The code outlines specific violations, enforcement procedures, and penalties for non-compliance with housing standards."
        
        else:
            return f"The most relevant information is found in {primary.title}. This section of the Housing Maintenance Code addresses your query and may contain specific requirements, definitions, or procedures related to your question."
    
    def get_chunk_content(self, chunk_id: str) -> str:
        """
        Get the full content of a specific chunk
        (In a real implementation, this would extract from the original PDF)
        """
        if chunk_id in self.chunks:
            chunk = self.chunks[chunk_id]
            return f"[Full content of {chunk['title']} - {chunk['content_length']} characters]"
        return "Chunk not found."

def demo_queries():
    """Demonstrate the chatbot with sample queries"""
    chatbot = HMCChatbot()
    
    sample_questions = [
        "What are the owner's responsibilities for maintenance?",
        "What defines a dwelling under the housing code?",
        "What are the heating requirements for apartments?",
        "How are housing violations enforced?",
        "What is section 27-2004 about?",
        "What rights do tenants have regarding repairs?"
    ]
    
    print("\n🏢 NYC Housing Maintenance Code Chatbot Demo")
    print("=" * 60)
    
    for question in sample_questions:
        response = chatbot.answer_question(question)
        
        print(f"\n💬 Answer: {response['answer']}")
        
        if response['sources']:
            print(f"\n📋 Sources:")
            for source in response['sources']:
                print(f"   • {source['title']} (relevance: {source['relevance']})")
        
        if response['related_sections']:
            print(f"\n🔗 Related sections: {', '.join(response['related_sections'])}")
        
        print("-" * 60)

def integration_guide():
    """Print integration guide for LLM systems"""
    guide = """
🚀 LLM Integration Guide for HMC Chatbot

1. RETRIEVAL-AUGMENTED GENERATION (RAG)
   • Use semantic search (e.g., sentence-transformers) instead of keyword search
   • Embed chunks using models like 'all-MiniLM-L6-v2' or 'text-embedding-ada-002'
   • Store embeddings in vector database (Pinecone, Weaviate, Chroma)
   • Retrieve top-k relevant chunks for each query

2. PROMPT ENGINEERING
   ```python
   prompt = f'''
   You are an expert on NYC Housing Maintenance Code. Answer the user's question 
   based on the following relevant sections:

   {relevant_chunks}

   Question: {user_question}

   Provide a clear, accurate answer with specific section references.
   If the information is not in the provided sections, say so.
   '''
   ```

3. ENHANCED FEATURES
   • Cross-reference navigation: "See also sections X, Y, Z"
   • Citation tracking: Always include section numbers
   • Confidence scoring: Rate answer confidence based on chunk relevance
   • Multi-turn conversations: Maintain context across questions

4. PRODUCTION CONSIDERATIONS
   • Implement proper error handling and fallbacks
   • Add rate limiting and user authentication
   • Monitor for hallucinations and incorrect legal advice
   • Regular updates when HMC regulations change
   • Legal disclaimer about seeking professional advice

5. EVALUATION METRICS
   • Answer accuracy vs. ground truth
   • Citation precision and recall
   • User satisfaction ratings
   • Response time and system performance
   """
    print(guide)

if __name__ == "__main__":
    # Check if chunks directory exists
    if not os.path.exists("chunks"):
        print("❌ Chunks directory not found. Please run pdf_chunker.py first.")
        exit(1)
    
    # Run demo
    demo_queries()
    
    # Print integration guide
    integration_guide()