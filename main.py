import os
import json
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util
from datetime import datetime
import re
import sys

# ===============================
# 🔧 CONFIGURATION SETTINGS
# ===============================
class Config:
    """Configuration class to make the script adaptable for different use cases"""
    
    # File paths
    FOLDER_PATH = "./pdfs"  # Folder containing PDF files
    INPUT_FILE = "input.json"  # Input JSON file
    OUTPUT_FILE = "output.json"  # Output JSON file
    
    # Text processing settings
    MIN_SECTION_LENGTH = 50  # Minimum characters for a valid section
    MAX_REFINED_TEXT_LENGTH = 1000  # Maximum characters in refined text output
    
    # Similarity search settings
    SIMILARITY_MODEL = 'all-MiniLM-L6-v2'  # SentenceTransformer model
    TOP_N_SECTIONS = 5  # Number of top relevant sections to return
    MIN_SIMILARITY_THRESHOLD = 0.1  # Minimum similarity score to include a section
    
    # Section extraction settings
    MAX_HEADING_LENGTH = 200  # Maximum length for text to be considered a heading
    MAX_HEADING_WORDS = 10  # Maximum words in a heading for title case detection
    
    @classmethod
    def update_config(cls, **kwargs):
        """Update configuration parameters"""
        for key, value in kwargs.items():
            if hasattr(cls, key.upper()):
                setattr(cls, key.upper(), value)
            else:
                print(f"Warning: Unknown configuration parameter: {key}")

def create_input_json_interactive():
    """
    Interactive function to help users create their input.json file
    """
    print("🎯 PDF Document Analyzer - Interactive Setup")
    print("=" * 50)
    
    # Get user's role/persona
    print("\n👤 What is your role?")
    print("Examples: Travel Planner, Research Scientist, Legal Analyst, Software Developer")
    persona = input("Your role: ").strip()
    if not persona:
        persona = "Analyst"
    
    # Get what they want to analyze
    print(f"\n🎯 What do you want to find or analyze in your PDF documents?")
    print("Examples:")
    print("  - Plan a 7-day vacation for a family of 4")
    print("  - Find best practices for API development")
    print("  - Identify key research methodologies")
    print("  - Locate compliance requirements")
    task = input("Your task/question: ").strip()
    if not task:
        task = "Analyze and summarize key information"
    
    # Get project description
    print(f"\n📝 Brief description of your project:")
    description = input("Project description (optional): ").strip()
    if not description:
        description = f"Document analysis for {persona.lower()}"
    
    # Find PDF files in the pdfs folder
    pdf_folder = Config.FOLDER_PATH
    pdf_files = []
    
    if os.path.exists(pdf_folder):
        for file in os.listdir(pdf_folder):
            if file.lower().endswith('.pdf'):
                pdf_files.append(file)
    
    if not pdf_files:
        print(f"\n⚠️ No PDF files found in '{pdf_folder}' folder.")
        print("Please add your PDF files to the 'pdfs' folder and run this script again.")
        return False
    
    print(f"\n📂 Found {len(pdf_files)} PDF files:")
    for i, file in enumerate(pdf_files, 1):
        print(f"   {i}. {file}")
    
    # Auto-generate titles
    documents = []
    for file in pdf_files:
        title = file.replace('.pdf', '').replace('-', ' ').replace('_', ' ').title()
        documents.append({
            "filename": file,
            "title": title
        })
    
    # Create input JSON structure with description
    input_data = {
        "challenge_info": {
            "challenge_id": f"user_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "test_case_name": "user_defined_analysis",
            "description": description
        },
        "documents": documents,
        "persona": {
            "role": persona
        },
        "job_to_be_done": {
            "task": task
        }
    }
    
    # Save the input.json file
    with open(Config.INPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(input_data, f, indent=2, ensure_ascii=False)
    
    # Show summary
    print(f"\n✅ Created {Config.INPUT_FILE} successfully!")
    print(f"📋 Summary:")
    print(f"   Role: {persona}")
    print(f"   Task: {task}")
    print(f"   Description: {description}")
    print(f"   Documents: {len(documents)} PDF files")
    
    return True

def extract_text_with_pages_from_pdf(pdf_path):
    """
    Extract text from a PDF with page information using PyMuPDF.
    Returns a list of (page_number, text) tuples.
    """
    pages = []
    try:
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc, 1):
                text = page.get_text().strip()
                if text:
                    pages.append((page_num, text))
    except Exception as e:
        print(f"❌ Error reading PDF {pdf_path}: {e}")
    return pages

