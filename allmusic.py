#!/usr/bin/env python

import re, urlparse, sys
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from time import sleep

class SpotifyAPI(object):
	def __init__(self):
		self.token = 'BQBquQ8CC3oH6XjzRe4uQAt0OJFXlUSzf7vd7kYdsgwP-2GO3lpay6vMlHsk3b6_Fw655fwNCYIIqR_5H20yRtYphZJ9FsReWqeg8HVbOQxZVPrWF7XZeVCDreNiJn4CJBIBtKYq-gT_oaulNwqTuxtAj9GKN_1a3y0yBDSa7PaShny8CAtDqiMGWf9umBAoLiZxnklnfBVdz7vfvAPEX3arBVzat3YuIXoZAPRrTOegfbIn9EBxptZOnstB828tC7jnqv1grkc-TkQ9JPUdEF1aF4iN1-8lq25D0YK-OLvT0wuxVlBx'

	def search(self, itemType, query):
		response = requests.get('https://api.spotify.com/v1/search', 
              params={'q': query, 'type': itemType}, 
              headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
              			'Accept' : 'application/json',
              			'Authorization' : 'Bearer ' + self.token})
		return response.json()

class AllMusicScraper(object):
	def __init__(self):
		self.timeout = 5
		self.spotify = SpotifyAPI()
		try:
			self.driver = webdriver.PhantomJS(service_args=['--load-images=no'])
			self.driver.set_window_size(1120, 550)
		except Exception as e:
			print 'failed to open a browser'
			print e
			self.log_error('failed_to_open_browser', str(e))

	def add_spotify_data(self, info, option, keyword):
		if option == 'artist':
			try:
				spotify_searched_artists = self.spotify.search('artist', keyword)['artists']['items']
				for artist in spotify_searched_artists:
					if info['name'].lower() == artist['name'].lower():
						info['spotify_genres'] = artist['genres']
						info['spotify_popularity'] = artist['popularity']
						info['spotify_id'] = artist['id']
						info['spotify_followers'] = artist['followers']['total']
						break

			except Exception as e:
				print 'failed to access to spotify API'
				print e
				self.log_error('spotify_album_search', str(e))

			try:
				for i in range(0, len(info['albums'])):
					spotify_searched_albums = self.spotify.search('album', info['albums'][i]['title'])['albums']['items']
					for spotify_album in spotify_searched_albums:
						if info['name'].lower() == spotify_album['artists'][0]['name'].lower():
							info['albums'][i]['spotify_album_type'] = spotify_album['album_type']
							info['albums'][i]['spotify_id'] = spotify_album['id']
							break

			except Exception as e:
				print 'failed to access to spotify API'
				print e
				self.log_error('spotify_album_search', str(e))
		else:
			print 'not yet'

		return info

	def scrape(self, option, keyword):
		if option == 'artist':
			link = self.scape_artist_link(keyword)
			info = self.scrape_info(link + '/biography')
			info['albums'] = self.scrape_albums(link + '/discography')
			info = self.add_spotify_data(info, 'artist', keyword)

		self.driver.quit()
		return info

	def scape_artist_link(self, artist):
		artist = artist.replace(' ', '+')
		link = 'http://www.allmusic.com/search/artists/' + artist
		s = self.load_page(link, 'div.info')
		r = re.compile(r'www\.allmusic\.com\/artist\/')

		artist_link = s.find('a', href= r)['href']
		return artist_link

	def scrape_info(self, link):
		s = self.load_page(link, 'div.text')

		try:
			name = s.find('h1', class_= 'artist-name').text.strip()
			description = s.find('p', class_ = 'biography').find('span').text.strip()
			bio = s.find('div', class_='text')
			
			[img.extract() for img in bio.findAll('img')]
			bio = bio.text.strip()
			re.sub(r'[\s\t\r\n ]+',' ',bio)

			info = {
					'name' : name,
					'description' : description,
					'bio' : bio
					}
			return info
		except Exception as e:
			print('failed to scrape artist\'s info.')
			print e
			self.log_error('failed_to_scrape', link)
			return None

	def scrape_albums(self, link):
		s = self.load_page(link, 'img.lazy')
		r = re.compile(r'year')

		try:
			albums = []

			for d in s.findAll('td', class_ = r ):
				tr = d.findParent('tr')
				td = tr.findAll('td')

				album = {}
				album['year'] = d.text.strip()
				album['cover'] = urlparse.urljoin(link, td[1].find('img')['data-original'])
				album['title'] = td[3].text.strip()
				album['label'] = td[4].text.strip()
				album['rating'] = self.to_int(td[6].find('span')['class'][1])
				album['rating_count'] = self.to_int(td[6].find('span', class_='avg-rating-count').text)
				albums.append(album)

			return albums

		except Exception as e:
			print('failed to scrape albums.')
			print e
			self.log_error('failed_to_scrape', link)

			return None
		

	def to_int(self, number):
		number = number.replace(r'[\.\,]', '')
		number = re.findall(r'\d+', number)[0]
		return int(number)

	def log_error(self, errorType, errorInfo):
		f = open('error.log', 'a')
		f.write(errorType + ', ' + errorInfo)
		f.close()

	def load_page(self, link, selector):
		self.driver.get(link)
		try:
			element_present = EC.presence_of_element_located((By.CSS_SELECTOR, selector))
			WebDriverWait(self.driver, self.timeout).until(element_present)
		except TimeoutException:
			print "Timed out waiting for page to load"
			self.log_error('timeout', link)
			
		except Exception as e:
			print e
			self.log_error('failed_to_load', link)
		
		try:
			s = BeautifulSoup(self.driver.page_source, "html.parser")
		except Exception as e:
			print e
			selflog_error('failed_to_parse', link)
			sys.exit(2)

		return s
		
def main(argv):
	if (len(argv) >= 2):
		option = argv[0]
		keyword = ' '.join(argv[1:])
	else:
		print 'usage : -option <keyword>'
		sys.exit(2)

	scraper = AllMusicScraper()
	if option == '-a':
		albums = scraper.scrape('artist', keyword)
		print albums
	else:
		print 'try -a <keyword>'

if __name__ == '__main__':
	sys.argv.pop(0)
	main(sys.argv)