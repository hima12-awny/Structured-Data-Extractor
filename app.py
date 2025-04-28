import streamlit as st
import json
import time
from typing import Dict, List

# Import custom modules
from multi_schema_generator import MultiSchemaJSONConverter
from web_to_md import WebToMarkdown
from utilities import is_url_or_search_query, SourceType
from info_get_gemini import GeminiAPIClient


class InfoExtractor:
    """Main application class for extracting structured information from web pages and search queries."""

    def __init__(self) -> None:
        """Initialize the application state and dependencies."""
        # Configure the Streamlit page
        st.set_page_config(
            page_title="Structured Data Extractor",
            page_icon="🔍",
            layout="wide"
        )

        # Initialize session state
        self._initialize_session_state()

        # Render the UI
        self._render_ui()

    def _initialize_session_state(self):
        """Initialize all required session state variables."""
        if "pages_content" not in st.session_state:
            st.session_state.pages_content = {}

        if "extracted_info" not in st.session_state:
            st.session_state.extracted_info = {}

        if "web_extractor" not in st.session_state:
            st.session_state.web_extractor = WebToMarkdown()

        if "gemini_api_key" not in st.session_state:
            st.session_state.gemini_api_key = ""

        if "gemini_agent" not in st.session_state:
            st.session_state.gemini_agent = None

        # Timing information
        if "fetch_timing" not in st.session_state:
            st.session_state.fetch_timing = {}

        if "extract_timing" not in st.session_state:
            st.session_state.extract_timing = {}

        # Development mode flag
        st.session_state.dev_mode = True

    def _render_ui(self):
        """Render the main user interface."""

        col1, col2 = st.columns(
            [1, 10], vertical_alignment='center', gap='small')

        with col1:
            st.image("gemini-color.svg", width=150)

        with col2:
            st.title("Structured Data Extractor with Gemini API")
            st.subheader(
                "Convert web content and search results into structured JSON with AI")

        st.html("<br><br>")

        with st.sidebar:
            with st.container(border=True):
                st.subheader("API Keys Configuration")
                st.caption("Enter your API keys for Gemini and Groq services")

                # Input fields for API keys
                gemini_api_key = st.text_input(
                    label="Gemini API Key",
                    type="password",
                    placeholder="Enter your Gemini API key",
                )

                # Save API keys in session state
                if gemini_api_key:
                    st.session_state.gemini_api_key = gemini_api_key

                # Add a button to set or initialize agents
                if st.button("Set Agents", use_container_width=True,):
                    if st.session_state.gemini_api_key:

                        st.session_state.gemini_agent = GeminiAPIClient(
                            api_key=st.session_state.gemini_api_key)
                        st.success("Gemini agent initialized successfully")
                    else:
                        st.error("Gemini API key is missing")

        # Create a two-column layout
        left_col, right_col = st.columns(2)

        # Left column: Source input and data extraction
        with left_col:
            self._render_source_input_section()

        # Right column: Schema configuration
        with right_col.container(border=True):
            MultiSchemaJSONConverter()

    def _render_source_input_section(self):
        """Render the section for inputting URLs and search queries."""
        with st.container(border=True):
            st.subheader("Data Sources")
            st.caption("Enter URLs or search queries (one per line)")

            # Input for URLs and search queries
            info_sources = st.text_area(
                label="Enter URLs or search queries to extract information from",
                height=200,
                placeholder="https://example.com\nwhat is quantum computing\nhttps://another-site.org"
            )

            # Process the input
            info_sources_list = self._process_input_sources(info_sources)

            # Action buttons
            col1, col2 = st.columns(2)

            fetch_content = col1.button(
                "Fetch Content",
                use_container_width=True,
                disabled=len(info_sources_list) == 0
            )

            extract_info = col2.button(
                "Extract Structured Data",
                use_container_width=True,
                disabled=len(
                    info_sources_list) == 0 or "final_response_schema" not in st.session_state
            )

            # Display retrieved content
            if fetch_content or len(st.session_state.pages_content) > 0:
                self._display_retrieved_content(
                    info_sources_list, fetch_content)

            # Extract and display structured information
            if extract_info or len(st.session_state.extracted_info) > 0:

                if st.session_state.gemini_agent is None:
                    st.error(
                        "Gemini agent is not initialized. Please set the API key and initialize the agent.")

                else:
                    self._display_extracted_info(
                        info_sources_list, extract_info)

    def _process_input_sources(self, input_text: str) -> List[str]:
        """Process the input text area and return a list of unique, non-empty sources."""
        sources = input_text.splitlines()
        unique_sources = []

        for source in sources:
            source = source.strip()
            if source and source not in unique_sources:
                unique_sources.append(source)

        if unique_sources:
            st.caption(f"Found {len(unique_sources)} unique sources")

        return unique_sources

    def _display_retrieved_content(self, sources: List[str], should_fetch: bool):
        """Display the retrieved content for each source."""
        with st.container(border=True):
            st.subheader("Retrieved Content")

            total_fetch_time = 0
            sources_fetched = 0
            total_fetch_time = 0.0

            for source in sources:
                # If content already exists or we should fetch new content
                if source in st.session_state.pages_content or should_fetch:
                    if should_fetch and source not in st.session_state.pages_content:
                        source_type = is_url_or_search_query(source)

                        if source_type == SourceType.URL:
                            with st.spinner(f"Fetching content from {source}"):
                                start_time = time.time()
                                content = st.session_state.web_extractor.from_url(
                                    source)
                                end_time = time.time()

                                fetch_time = end_time - start_time
                                st.session_state.fetch_timing[source] = fetch_time

                                st.session_state.pages_content[source] = content

                # Display content for URLs
                if source in st.session_state.pages_content and is_url_or_search_query(source) == SourceType.URL:
                    fetch_time = st.session_state.fetch_timing.get(
                        source, 0)
                    fetch_time_str = f" (fetched in {fetch_time:.2f}s)" if fetch_time > 0 else ""

                    with st.expander(f"Content from {source}{fetch_time_str}"):
                        st.text_area(
                            label="Retrieved content",
                            value=st.session_state.pages_content.get(
                                source, "No content retrieved"),
                            height=200,
                            key=f"content_{source}"
                        )
                    sources_fetched += 1
                    total_fetch_time += st.session_state.fetch_timing[source]

                # Display placeholder for search queries
                if is_url_or_search_query(source) == SourceType.SEARCH_QUERY:
                    with st.expander(f"Search query: {source}"):
                        st.info(
                            "Content will be retrieved during extraction")

            # Display total fetch time
            if sources_fetched > 0:
                st.info(
                    f"📊 Total time for fetching {sources_fetched} sources: {total_fetch_time:.2f} seconds (avg: {total_fetch_time/sources_fetched:.2f}s per source)")

    def _display_extracted_info(self, sources: List[str], should_extract: bool):
        """Extract and display structured information for each source."""
        with st.container(border=True):
            st.subheader("Extracted Structured Data")

            # Check if we have a schema defined
            if should_extract and "final_response_schema" not in st.session_state:
                st.error(
                    "Please define a schema in the right panel before extracting data")
                return

            total_extract_time = 0
            sources_extracted = 0

            # Process each source
            for source in sources:
                # Extract information if needed
                if should_extract and source not in st.session_state.extracted_info:
                    source_type = is_url_or_search_query(source)

                    if source_type == SourceType.URL:
                        with st.spinner(f"Extracting data from {source}", show_time=True):
                            start_time = time.time()
                            result = self._extract_from_url(source)
                            end_time = time.time()

                            extract_time = end_time - start_time
                            st.session_state.extract_timing[source] = extract_time

                            st.session_state.extracted_info[source] = result
                    else:  # Search query
                        with st.spinner(f"Processing query (Searching/Extracting) data for '{source}'", show_time=True):
                            start_time = time.time()
                            result = self._extract_from_query(source)
                            end_time = time.time()

                            extract_time = end_time - start_time
                            st.session_state.extract_timing[source] = extract_time

                            st.session_state.extracted_info[source] = result

                # Display extracted information
                if source in st.session_state.extracted_info:
                    extract_time = st.session_state.extract_timing.get(
                        source, 0)
                    extract_time_str = f" (extracted in :blue[{extract_time:.2f}s])" if extract_time > 0 else ""

                    with st.expander(f"Structured data from :blue[{source}]{extract_time_str}"):
                        st.json(st.session_state.extracted_info[source])

                        # Add delete button for each extracted item
                        if st.button(f"Delete Extracted Data for {source}", key=f"delete_{source}"):
                            del st.session_state.extracted_info[source]
                            if source in st.session_state.extract_timing:
                                del st.session_state.extract_timing[source]
                            st.success(f"Deleted extracted data for {source}")
                            st.rerun()

                    total_extract_time += st.session_state.extract_timing[source]
                    sources_extracted += 1

            # Display total extraction time
            if len(st.session_state.extracted_info) > 0:
                avg = total_extract_time / sources_extracted
                st.info(
                    f"📊 Total time for extracting {sources_extracted} sources: {total_extract_time:.2f} seconds (avg: {avg:.2f}s per source)")

            # Add download and clear buttons
            if st.session_state.extracted_info:
                self._add_data_management_buttons()

    def _extract_from_url(self, url: str) -> Dict:
        """Extract structured information from a URL using the Gemini agent."""
        response_schema = st.session_state.get("final_response_schema")

        # Get or fetch the content
        if url not in st.session_state.pages_content:
            content = st.session_state.web_extractor.from_url(url)
            st.session_state.pages_content[url] = content
        else:
            content = st.session_state.pages_content[url]

        # Extract structured information
        results = st.session_state.gemini_agent.query(response_schema, content)
        return results

    def _extract_from_query(self, query: str) -> Dict:
        """Extract structured information from a search query using the Groq agent."""
        response_schema = st.session_state.get("final_response_schema")

        results = st.session_state.gemini_agent.query_with_search(
            response_schema, query)
        return results

    def _add_data_management_buttons(self):
        """Add buttons for downloading and clearing extracted data."""
        schema = st.session_state.get("final_response_schema")
        schema_title = schema.get('title', 'data') if schema else 'data'

        col1, col2 = st.columns(2)

        with col1:
            download_popover = st.popover(
                "Download Data",
                icon=":material/download:",
                use_container_width=True
            )

            with download_popover:
                output_filename = f"extracted_{schema_title.lower()}.json"

                st.download_button(
                    "Download as Dictionary",
                    data=json.dumps(st.session_state.extracted_info, indent=2),
                    file_name=output_filename,
                    mime="application/json",
                    use_container_width=True
                )

                st.download_button(
                    "Download as List",
                    data=json.dumps(
                        list(st.session_state.extracted_info.values()), indent=2),
                    file_name=output_filename,
                    mime="application/json",
                    use_container_width=True
                )

        with col2:
            if st.button("Clear Extracted Data", use_container_width=True):
                st.session_state.extracted_info = {}
                st.session_state.extract_timing = {}
                st.rerun()


# Run the application
if __name__ == "__main__":
    InfoExtractor()
