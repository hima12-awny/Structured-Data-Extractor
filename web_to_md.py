import urllib.request
from io import BytesIO
from docling.backend.html_backend import HTMLDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument
import time


class WebToMarkdown:
    def __init__(self):
        self.backend = None
        self.dl_doc = None

    def _get_webpage_content(self, url: str):
        return urllib.request.urlopen(url).read()

    def from_url(self, url: str) -> str:
        html_text = self._get_webpage_content(url)
        return self.convert_html(html_text)

    def from_url_list(self, urls: list[str]) -> dict:
        results = {}
        for url in urls:
            try:
                results[url] = self.from_url(url)
                time.sleep(1)  # To avoid hitting the API too fast
            except Exception as e:
                results[url] = str(e)
        return results

    def convert_html(self, page_html_content):
        """Convert HTML content to markdown.

        Args:
            page_html_content: HTML content of the page

        Returns:
            str: Markdown formatted content
        """

        if isinstance(page_html_content, str):
            page_html_content = page_html_content.encode('utf-8')

        in_doc = InputDocument(
            path_or_stream=BytesIO(page_html_content),
            format=InputFormat.HTML,
            backend=HTMLDocumentBackend,
            filename='webpage.html',
        )

        self.backend = HTMLDocumentBackend(
            in_doc=in_doc, path_or_stream=BytesIO(page_html_content))

        self.dl_doc = self.backend.convert()
        return self.dl_doc.export_to_markdown()
