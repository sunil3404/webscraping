import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import json
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

import logging

class Quotes:

    def __init__(self, quote_url, quote_data):
        self.quote_url = quote_url
        self.quote_data = quote_data

    def get_soup(self, pgindex):
        response = requests.get(self.quote_url + "page/" + str(pgindex) +"/")
        return bs(response.text, 'html.parser')

    def get_quote(self, tag):
        quote = tag.find("span", class_="text").text.strip()
        self.quote_data['quote'].append(quote)
        return self.quote_data

    def get_author(self, tag):
        author = tag.find("small", class_="author").text.strip()
        self.quote_data['author'].append(author)
        return self.quote_data

    def get_author_details(self, tag):
        author_url = tag.find("small", class_="author").next_sibling.next_sibling['href']
        author_soup = bs(requests.get(self.quote_url + author_url).text, "html.parser")
        dob = author_soup.find("span", class_="author-born-date").text.strip()
        born_location = author_soup.find("span", class_="author-born-location").text.strip()
        about_author = author_soup.find("div", class_="author-description").text.strip()
        self.quote_data['author_desc'].append(about_author)
        self.quote_data['author_loc'].append(born_location)
        self.quote_data['author_dob'].append(dob)
        return self.quote_data
        

    def get_tags(self, tag):
        try:
            tags = tag.find("meta", class_="keywords")['content']
            self.quote_data['tags'].append(tags)
        except Exception as e:
            print(tag)
        finally:
            return self.quote_data

    def process_soup(self, all_quotes):
        try:
            for quote in all_quotes:
                self.quote_data = self.get_quote(quote)
                self.quote_data = self.get_author(quote)
                self.quote_data = self.get_tags(quote)
                self.quote_data = self.get_author_details(quote)
                
        except Exception as e:
            logging.debug(quote)
        finally:
            return self.quote_data
            

if __name__ == "__main__":
    
    with open('../config.json') as quote_json:
        quote_data = json.load(quote_json)['quotes']

    quote = Quotes(quote_data["url_quotes"], quote_data['quotes'])
    count = 1

    #with ThreadPoolExecutor(max_workers=5) as executor:
    #    url = {executor.submit(quote.get_soup, count): count for count in range(1, 12)}

    #    for result in concurrent.futures.as_completed(url):
    #        print(result.result())
    #        

    try:
        while count < 11:
            pg_soup = quote.get_soup(count)
            all_quotes_soup = pg_soup.find_all("div", class_="quote")
            quote_df = quote.process_soup(all_quotes_soup)
            count = count + 1
        df = pd.DataFrame(quote_df)
        df.to_csv(quote_data['to_csv_path'])
    except Exception as e:
        logging.debug(count)

