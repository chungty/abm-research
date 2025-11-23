"""
Web scraping utilities for company websites and news sources
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import logging
import re
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class WebScraper:
    """Web scraper for company websites and news sources"""

    def __init__(self, timeout: int = 30):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None

        # Common headers to avoid bot detection
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers=self.headers
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def _get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Get and parse a web page"""
        if not self.session:
            raise RuntimeError("WebScraper not initialized. Use 'async with' context manager.")

        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    return BeautifulSoup(html, 'html.parser')
                else:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    async def scrape_company_about_page(self, domain: str) -> Dict[str, Any]:
        """Scrape company about/info page for firmographics"""
        logger.info(f"Scraping company info for {domain}")

        # Try common about page URLs
        about_urls = [
            f"https://{domain}/about",
            f"https://{domain}/about-us",
            f"https://{domain}/company",
            f"https://{domain}/info",
            f"https://www.{domain}/about",
            f"https://www.{domain}/about-us"
        ]

        company_data = {}

        for url in about_urls:
            soup = await self._get_page(url)
            if not soup:
                continue

            # Extract employee count
            employee_info = self._extract_employee_count(soup)
            if employee_info and 'employee_count' not in company_data:
                company_data['employee_count'] = employee_info

            # Extract data center locations
            locations = self._extract_locations(soup)
            if locations and 'data_center_locations' not in company_data:
                company_data['data_center_locations'] = locations

            # Extract facility capacity information
            capacity = self._extract_facility_capacity(soup)
            if capacity and 'facility_capacity' not in company_data:
                company_data['facility_capacity'] = capacity

            # Stop if we found good data
            if len(company_data) >= 2:
                break

        return company_data

    def _extract_employee_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract employee count from page content"""
        # Look for patterns like "500+ employees", "team of 200", etc.
        patterns = [
            r'(\d+)[\+\s]*employees',
            r'team of (\d+)',
            r'(\d+)[\+\s]*people',
            r'staff of (\d+)',
            r'(\d+)[\+\s]*team members'
        ]

        text = soup.get_text().lower()
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue

        return None

    def _extract_locations(self, soup: BeautifulSoup) -> List[str]:
        """Extract data center or office locations"""
        locations = []

        # Look for location indicators
        location_keywords = ['data center', 'datacenter', 'facility', 'office', 'location']
        city_patterns = [
            r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)*),\s*([A-Z]{2}|[A-Z][a-z]+)',  # City, State/Country
            r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\s+([A-Z]{2,3})',  # City State
        ]

        text = soup.get_text()

        # Find paragraphs or sections mentioning locations
        for keyword in location_keywords:
            if keyword in text.lower():
                # Extract cities near the keyword
                keyword_context = self._get_text_around_keyword(text, keyword, 200)
                for pattern in city_patterns:
                    matches = re.findall(pattern, keyword_context)
                    for match in matches:
                        location = f"{match[0]}, {match[1]}"
                        if location not in locations:
                            locations.append(location)

        return locations[:5]  # Limit to top 5 locations

    def _extract_facility_capacity(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract facility capacity information (MW, sq ft, etc.)"""
        # Look for capacity patterns
        patterns = [
            r'(\d+(?:\.\d+)?)\s*MW',
            r'(\d+(?:,\d+)*)\s*sq\.?\s*ft',
            r'(\d+(?:,\d+)*)\s*square feet',
            r'(\d+(?:\.\d+)?)\s*megawatts?'
        ]

        text = soup.get_text()
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)

        return None

    def _get_text_around_keyword(self, text: str, keyword: str, context_length: int) -> str:
        """Get text around a keyword for context extraction"""
        keyword_pos = text.lower().find(keyword.lower())
        if keyword_pos == -1:
            return ""

        start = max(0, keyword_pos - context_length // 2)
        end = min(len(text), keyword_pos + context_length // 2)
        return text[start:end]

    async def scrape_news_page(self, url: str) -> Dict[str, Any]:
        """Scrape a news article or press release"""
        logger.info(f"Scraping news page: {url}")

        soup = await self._get_page(url)
        if not soup:
            return {}

        # Extract article metadata
        article_data = {
            'url': url,
            'title': self._extract_title(soup),
            'date': self._extract_publish_date(soup),
            'content': self._extract_main_content(soup)
        }

        return article_data

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        # Try multiple selectors
        selectors = [
            'h1.entry-title',
            'h1.post-title',
            'h1.article-title',
            'h1',
            'title'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()

        return ""

    def _extract_publish_date(self, soup: BeautifulSoup) -> Optional[date]:
        """Extract publish date from article"""
        # Look for date patterns in various formats
        date_selectors = [
            'time[datetime]',
            '.published-date',
            '.post-date',
            '.article-date'
        ]

        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                date_str = element.get('datetime') or element.get_text()
                parsed_date = self._parse_date_string(date_str)
                if parsed_date:
                    return parsed_date

        # Look for date patterns in the text
        text = soup.get_text()
        date_patterns = [
            r'(\w+ \d{1,2}, \d{4})',  # January 15, 2024
            r'(\d{1,2}/\d{1,2}/\d{4})',  # 1/15/2024
            r'(\d{4}-\d{2}-\d{2})'  # 2024-01-15
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                parsed_date = self._parse_date_string(match.group(1))
                if parsed_date:
                    return parsed_date

        return None

    def _parse_date_string(self, date_str: str) -> Optional[date]:
        """Parse various date string formats"""
        date_formats = [
            '%B %d, %Y',  # January 15, 2024
            '%b %d, %Y',  # Jan 15, 2024
            '%m/%d/%Y',   # 1/15/2024
            '%Y-%m-%d',   # 2024-01-15
            '%Y-%m-%dT%H:%M:%S'  # ISO format
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue

        return None

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content"""
        # Try to find the main content area
        content_selectors = [
            '.entry-content',
            '.post-content',
            '.article-content',
            '.content',
            'article',
            '.main-content'
        ]

        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # Remove script and style elements
                for script in element(["script", "style"]):
                    script.decompose()
                return element.get_text().strip()

        # Fallback to body content
        body = soup.find('body')
        if body:
            return body.get_text()[:2000]  # Limit to first 2000 chars

        return ""

    async def search_company_newsroom(self, domain: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Search company newsroom for relevant articles"""
        logger.info(f"Searching newsroom for {domain}")

        # Try common newsroom URLs
        newsroom_urls = [
            f"https://{domain}/newsroom",
            f"https://{domain}/news",
            f"https://{domain}/press-releases",
            f"https://{domain}/blog",
            f"https://www.{domain}/newsroom",
            f"https://www.{domain}/news"
        ]

        articles = []

        for base_url in newsroom_urls:
            soup = await self._get_page(base_url)
            if not soup:
                continue

            # Find article links
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if not href:
                    continue

                # Make absolute URL
                full_url = urljoin(base_url, href)

                # Check if link text contains keywords
                link_text = link.get_text().lower()
                if any(keyword.lower() in link_text for keyword in keywords):
                    article_data = await self.scrape_news_page(full_url)
                    if article_data.get('title'):
                        articles.append(article_data)

            # Stop if we found articles
            if articles:
                break

        return articles[:10]  # Limit results