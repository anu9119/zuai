import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client['ZuAI_DB']
collection = db['IAs_EEs']

# Helper function to clean text
def clean_text(text):
    return ' '.join(text.split()) if text else ''

# Scrape function
def scrape_nailib():
    url = "https://nailib.com/ia-sample/ib-math-ai-sl/63909fa87396d2b674677e94"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch URL: {url}, Status Code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extracting Data Points
    title = clean_text(soup.find('h1').get_text()) if soup.find('h1') else "Unknown Title"
    subject = "Math AI SL"  # Given directly in the task
    description = clean_text(soup.find('div', class_='description').get_text()) if soup.find('div', class_='description') else "No Description"

    sections = {}
    for section in soup.find_all('div', class_='section'):  # Assuming div class 'section' wraps sections
        heading = clean_text(section.find('h2').get_text()) if section.find('h2') else "Unknown Section"
        content = clean_text(section.get_text())
        sections[heading] = content

    word_count = int(clean_text(soup.find('span', class_='word-count').get_text()).split()[0]) if soup.find('span', class_='word-count') else 0
    read_time = clean_text(soup.find('span', class_='read-time').get_text()) if soup.find('span', class_='read-time') else "Unknown"
    
    file_link = soup.find('a', href=True)['href'] if soup.find('a', href=True) else "No File Link"
    publication_date = clean_text(soup.find('time', class_='pub-date').get_text()) if soup.find('time', class_='pub-date') else "Unknown Date"

    # Structuring Data for MongoDB
    data = {
        "title": title,
        "subject": subject,
        "description": description,
        "sections": sections,
        "word_count": word_count,
        "read_time": read_time,
        "file_link": file_link,
        "publication_date": publication_date if publication_date != "Unknown Date" else datetime.utcnow().strftime('%Y-%m-%d')
    }

    # Upsert into MongoDB
    collection.update_one({"title": title}, {"$set": data}, upsert=True)
    print(f"Data upserted for: {title}")

if __name__ == "__main__":
    scrape_nailib()
    print("Scraping and data insertion complete.")