def extract_sections_from_text(text, page_number, min_section_length=None):
    """
    Extract meaningful sections from text based on headings and content structure.
    More flexible approach that works with various document types.
    """
    if min_section_length is None:
        min_section_length = Config.MIN_SECTION_LENGTH
        
    sections = []
    
    # Multiple strategies for section extraction
    
    # Strategy 1: Split by double newlines (paragraph breaks)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    # Strategy 2: Look for common heading patterns
    lines = text.split('\n')
    current_section = ""
    current_title = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Enhanced heading detection - more flexible patterns
        is_heading = False
        
        # Check various heading patterns
        if len(line) < Config.MAX_HEADING_LENGTH:  # Reasonable heading length
            # Pattern 1: All caps
            if line.isupper() and len(line) > 3:
                is_heading = True
            # Pattern 2: Title case starting with capital, no ending punctuation
            elif re.match(r'^[A-Z][^.!?]*[^.!?]$', line) and len(line.split()) <= Config.MAX_HEADING_WORDS:
                is_heading = True
            # Pattern 3: Lines ending with colon
            elif line.endswith(':') and len(line.split()) <= 8:
                is_heading = True
            # Pattern 4: Numbered sections
            elif re.match(r'^\d+[\.\)]\s*[A-Z]', line):
                is_heading = True
            # Pattern 5: Bullet point headers
            elif re.match(r'^[•\-\*]\s*[A-Z]', line) and len(line.split()) <= 8:
                is_heading = True
        
        if is_heading:
            # Save previous section if it exists and has enough content
            if current_title and current_section and len(current_section.strip()) >= min_section_length:
                sections.append({
                    'title': current_title,
                    'content': current_section.strip(),
                    'page_number': page_number
                })
            
            current_title = line
            current_section = ""
        else:
            current_section += line + " "
    
    # Add the last section
    if current_title and current_section and len(current_section.strip()) >= min_section_length:
        sections.append({
            'title': current_title,
            'content': current_section.strip(),
            'page_number': page_number
        })
    
    # Strategy 3: If no clear headings found, create sections from paragraphs
    if not sections and paragraphs:
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph) >= min_section_length:
                # Use first few words as title
                words = paragraph.split()
                title = ' '.join(words[:8]) + ('...' if len(words) > 8 else '')
                sections.append({
                    'title': title,
                    'content': paragraph,
                    'page_number': page_number
                })
    
    # Strategy 4: If still no sections, create one large section
    if not sections and len(text.strip()) >= min_section_length:
        words = text.strip().split()
        title = ' '.join(words[:10]) + ('...' if len(words) > 10 else '')
        sections.append({
            'title': title,
            'content': text.strip(),
            'page_number': page_number
        })
    
    return sections

def load_documents_with_sections(folder_path, input_documents):
    """
    Load text from PDF files specified in input_documents and extract sections.
    """
    all_sections = []
    
    for doc_info in input_documents:
        filename = doc_info['filename']
        path = os.path.join(folder_path, filename)
        
        if not os.path.exists(path):
            print(f"⚠️ File not found: {filename}")
            continue
            
        if filename.endswith('.pdf'):
            pages = extract_text_with_pages_from_pdf(path)
            
            for page_num, text in pages:
                sections = extract_sections_from_text(text, page_num)
                for section in sections:
                    section['document'] = filename
                    all_sections.append(section)
        else:
            print(f"⚠️ Unsupported file type: {filename}")
    
    return all_sections

