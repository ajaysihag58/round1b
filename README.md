# 📄 Universal PDF Document Analyzer

A powerful, flexible Python script that can analyze **any type of PDF documents** and extract relevant sections based on semantic similarity to your specific task or query.

## 🚀 Super Quick Start

### Just Run It! (Recommended)
```bash
# 1---

## 📁 Files in This Package

### What You Get:
- **`pdf_analyzer.py`** - Main analyzer script (run this!)
- **`README.md`** - This comprehensive guide

### What Gets Created:
- **`output.json`** - Analysis results (generated automatically)
- **`pdfs/`** - Folder for your PDF files (created if needed)
- **`input.json`** - Optional configuration file (only for advanced usage)

### What You Need to Do:
1. Install Python packages: `pip install PyMuPDF sentence-transformers torch`
2. Add your PDF files to the `pdfs/` folder
3. Run: `python pdf_analyzer.py`
4. Answer the prompts about your role and task
5. Get your results in `output.json`! requirements
pip install PyMuPDF sentence-transformers torch

# 2. Put your PDF files in the pdfs/ folder
# 3. Run the analyzer - it will ask you what you need!
python pdf_analyzer.py
```

The script will interactively ask you:
- **Your role** (Travel Planner, Research Scientist, etc.)
- **Your task** (What you want to find in the documents)
- **Description** (Optional project description)

That's it! No setup files needed.

---

## 📝 Files in This Package

### Essential Files:
- **`pdf_analyzer.py`** - Complete analyzer script (this is all you need!)
- **`README.md`** - This comprehensive guide

### Files Created Automatically:
- **`output.json`** - Analysis results (generated after each run)
- **`pdfs/`** - Folder for your PDF files (created automatically if needed)

### Optional Setup Mode:
- **`input.json`** - Configuration file (only needed for advanced/batch usage)

---

## 📋 Two Ways to Use the Analyzer

### Option 1: Interactive Mode (Recommended)
```bash
# Simply run the script - it will guide you through everything
python pdf_analyzer.py
```

### Option 2: Advanced Setup Mode
```bash
# Create a reusable configuration file
python pdf_analyzer.py --setup

# Then run with that configuration
python pdf_analyzer.py
```

---

## 📋 Input.json Format (for advanced/batch usage only)

If you prefer to use the setup mode or need batch processing, you can create an input.json file:

```json
{
    "challenge_info": {
        "description": "Your project description"
    },
    "documents": [
        {
            "filename": "document1.pdf",
            "title": "Document 1 Title"
        }
    ],
    "persona": {
        "role": "Your Role (e.g., Travel Planner, Researcher, Legal Analyst)"
    },
    "job_to_be_done": {
        "task": "Your specific question or task"
    }
}
```

---

## 🎯 Real-World Examples

### 🏖️ Travel Planning
When prompted, enter:
- **Role**: Travel Planner
- **Task**: Plan a 7-day vacation for a family of 4 interested in food and culture
- **Description**: Family vacation planning

**PDFs**: Travel guides, restaurant lists, cultural attractions

### 📚 Academic Research
When prompted, enter:
- **Role**: Research Scientist  
- **Task**: Find key methodologies used in machine learning research
- **Description**: ML methodology analysis

**PDFs**: Research papers, technical reports

### ⚖️ Legal Analysis
When prompted, enter:
- **Role**: Legal Analyst
- **Task**: Find regulations related to data privacy compliance
- **Description**: GDPR compliance research

**PDFs**: Legal documents, regulatory guidelines

### 🔧 Technical Documentation
When prompted, enter:
- **Role**: Software Developer
- **Task**: Find best practices for API authentication implementation
- **Description**: API security documentation review

**PDFs**: Technical manuals, API documentation

### 🏥 Medical Research
When prompted, enter:
- **Role**: Medical Researcher
- **Task**: Find treatment protocols for diabetes management
- **Description**: Clinical guideline analysis

**PDFs**: Medical journals, treatment guidelines

### 💼 Business Analysis
When prompted, enter:
- **Role**: Marketing Manager
- **Task**: Identify consumer trends in sustainable products
- **Description**: Sustainability market research

**PDFs**: Market reports, consumer studies

---

## ⚙️ Configuration for Different Document Types

You can customize the analyzer by adding configuration at the top of `pdf_analyzer.py`:

### For Technical Documentation:
```python
Config.update_config(
    min_section_length=100,
    max_heading_length=300,
    top_n_sections=10,
    min_similarity_threshold=0.05,
    similarity_model='all-mpnet-base-v2'
)
```

