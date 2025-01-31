import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from typing import Dict, List, Optional

class NGOScraper:
    def __init__(self, base_url: str, ngo_name: str):
        self.base_url = base_url
        self.ngo_name = ngo_name
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        self.data = []

    def clean_text(self, text: Optional[str]) -> str:
        if not text:
            return ''
        return ' '.join(text.strip().split())

    def extract_contact_details(self, soup: BeautifulSoup) -> Dict[str, str]:
        contact_info = {'address': '', 'phone': '', 'email': ''}
        contact_div = soup.find('div', class_='con-com home-list-pop list-spac')
        if contact_div:
            address_element = contact_div.find('p')
            if address_element:
                contact_info['address'] = self.clean_text(address_element.text)
            phone_element = contact_div.find('a', href=re.compile('tel:'))
            if phone_element:
                contact_info['phone'] = self.clean_text(phone_element.text)
            email_element = contact_div.find('a', href=re.compile('mailto:'))
            if email_element:
                contact_info['email'] = self.clean_text(email_element.text)
        return contact_info

    def extract_services(self, soup: BeautifulSoup) -> List[str]:
        services = []
        service_divs = soup.find_all('div', class_='hom-pro')
        for service_div in service_divs:
            service_name_element = service_div.find('h4')
            if service_name_element:
                services.append(self.clean_text(service_name_element.text))
        return services

    def scrape_website(self) -> bool:
        try:
            time.sleep(2)
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            main_soup = BeautifulSoup(response.text, 'html.parser')
            contact_url = f"{self.base_url}/contact_us"
            contact_response = requests.get(contact_url, headers=self.headers)
            contact_soup = BeautifulSoup(contact_response.text, 'html.parser')
            ngo_data = {
                'NGO Name': self.ngo_name,
                'Website': self.base_url,
                'Services': self.extract_services(main_soup),
                'Contact Details': self.extract_contact_details(contact_soup)
            }
            self.data.append(ngo_data)
            return True
        except Exception:
            return False

    def save_to_excel(self, filename: str = 'ngo_data.xlsx'):
        if not self.data:
            return
        flattened_data = []
        for entry in self.data:
            flat_entry = {
                'NGO Name': entry['NGO Name'],
                'Website': entry['Website'],
                'Address': entry['Contact Details']['address'],
                'Phone Number': entry['Contact Details']['phone'],
                'Email': entry['Contact Details']['email'],
                'Services': '; '.join(entry['Services'])
            }
            flattened_data.append(flat_entry)
        df = pd.DataFrame(flattened_data)
        df.to_excel(filename, index=False)

def main():
    ngo_url = 'https://y4d.ngo'
    ngo_name = 'Youth For Development (Y4D)'
    scraper = NGOScraper(ngo_url, ngo_name)
    if scraper.scrape_website():
        scraper.save_to_excel()

if __name__ == "__main__":
    main()