def find_relevant_sections(task, sections, model_name='all-MiniLM-L6-v2', top_n=5, min_similarity=0.1):
    """
    Find sections most relevant to the given task using semantic similarity.
    
    Args:
        task (str): The task description to match against
        sections (list): List of section dictionaries
        model_name (str): SentenceTransformer model name
        top_n (int): Number of top sections to return
        min_similarity (float): Minimum similarity threshold
    """
    model = SentenceTransformer(model_name)
    
    if not sections:
        return []
    
    # Create text for similarity comparison
    section_texts = []
    for section in sections:
        # Combine title and content for better matching
        combined_text = f"{section['title']} {section['content']}"
        section_texts.append(combined_text)
    
    # Encode task and sections
    task_embedding = model.encode(task, convert_to_tensor=True)
    section_embeddings = model.encode(section_texts, convert_to_tensor=True)
    
    # Calculate similarities
    similarities = util.cos_sim(task_embedding, section_embeddings)[0]
    
    # Get top sections with similarity scores
    scored_sections = []
    for i, (section, similarity) in enumerate(zip(sections, similarities)):
        # Only include sections above minimum similarity threshold
        if float(similarity) >= min_similarity:
            scored_sections.append({
                'section': section,
                'similarity': float(similarity),
                'index': i
            })
    
    # Sort by similarity and return top N
    scored_sections.sort(key=lambda x: x['similarity'], reverse=True)
    return scored_sections[:top_n]

