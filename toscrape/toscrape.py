import pandas as pd
from bs4 import BeautifulSoup as bs
import logging
import requests
import json

logger = logging.getLogger(__name__)


class ToScrape:
    def __init__(self, url_pgn, url_pages, book_data):
        self.url_pgn = url_pgn
        self.url_pages = url_pages
        self.book_data = book_data

        def __repr__(self):
            return f"{self.url}, {self.book_data}"
        
        def __str__(self):
            return f"{self.url}, {self.book_data}"

    def get_page_numbers(self):
        soup = bs(requests.get(self.url_pgn).text, 'html.parser')
        return soup.find('li', class_='current').text.split("of")[1].strip()
    
    def get_book_soup(self):
        book_soup = bs(requests.get(self.url_pages.format(index)).text, 'html.parser')
        book_tags = book_soup.find('ol', class_='row').find_all('li')
        return book_tags
    
    def glean_book_details(self, book_tags):
        try:
            for index, tag in enumerate(book_tags):
                self.book_data = self._get_star_rating(tag)
                self.book_data = self._get_image_url(tag)
                self.book_data = self._get_book_description_url(tag)
                self.book_data = self._get_book_description(tag)
                self.book_data = self._get_book_price(tag)
                self.book_data = self._get_stock_availability(tag)
            return self.book_data
        except Exception as e:
            print(e)

    def _get_stock_availability(self, tag):
        try:
            is_available = tag.find('p', class_="instock availability").text.strip()
            if is_available == 'In stock': 
                self.book_data['in_stock'].append(True)
            else:
                self.book_data['in_stock'].append(False)
        except Exception as e:
            self.book_data['in_stock'].append(None)
        finally:
            return self.book_data

    def _get_book_price(self, tag):
        try:
            book_price = tag.find('p', class_='price_color').text.strip()
            self.book_data['price'].append(book_price)
        except Exception as e:
            self.book_data['price'].append(None)
        finally:
            return self.book_data

    def _get_star_rating(self, tag):
        try:
            star_rating = tag.find('p')['class'][1]
            self.book_data['rating'].append(star_rating)
        except Exception as e:
            self.book_datap['rating'].append(None)
        finally:
            return self.book_data

    def _get_image_url(self, tag):
        try:
            image_url = self.url_pgn + tag.find('img')['src'].replace("..", "")
            book_name = tag.find('img')['alt']
        except Exception as e:
            self.book_data['image_url'].append(None)
            self.book_data['book'].append(None)
        else:
            self.book_data['image_url'].append(image_url)
            self.book_data['book'].append(book_name)
        finally:
            return self.book_data

    def _get_book_description(self, tag):
        desc_resp = requests.get(self.book_data['description_url'][::-1][0])
        desc_soup = bs(desc_resp.text, 'html.parser')
        try:
            book_desc = desc_soup.find('div', 
                    {'id':'product_description'}).findNext('p').text.strip()
            self.book_data['description'].append(book_desc)
        except Exception as e:
            self.book_data['description'].append(None)
        finally:
            return self.book_data

    def _get_book_description_url(self, tag):
        try:
            description_url = self.url_pgn + "/catalogue/"+ tag.find('a')['href']
            self.book_data['description_url'].append(description_url)
        except Exception as e:
            self.book_data['description_url'].append(None)
        finally:
            return self.book_data


if __name__ == '__main__':

    with open('../config.json') as bookjson:
        toScrapeData = json.load(bookjson)
    bookScrape = toScrapeData['toscrape']

    toscrape=ToScrape(bookScrape['url_pgn'], bookScrape['url_books'],
                      bookScrape['book_details'])

    max_pgn = int(toscrape.get_page_numbers())
    #max_pgn = 10
    try:
        for index in range(1, max_pgn+1):
            if index % 10 == 0:
                print(f"Books scraped till page {index} out of {max_pgn}")
            books = toscrape.get_book_soup()
            book_d = toscrape.glean_book_details(books)
        df = pd.DataFrame(book_d)
        print(df.info())
        df.to_csv(bookScrape['to_csv_path'])
    except Exception as e:
        for each, value in book_d.items():
            print(each, len(value))


