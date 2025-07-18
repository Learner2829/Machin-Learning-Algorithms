import os
import requests
from bs4 import BeautifulSoup
import shutil
import re
from PyPDF2 import PdfReader
import threading
import queue

# ========== CONFIGURATION ==========
BASE_URL = "https://cag.gov.in/en/audit-report?page="
NUM_PAGES = 242
DOWNLOAD_FOLDER = "cag_reports"
DEFAULT_FOLDER = "Central_Government"

# ========== SETUP ==========
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ========== QUEUE FOR THREADING ==========
file_queue = queue.Queue()

# ========== STATE EXTRACTION ==========
def extract_state_name(text):
    match = re.search(r"Government of\s+([A-Za-z\s]+)", text, re.IGNORECASE)
    if match:
        state = match.group(1).strip()
        return " ".join(state.split()).title()
    return None

# ========== PDF ORGANIZER ==========
def organize_worker():
    while True:
        file_path = file_queue.get()
        if file_path is None:
            break
        try:
            reader = PdfReader(file_path)
            text = ""
            for i in range(min(2, len(reader.pages))):
                text += reader.pages[i].extract_text() or ""
            state = extract_state_name(text)
        except Exception as e:
            print(f"⚠️ Failed reading {file_path}: {e}")
            state = None

        folder_name = state if state else DEFAULT_FOLDER
        state_folder = os.path.join(DOWNLOAD_FOLDER, folder_name)
        os.makedirs(state_folder, exist_ok=True)

        dest_path = os.path.join(state_folder, os.path.basename(file_path))
        shutil.move(file_path, dest_path)
        print(f"📦 Moved '{os.path.basename(file_path)}' → '{folder_name}'")
        file_queue.task_done()

# ========== DOWNLOAD FUNCTION ==========
def download_and_queue(pdf_url):
    filename = pdf_url.split("/")[-1].split("?")[0]
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    if os.path.exists(filepath):
        print(f"✅ Already exists: {filename}")
        file_queue.put(filepath)
        return

    print(f"⬇️  Downloading: {filename}")
    response = requests.get(pdf_url)
    if response.status_code == 200:
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"✅ Saved: {filename}")
        file_queue.put(filepath)
    else:
        print(f"❌ Failed: {pdf_url}")

# ========== SCRAPE FUNCTION ==========
def scrape_and_process():
    for page_num in range(49,NUM_PAGES):
        url = f"{BASE_URL}{page_num}"
        print(f"\n🌐 Scraping page {page_num + 1}: {url}")
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, "html.parser")

            links = soup.find_all("a", string=lambda text: text and "Download Full Report" in text)
            for link in links:
                href = link.get("href")
                if href and href.endswith(".pdf"):
                    full_url = f"https://cag.gov.in{href}" if href.startswith("/") else href
                    download_and_queue(full_url)

        except Exception as e:
            print(f"⚠️ Error on page {page_num}: {e}")

# ========== MAIN ==========
if __name__ == "__main__":
    # Start background worker thread
    worker_thread = threading.Thread(target=organize_worker, daemon=True)
    worker_thread.start()

    scrape_and_process()

    # Wait for all files to be organized
    file_queue.join()
    file_queue.put(None)
    worker_thread.join()

    print("\n✅ All reports downloaded and organized.")
