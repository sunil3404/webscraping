from bs4 import BeautifulSoup as bs
import pandas as pd
import requests 
import json
import logging
import copy
import re
import traceback

logging.basicConfig(level=logging.DEBUG)


class IMDB():
    def __init__(self, url, movie_details):
        self.url = url
        self.movie_details = movie_details

    def get_movie_tags(self, response):
        soup = bs(response.text, 'html.parser')
        tags = soup.find_all("div", class_="lister-item-content")
        return tags
        
    def fetch_movies(self, start, movie_tags):
        try:
            response = requests.get(self.url.format(start))
            tags = self.get_movie_tags(response)
            movie_tags.extend(tags)
            return movie_tags
        except Exception as e:
            logging.debug(e)

    def process_soup(self, movie_tags):
        try:
            for index, tag in enumerate(movie_tags):
                self.movie_details = self._get_movie_title_and_year(tag)
                self.movie_details = self._get_movie_certificate(tag)
                self.movie_details = self._get_movie_runtime(tag)
                self.movie_details = self._get_movie_genre(tag)
                self.movie_details = self._get_movie_rating(tag)
                self.movie_details = self._get_movie_metascore(tag)
                self.movie_details = self._get_movie_description(tag)
                self.movie_details = self._get_movie_director_and_stars(tag)
                self.movie_details = self._get_movie_votes(tag)
                #break
        except Exception as e:
            logging.debug(e)
            logging.debug(index)
        return self.movie_details
    
    def _get_movie_votes(self, tag):
        monetary = tag.find_all('span', {'name': 'nv'})
        try:
            if len(monetary) == 1:
                self.movie_details['votes'].append(monetary[0].text.strip())
                self.movie_details['gross'].append(None)
                self.movie_details['top_250'].append(None)
            elif len(monetary) == 2:
                self.movie_details['votes'].append(monetary[0].text.strip())
                self.movie_details['gross'].append(monetary[1].text.strip())
                self.movie_details['top_250'].append(None)
            else:
                self.movie_details['votes'].append(monetary[0].text.strip())
                self.movie_details['gross'].append(monetary[1].text.strip())
                self.movie_details['top_250'].append(monetary[2].text.strip())
        except Exception as e:
            logging.debug(monetary)
        return self.movie_details

    def _get_movie_director_and_stars(self, tag):
        details = tag.find("p", { "class" : "" }).findAll("a", recursive=False)
        director = details[0].text
        stars = []
        for each in details[1:]:
            stars.append(each.text.strip())
        stars = "  ".join(stars)
        self.movie_details['director'].append(director)
        self.movie_details['stars'].append(stars)
        return self.movie_details

    def _get_movie_description(self, tag):
        description = tag.find_all('p', class_='text-muted')[1].text.strip()
        import string
        description = "".join([i for i in description if i not in string.punctuation])
        self.movie_details['description'].append(description)
        return self.movie_details

    def _get_movie_metascore(self, tag):
        try:
            metascore = tag.find('span', class_='metascore favorable').text.strip()
        except Exception as e:
            try:
                metascore = tag.find('span', class_='metascore mixed').text.strip()
            except Exception as e:
                self.movie_details['metascore'].append(None)
                return self.movie_details
        self.movie_details['metascore'].append(metascore)
        return self.movie_details
    
    def _get_movie_rating(self, tag):
        rating = tag.find('div', class_='inline-block ratings-imdb-rating').get('data-value') 
        self.movie_details['rating'].append(rating)
        return self.movie_details

    def _get_movie_genre(self, tag):
        genre = tag.find('span', class_='genre').text.strip()  
        self.movie_details['genre'].append(genre)
        return self.movie_details

    def _get_movie_runtime(self, tag):
        runtime = tag.find('span', class_='runtime').text.strip()
        self.movie_details['runtime'].append(runtime)
        return self.movie_details

    def _get_movie_certificate(self, tag):
        #import pdb;pdb.set_trace()
        try:
            certificate = tag.find('span', class_='certificate').text.strip()
            self.movie_details['certificate'].append(certificate)
        except Exception as e:
            self.movie_details['certificate'].append(None)
        return self.movie_details
    
    def _get_movie_title_and_year(self, tag):
        try:
            movie_name = tag.find('a').text.strip()
            year = re.findall("\d+", tag.find('h3').text.split("(")[1])[0]
            self.movie_details['movie'].append(movie_name)
            self.movie_details['year'].append(year)
        except Exception as e:
            year = re.findall("\d+", tag.find('h3').text)
            self.movie_details['movie'].append(movie_name)
            self.movie_details['year'].append(year[1])

        return self.movie_details

if __name__ == "__main__":
    
    with open("../config.json", 'r') as conf:
        data = json.load(conf)

    movie_tags = []
    try:
        for start in range(1, 902, 100):
            imdb = copy.deepcopy(IMDB(data['imdb']["url"], data['imdb']['movie_details']))
            movie_tags  = imdb.fetch_movies(start, movie_tags)
        final_output = imdb.process_soup(movie_tags)
        df = pd.DataFrame(final_output)
        df.to_csv(data['imdb']['to_csv_path'])
    except Exception as e:
        logging.debug("I am in the exception")
        logging.debug(e)