### For Research Papers:
```python
Config.update_config(
    min_section_length=200,
    max_refined_text_length=2000,
    top_n_sections=8,
    max_heading_words=15
)
```

### For Legal Documents:
```python
Config.update_config(
    min_section_length=150,
    top_n_sections=7,
    min_similarity_threshold=0.08,
    max_refined_text_length=1500
)
```

### For Marketing Content:
```python
Config.update_config(
    min_section_length=30,
    max_heading_length=150,
    top_n_sections=6,
    min_similarity_threshold=0.15
)
```

---

## 📊 Output Format

The script generates an `output.json` file with:

### Metadata
- Your role, task, and description
- Processing timestamp and document list
- Configuration details used

### Extracted Sections
- Top relevant sections ranked by importance
- Document name, section title, page number
- Similarity scores showing relevance

### Subsection Analysis
- Detailed text content from each relevant section
- Cleaned and formatted for easy reading
- Page references for source verification

---

## 🔍 How It Works

1. **PDF Text Extraction**: Extracts text from PDFs with page numbers using PyMuPDF
2. **Smart Section Detection**: Uses multiple strategies to identify document sections:
   - Heading pattern recognition (ALL CAPS, Title Case, numbered sections)
   - Paragraph breaks and formatting cues
   - Bullet points and colon-ending lines
3. **AI-Powered Semantic Analysis**: Uses SentenceTransformers to find sections most relevant to your task
4. **Intelligent Ranking**: Ranks sections by relevance and generates structured output

---

## 🛠️ Advanced Usage

### Custom AI Models
```python
Config.update_config(
    similarity_model='sentence-transformers/all-mpnet-base-v2'
    # or any other SentenceTransformer model
)
```

### Batch Processing
Process multiple document sets by changing the input.json file and running the script multiple times.

### Integration
- **Web Services**: Wrap the script in a Flask/FastAPI application
- **Databases**: Store results in your preferred database
- **Automation**: Use in CI/CD pipelines or scheduled tasks

---

## 🐛 Troubleshooting

### "No sections found"
- Check PDF text extraction quality (PDFs should be text-based, not scanned images)
- Lower `min_section_length` parameter
- Verify PDF files are in the correct folder

### "Low similarity scores"
- Make task description more specific
- Lower `min_similarity_threshold`
- Try different AI models (all-mpnet-base-v2 for better accuracy)

### "Poor section detection"
- Adjust heading detection parameters
- Check document formatting
- Use different extraction strategies

---

## 📈 Performance Tips

### For Better Results:
- **Specific Tasks**: Use descriptive, specific tasks when prompted
- **Quality PDFs**: Ensure PDFs have good text extraction quality (not scanned images)
- **Domain Tuning**: Adjust similarity thresholds based on your domain
- **Model Selection**: Use domain-specific AI models when available

### Example Good vs. Poor Task Descriptions:
✅ **Good**: "Find budget-friendly family restaurants in downtown Paris with outdoor seating"
❌ **Poor**: "Find restaurants"

✅ **Good**: "Identify machine learning algorithms suitable for time series forecasting"
❌ **Poor**: "Find AI stuff"

### Recommended Settings by Domain:
- **Technical docs**: Lower similarity threshold (0.05-0.08)
- **Marketing content**: Higher similarity threshold (0.12-0.18)
- **Academic papers**: More sections (8-10) with longer text
- **Legal documents**: Moderate settings with comprehensive sections

---

## 🎯 The Magic ✨

1. **Universal Compatibility** → Works with ANY type of PDF documents
2. **Smart Understanding** → AI-powered semantic matching, not just keyword search
3. **Flexible Configuration** → Easily adaptable for different domains and use cases
4. **Structured Output** → Clean JSON format for easy integration
5. **Page Tracking** → Knows exactly where information came from

---

## � Files in This Package

- **`pdf_analyzer.py`** - Main analyzer script (run this!)
- **`README.md`** - This comprehensive guide
- **`input.json`** - Your task/question configuration (create this)
- **`output.json`** - Analysis results (generated automatically)
- **`pdfs/`** - Folder for your PDF files (create this)

---

## 🤝 License & Contributing

This script is provided for educational and research purposes. Feel free to:
- Adapt for your specific use cases
- Add support for other file formats
- Improve section detection algorithms
- Enhance similarity matching
- Share improvements with the community

---

**🚀 Universal Document Analysis - Adaptable to Any Domain!**

*Made to understand what you're looking for in any type of document.*
