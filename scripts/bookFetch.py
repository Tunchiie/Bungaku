import pdfplumber
import re
import os
import json
import requests
import time
from google.cloud import translate_v2 as translate
from tqdm import tqdm
import logging

logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)


class bookFetch:
    def __init__(self):
        self.api_call_count = 0
        self.books_key = os.getenv("BOOKS_KEY")
        service_account_path = os.getenv(
            "SERVICE_ACCOUNT_PATH", "../bungaku_cloud_trans.json"
        )
        self.translator = translate.Client.from_service_account_json(
            service_account_path
        )

    def parse_single_entry(self, text, category, date):
        """
        Get the appropriate details for each book from the text passed
        and store it in a cache.
        """
        try:
            rank_match = re.match(r"(\d+)", text)
            rank = int(rank_match.group(1)) if rank_match else None

            title_match = re.search(r"\d+\s+(.*?), by", text)
            title = title_match.group(1).title() if title_match else None

            author_match = re.search(r"by (.*?)\.", text)
            author = author_match.group(1).strip() if author_match else None

            pub_match = re.search(r"\((.*?)\)", text)
            publisher = pub_match.group(1).strip() if pub_match else None

            rank_pairs = re.findall(r"(?:(\d{1,2})|--)\s+(\d{1,2})", text)
            if rank_pairs:
                first = rank_pairs[0]
                last_week_rank = (
                    int(first[0]) if first[0] and first[0].isdigit() else None
                )
                weeks_on_list = int(first[1])
            else:
                last_week_rank = None
                weeks_on_list = None

            text = re.sub(r"(?:(\d{1,2})|--)\s+(\d{1,2})", "", text, count=1).strip()

            return {
                "date": date,
                "category": category,
                "rank": rank,
                "title": title,
                "author": author,
                "publisher": publisher,
                "last_week_rank": last_week_rank,
                "weeks_on_list": weeks_on_list,
            }

        except Exception as e:
            print(f"Failed to parse entry: {e}")
            return None

    def parse_bestseller_pdf(self, filepath):
        """
        Store the ranked new york times bestsellers list for each file.
        Matching each entry to it's appropriate format and storing them correctly.
        """
        buffer = []
        entries = []

        date_match = re.search(r"s_(.*?)\.", filepath)
        date = date_match.group(1) if date_match else None
        category = None

        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                try:
                    text = page.extract_text()
                    lines = text.split("\n")[2:]

                    for line in lines:
                        line = line.strip()
                        category = re.match(
                            r"Week (.*?) Week On List$", line, re.IGNORECASE
                        )
                        if category:
                            category = category.group(1).strip().title()
                            continue

                        elif re.match(r"^\d{1,2}\s", line):
                            if buffer:
                                full_entry = " ".join(buffer)
                                parsed = self.parse_single_entry(
                                    full_entry, category, date
                                )
                                if parsed:
                                    entries.append(parsed)
                                buffer = []

                        buffer.append(line)
                except Exception as e:
                    print(f"Skipping bad page in {filepath}: {e}")
                    continue

            if buffer:
                full_entry = " ".join(buffer)
                parsed = self.parse_single_entry(full_entry, category, date)
                if parsed:
                    entries.append(parsed)

        cleaned_entries = [e for e in entries if e is not None]
        return cleaned_entries

    def parse_pdf(self, filepath):
        """
        Helper function to accelerate the parsing of all data.
        """
        try:
            return self.parse_bestseller_pdf(filepath)
        except Exception as e:
            print(f"Failed: {e}")
            return []

    def load_cache(self, path="../data/raw/books_cache.json"):
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def save_cache(self, cache, path="../data/raw/books_cache.json"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(cache, f)

    def clean_text(self, text):
        """
        Clean and normalize text by decoding unicode escape sequences,
        removing HTML tags, excess whitespace, and unnecessary newline characters.
        """

        if not text:
            return None
        text = text.encode().decode("unicode_escape")
        text = re.sub(r"<[^>]+>", "", text)
        text = text.replace("\n", " ").replace("\r", "").strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def book_detail_generator(self, batch):
        """
        Query the Google Books API to retrieve public metadata for each book in the dataset,
        including description, categories, and maturity rating.
        """

        cache = self.load_cache()

        base_url = "https://www.googleapis.com/books/v1/volumes"
        detailed_count = 0

        try:
            for entry in tqdm(batch):
                query = f"intitle:{self.clean_text(entry['title'])}"

                if entry["author"]:
                    query += f"+inauthor:{self.clean_text(entry['author'])}"

                key = f"{entry['title']} - {entry['author']}"

                if key in cache:
                    continue

                else:
                    books_url = (
                        f"{base_url}?q={query}&maxResults=1&key={self.books_key}"
                    )

                    if self.api_call_count >= 900:
                        return "Stop"
                    try:
                        self.api_call_count += 1
                        response = requests.get(books_url, timeout=10)
                        response.raise_for_status()
                    except requests.exceptions.RequestException as error:
                        print(f"Book couldn't be found: {error}")
                        continue
                    if response and response.ok:
                        try:
                            data = response.json()
                            if "items" in data:
                                result = data["items"][0]["volumeInfo"]
                                cache[key] = {
                                    "maturityRating": result.get("maturityRating")
                                    if "maturityRating" in result
                                    else None,
                                    "description": result.get("description")
                                    if "description" in result
                                    and result.get("language") == "en"
                                    else self.translate(result.get("description")),
                                    "categories": result.get("categories")
                                    if "categories" in result
                                    else None,
                                }
                        except Exception as error:
                            print(error)
                            continue
                    time.sleep(2)
                detailed_count += 1
                pass
        finally:
            if detailed_count > 0:
                self.save_cache(cache)
            return "Ok"

    def translate(self, description):
        """
        Detect the language of each description and translate it to English if necessary.
        """
        translator = self.translator
        description = self.clean_text(description)
        translation = None
        try:
            if description:
                detect_response = translator.detect_language(description)
                detect_lang = detect_response.get("language")
                if detect_lang and detect_lang != "en":
                    translation = translator.translate(
                        description, source_language=detect_lang, target_language="en"
                    )
                    if "translatedText" in translation:
                        return translation["translatedText"]
        except Exception as e:
            truncated_description = (
                description[:50] + "..."
                if description and len(description) > 50
                else description
            )
            print(f"Failed to translate: {e}. Description: {truncated_description}")
            return translation.get("translatedText")