def create_output_json(input_data, relevant_sections):
    """
    Create the output JSON in the required format.
    """
    # Extract metadata
    metadata = {
        "input_documents": [doc['filename'] for doc in input_data['documents']],
        "persona": input_data['persona']['role'],
        "job_to_be_done": input_data['job_to_be_done']['task'],
        "processing_timestamp": datetime.now().isoformat()
    }
    
    # Add description if it exists
    if 'challenge_info' in input_data and 'description' in input_data['challenge_info']:
        metadata["description"] = input_data['challenge_info']['description']
    
    # Create extracted sections
    extracted_sections = []
    for i, item in enumerate(relevant_sections, 1):
        section = item['section']
        extracted_sections.append({
            "document": section['document'],
            "section_title": section['title'],
            "importance_rank": i,
            "page_number": section['page_number']
        })
    
    # Create subsection analysis with refined text
    subsection_analysis = []
    for item in relevant_sections:
        section = item['section']
        # Limit content to reasonable length and clean it up
        refined_text = section['content'][:Config.MAX_REFINED_TEXT_LENGTH].strip()
        # Remove extra whitespace
        refined_text = re.sub(r'\s+', ' ', refined_text)
        
        subsection_analysis.append({
            "document": section['document'],
            "refined_text": refined_text,
            "page_number": section['page_number']
        })
    
    return {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

# ===============================
# 🔧 MAIN PROGRAM CONFIGURATION
# ===============================
if __name__ == "__main__":
    # ===========================================
    # 🎯 WELCOME MESSAGE
    # ===========================================
    print("🎯 Universal PDF Document Analyzer")
    print("=" * 45)
    print("📂 Analyzes PDF documents and finds relevant sections")
    print("   based on your specific task or question.")
    print()
    
    # Check for setup mode
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        if create_input_json_interactive():
            print(f"\n🚀 Setup complete! Now run: python pdf_analyzer.py")
        sys.exit()
    
    # ===========================================
    # 🎯 GET USER INPUT
    # ===========================================
    print("👤 What is your role?")
    print("Examples: Travel Planner, Research Scientist, Legal Analyst, Software Developer")
    user_role = input("Your role: ").strip()
    if not user_role:
        user_role = "Analyst"
    
    print(f"\n🎯 What do you want to find or analyze in your PDF documents?")
    print("Examples:")
    print("  - Plan a 7-day vacation for a family of 4")
    print("  - Find best practices for API development")
    print("  - Identify key research methodologies")
    print("  - Locate compliance requirements")
    user_task = input("Your task/question: ").strip()
    if not user_task:
        user_task = "Analyze and summarize key information"
    
    print(f"\n📝 Brief description of your project (optional):")
    user_description = input("Project description: ").strip()
    if not user_description:
        user_description = f"Document analysis for {user_role.lower()}"
    
    # ===========================================
    # 🎯 CONFIGURATION OPTIONS
    # ===========================================
    # Uncomment and modify these for different document types:
    #
    # For technical documentation:
    # Config.update_config(
    #     min_section_length=100,
    #     max_heading_length=300,
    #     top_n_sections=10,
    #     min_similarity_threshold=0.05,
    #     similarity_model='all-mpnet-base-v2'
    # )
    #
    # For research papers:
    # Config.update_config(
    #     min_section_length=200,
    #     max_refined_text_length=2000,
    #     top_n_sections=8,
    #     max_heading_words=15
    # )
    #
    # For legal documents:
    # Config.update_config(
    #     min_section_length=150,
    #     top_n_sections=7,
    #     min_similarity_threshold=0.08,
    #     max_refined_text_length=1500
    # )
    #
    # For marketing content:
    # Config.update_config(
    #     min_section_length=30,
    #     max_heading_length=150,
    #     top_n_sections=6,
    #     min_similarity_threshold=0.15
    # )
    # ===========================================
    
    # Configuration
    folder_path = Config.FOLDER_PATH
    output_file = Config.OUTPUT_FILE
    
    # Find PDF files in the pdfs folder
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"📂 Created '{folder_path}' folder - add your PDF files here")
        sys.exit(1)
    
    pdf_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith('.pdf'):
            pdf_files.append(file)
    
    if not pdf_files:
        print(f"\n⚠️ No PDF files found in '{folder_path}' folder.")
        print("Please add your PDF files to the 'pdfs' folder and try again.")
        sys.exit(1)
    
    print(f"\n📂 Found {len(pdf_files)} PDF files:")
    for i, file in enumerate(pdf_files, 1):
        print(f"   {i}. {file}")
    
    # Auto-generate document list
    documents = []
    for file in pdf_files:
        title = file.replace('.pdf', '').replace('-', ' ').replace('_', ' ').title()
        documents.append({
            "filename": file,
            "title": title
        })
    
    # Create input data structure from user input
    input_data = {
        "challenge_info": {
            "challenge_id": f"user_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "test_case_name": "user_defined_analysis",
            "description": user_description
        },
        "documents": documents,
        "persona": {
            "role": user_role
        },
        "job_to_be_done": {
            "task": user_task
        }
    }
    
    print(f"\n📋 Analysis Summary:")
    print(f"👤 Role: {user_role}")
    print(f"🎯 Task: {user_task}")
    print(f"📝 Description: {user_description}")
    print("🔍 Processing documents...")
    
    # Load and process documents
    sections = load_documents_with_sections(folder_path, input_data['documents'])
    print(f"📂 Extracted {len(sections)} sections from {len(input_data['documents'])} documents.")
    
    if not sections:
        print("❌ No valid sections found. Exiting.")
        exit()
    
    # Find relevant sections for the task
    task = input_data['job_to_be_done']['task']
    print(f"🧠 Finding relevant sections for task: {task}")
    
    relevant_sections = find_relevant_sections(
        task, 
        sections, 
        model_name=Config.SIMILARITY_MODEL,
        top_n=Config.TOP_N_SECTIONS,
        min_similarity=Config.MIN_SIMILARITY_THRESHOLD
    )
    
    # Create output JSON
    output_data = create_output_json(input_data, relevant_sections)
    
    # Save output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Output saved to {output_file}")
    print(f"\n🔝 Top {len(relevant_sections)} relevant sections:")
    
    for i, item in enumerate(relevant_sections, 1):
        section = item['section']
        similarity = item['similarity']
        print(f"\n📄 Result {i}: {section['document']}")
        print(f"📑 Section: {section['title']}")
        print(f"📄 Page: {section['page_number']}")
        print(f"🔗 Similarity: {similarity:.4f}")
        print(f"� Content: {section['content'][:200]}...")
    
    print(f"\n📊 Metadata:")
    print(f"   Persona: {output_data['metadata']['persona']}")
    print(f"   Task: {output_data['metadata']['job_to_be_done']}")
    print(f"   Documents processed: {len(output_data['metadata']['input_documents'])}")
    print(f"   Timestamp: {output_data['metadata']['processing_timestamp']}")
