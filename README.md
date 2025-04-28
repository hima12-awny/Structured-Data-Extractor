# Structured Data Extractor

A powerful Streamlit application that extracts structured data from web pages and search queries using the Gemini API. This tool allows users to define custom data schemas and extract information in a structured JSON format, making it ideal for data collection, analysis, and integration tasks.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)](https://www.linkedin.com/in/ibrahim-awny/)
[![Gmail](https://img.shields.io/badge/Gmail-Email-red?logo=gmail)](mailto:hima12awny@gmail.com)


![Structured Data Extractor](https://github.com/yourusername/structured-data-extractor/raw/main/screenshots/app-preview.png)

## 🚀 Use Cases

- **Web Scraping with Structure**: Extract specific data points from websites in a structured format.
- **Research & Analysis**: Gather structured information about topics from multiple sources.
- **Content Aggregation**: Build datasets from web content with consistent schema.
- **Data Pipeline Creation**: Use as the first step in automated data collection workflows.
- **Knowledge Base Building**: Create structured knowledge bases from unstructured web content.
- **Competitive Analysis**: Extract structured information about competitors from their websites.
- **Educational Resources**: Gather structured data about educational platforms and courses.

## ✨ Features

- **Flexible Schema Definition**: Create and save custom JSON schemas for structured data extraction.
- **Dual Source Support**: Process both URLs and search queries.
- **Markdown Conversion**: Convert HTML content to Markdown for better processing.
- **Performance Metrics**: Track and display extraction performance times.
- **Gemini AI Integration**: Leverage Google's Gemini AI to understand content and extract data.
- **Export Options**: Download extracted data as dictionary or list format.
- **Schema Library**: Save and reuse schemas for future extractions.

## 🔧 Technical Architecture

The application consists of several components:

1. **Multi-Schema Generator** (`multi_schema_generator.py`): Visual schema builder for creating complex JSON schemas.
2. **Web-to-Markdown Converter** (`web_to_md.py`): Converts web page HTML to clean Markdown for better processing.
3. **Gemini API Client** (`info_get_gemini.py`): Interface with Google's Gemini AI for structured data extraction.
4. **Utilities** (`utilities.py`): Helper functions for URL/query detection and other common tasks.
5. **Main Application** (`app.py`): Streamlit interface and orchestration of the extraction pipeline.

## 📋 Requirements

- Python 3.11+
- Google Gemini API key [(get gemini api key)](https://aistudio.google.com/app/apikey) it is free!.
- Additional dependencies in `requirements.txt`

## 🛠️ Installation

1. Clone this repository
```bash
git clone https://github.com/yourusername/structured-data-extractor.git
cd structured-data-extractor
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
streamlit run app.py
```

## 🔍 How It Works

1. **Define Your Schema**: Use the schema builder on the right panel to create a structured data format.
2. **Add Data Sources**: Enter URLs or search queries in the left panel.
3. **Fetch Content**: For URLs, fetch and convert HTML to Markdown.
4. **Set Gemini API KEY**: in the sidebar set the Gemini api key to create the extractor agent.
5. **Extract Data**: Process content through Gemini API to extract structured information matching your schema.
6. **Export Results**: Download extracted data as JSON for further processing.

## 💻 Code Overview

### Schema Generation
The `MultiSchemaJSONConverter` class provides a visual interface for creating complex JSON schemas with nested objects, arrays, enums, and references.

```python
# Example schema results
schema = {
    "title": "Course",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "price": {"type": "number"},
        "topics": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["name", "description"]
}
```

### Web Content Processing
The `WebToMarkdown` class handles fetching web content and converting HTML to Markdown for better processing.

```python
# Example usage
converter = WebToMarkdown()
markdown_content = converter.from_url("https://example.com")
```

### Gemini API Integration
The `GeminiAPIClient` class provides methods to query the Gemini API with content and schemas.

```python
# Example usage
client = GeminiAPIClient(api_key="your_api_key")
results = client.query(schema, content)
```
### Search Query Handling
For search queries (as opposed to URLs), the application uses Gemini with Google Search Tool for grounding:

```python
# Using Gemini with Google Search for handling search queries
results = client.query_with_search(schema, search_query)
```
This method:

1. Detects when input is a search query rather than a URL
2. Utilizes Gemini's Google Search Tool capabilities to fetch relevant information
3. Grounds the AI's responses in current web content
4. Structures the search results according to your defined schema

The implementation in ```info_get_gemini.py``` configures the Gemini model with:

* System instructions for the search agent
* Google Search Tool integration
* Response formatting to match your schema

This approach ensures that even when users provide general topics rather than specific URLs, the application can still gather relevant structured data by leveraging Gemini's search capabilities.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgements

- [Streamlit](https://streamlit.io/) for the interactive web framework
- [Google Gemini API](https://ai.google.dev/) for the AI language capabilities
- [Docling](https://github.com/docling-project/docling) for HTML to Markdown conversion capabilities


## 📧 Contact

For questions or feedback, please open an issue on this repository.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)](https://www.linkedin.com/in/ibrahim-awny/)
[![Gmail](https://img.shields.io/badge/Gmail-Email-red?logo=gmail)](mailto:hima12awny@gmail.com)

---