import re
import scrapy
from scrapy import Spider
from goodreads25.items import goodreads25Item
from scrapy.http.request import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.exporters import CsvItemExporter

class goodreads25_spider(Spider):
	## The spider start page is the home page for a goodreads list
	## About 200 books/author were scraped per list
	name = 'goodreads25_spider'
	allowed_urls = ['https://www.goodreads.com/']
	start_urls = ['https://www.goodreads.com/list/popular_lists?page=1']
	
	def parse(self,response):
		print('retrieving book list urls')
		#retrieves urls for result pages of most popular lists
		list_urls = ['https://www.goodreads.com/list/popular_lists?page={}'.format(x) for x in range(1,7000)]
		for url in list_urls[80:100]: #for url in list_urls[:20]: , new statement will be for url in list_urls[20:]:
			print(url)
			yield Request(url=url,callback=self.parse_list)

	def parse_list(self,response):
		#retrieves url for each list
		list_links= response.xpath('/html/body/div[2]/div[3]/div[1]/div[1]/div[2]//@href').extract()
		list_links=list_links[1:-12]
		list_links = list(set(list_links))
	#for loop to scrape each list
		for url in list_links[:]:
			print(url)
			yield Request(url='https://www.goodreads.com'+url,callback=self.parse_result_page)
	

	def parse_result_page(self, response):
	# This fucntion parses the search result page for the book urls
	## A for loop was created to grab each url and score
		book_urls = response.xpath('//div[@id="all_votes"]/table//td/a/@href').extract()
		for i,v in enumerate(book_urls):
			print("I'm getting the urls for the books")
			#This extracts that url of the book
			
			score_ = response.xpath('//span[@class="smallText uitext"]/a/text()').extract()
			score_=score_[0::2]
			score_ = list(map(lambda x: str(x[7:]),score_))
			score_ = list(map(lambda x: x.replace(',',''),score_))
			print('i printed score')

			print('_' * 50)
			#retrieves score for each book
			score_=list(map(lambda x: x.replace('score:','').strip(),score_))
			score_=list(map(lambda x: x.replace(',',''),score_))
			score = score_[i]
			print(score)
		
			print(v)
			
			yield Request(url='https://www.goodreads.com' + v, callback=self.parse_book_page, meta={'score':score})
	def parse_book_page(self, response):
		#scrapes the book pages
		score = response.meta.get('score')
		print("I'm scraping the book pages and each score")
		#retrieves book title
		book_title = response.xpath('//*[@id="bookTitle"]/text()').extract_first()
		
		#retrieves url of author page, which is where it will go next
		author_page_url = response.xpath('//*[@id="aboutAuthor"]/div[2]/div/div[1]/div[1]/div[2]/div[1]/a/@href').extract()
		author_page_url=str(author_page_url)
		author_page_url=author_page_url.replace('[','')
		author_page_url=author_page_url.replace(']','')
		author_page_url=author_page_url.replace(author_page_url[0:1],'')
		print(author_page_url)
		#retrieves url of current book page
		book_url = response.xpath('//link[@rel="canonical"]/@href').extract()
		book_url2= str(book_url)
		book_url2=book_url2.replace('[','')
		book_url2=book_url2.replace(']','')
		book_fullurl=book_url2.replace(book_url2[0:1],'')
		#retrieves book id, which is just an index that goodreads uses
		book_id = str(book_url)
		book_id = book_id[book_id.index('/show/')+6:]
		stoppers = ['.','-']
		for stopper in stoppers:
			if stopper not in book_id: #if there is no puncuattion in the book id
				continue				## then continue
			else:
				end_index = book_id.index(stopper) #get the index of the puncuation
				book_id = book_id[:end_index]		## and retrieve all text after that

		#retrieves author_name
		author_name = response.xpath('//*[@id="aboutAuthor"]/div[2]/div/div[1]/div[1]/div[2]/div[1]/a/text()').extract_first()


		#prints progerss message for the user
		print('	....now grabbing url, id, number of pages, ratings, reviews, and genre')
		print('Currently scraping: ' + book_title + ' by ' + author_name)
		
		#retrieves both the number of ratings and reivews for each book and average rating
		ratings_and_reviews = response.xpath('//a[@class="gr-hyperlink"]/meta/@content').extract()
		num_ratings = ratings_and_reviews[0]
		num_reviews = ratings_and_reviews[1]
		book_average_rating = response.xpath('//span[@itemprop="ratingValue"]/text()').extract_first()
		
		#returns a numeric value for the number of pages
		pages = response.xpath('//span[@itemprop="numberOfPages"]/text()').extract_first()
		pages = pages.replace('pages','').strip()

		#selects genre with most users who read this book
		top_genres = response.xpath('//div[@class="stacked"]//a/text()').extract()
		genre_1 = top_genres[1]
		genre_2 = top_genres[3]
		genre_2 = str(genre_2)
		if bool(re.search(r'\d', genre_2)) == True:
			genre_2 = top_genres[4]
			if genre_2 == '[]':
				genre_2 == top_genres[3]
			else:
				genre_2=top_genres[4]
		else:
			genre_2 = top_genres[3]

		print('-'* 40 )
		#returns publish date of book, conditions were needed because goodreads commonly
		#lists multiple dates, especially if it's an older book
		publish_date = response.xpath('//*[@id="details"]/div[2]/nobr/text()').extract()
		publish_date = str(publish_date)
		if publish_date != '[]':
			publish_date = response.xpath('//*[@id="details"]/div[2]/nobr/text()').extract()
			publish_date=str(publish_date)
			start=publish_date.index("published") +9
			end=publish_date.index(")")
			publish_date = publish_date[start:end]
		else:
			publish_date = response.xpath('//*[@id="details"]/div[2]/text()').extract_first()
			publish_date=str(publish_date)
			publish_date = publish_date.replace('       ','')
			publish_date = publish_date.replace('\n','')
			publish_date = publish_date.split(' ')
			publish_date = publish_date[8]
		
			##all variables defined in this function were yielded into a meta dictionary so that
			## they could be yieled into a csv later
		yield Request(url='https://www.goodreads.com/' + author_page_url, callback=self.parse_author_page,
			meta={'book_title': book_title,'author_name': author_name, 'author_page_url': author_page_url,
			'book_fullurl':book_fullurl,'book_id': book_id,'num_ratings':num_ratings,
			'num_reviews':num_reviews,'book_average_rating':book_average_rating,'pages':pages,'genre_1':genre_1,
			'genre_2':genre_2,'publish_date':publish_date, 'score':score
			})

	def parse_author_page(self,response):
		###
		# list_links = response.meta.get('list_links')
		
		# list_title = response.meta.get('list_title')
		print('scraping the author page')
		#returns the url page for the author and his/her respective goodreads id
		author_page_url = response.xpath('.//head[@prefix="og: http://ogp.me/ns# fb: http://ogp.me/ns/fb# good_reads: http://ogp.me/ns/fb/good_reads#"]/link/@href').extract()[2]
		author_id=author_page_url[author_page_url.index('/show/')+6:]
		author_id = author_id[:author_id.index('.')]
		author_id
		
		#retrieves the top genres that author is involved in
		author_genres = response.xpath('//div[@class="rightContainer"]//@href').extract()[0:3]
		#only keep the linkes that have 'genre' in them which was the parent
		#directory of the target value
		lister = [item for item in author_genres if 'genres' in item]
		author_genres=""

		for item in lister:
			index = item.index('genres/')+7 ##grabs the genre by indexing 'genres/'
			item=item[index:]
			author_genres+=item + ' '
		author_genres=author_genres.split(' ') #converts it into a list
		if len(author_genres) == 1:
			author_genres=author_genres(',','') #removes comma for single element
		else:
			pass

		print('top author genres are {}'.format(author_genres))

		#retrieve bithplace location of author
		birthplace = response.xpath('//div[2]/div[3]/div[1]/div[1]/div[3]/div[2]/text()').extract()[4]
		birthplace = str(birthplace)
		birthplace = birthplace.replace('in ','')
		## this everything after the last comma, which is the country
		if ',' in birthplace:
			end = birthplace.rfind(',') + 2
			birthplace = birthplace[end:]
		else:
			birthplace = birthplace
			birthplace
		birthplace = birthplace.replace('The','')

		#average rating from all book written
		author_average_rating = response.xpath('//span[@itemprop="ratingValue"]/text()').extract()
		author_average_rating = str(author_average_rating)
		author_average_rating = author_average_rating[2:-2]
		#number of ratings and reviews
		author_rating_count = response.xpath('//span[@itemprop="ratingCount"]/text()').extract_first()
		author_rating_count= author_rating_count.replace('\n','').strip()
		author_rating_count=author_rating_count.replace(',','')
		author_review_count = response.xpath('//span[@itemprop="reviewCount"]/text()').extract_first()
		author_review_count= author_review_count.replace('\n','').strip()
		author_review_count=author_review_count.replace(',','')
		
		#returns a binary gender variable based on masculine/feminine pronouns used in bio
		author_bio = response.xpath('//div[@class="aboutAuthorInfo"]/span/text()').extract()
		author_bio=str(author_bio)
		female_count=author_bio.count(' she ') + author_bio.count(' her ')
		male_count=author_bio.count(' he ') + author_bio.count(' his ')
		author_gender = ""
		if female_count > male_count:
			author_gender = author_gender.replace("",'female')
		else:
			author_gender = author_gender.replace("",'male')

		#defines variable in the item class
		item = goodreads25Item()
		item['author_rating_count'] = author_rating_count
		item['author_review_count'] = author_review_count
		item['author_gender'] = author_gender
		item['author_average_rating'] = author_average_rating
		item['birthplace'] = birthplace
		item['author_id'] = author_id
		book_title = response.meta['book_title']
		item['book_title'] = book_title
		author_name = response.meta['author_name']
		item['author_name'] = author_name
		author_page_url = response.meta['author_page_url']
		item['author_page_url'] = author_page_url
		pages=response.meta['pages']
		item['pages'] = pages
		genre_1=response.meta['genre_1']
		item['genre_1'] = genre_1
		genre_2=response.meta['genre_2']
		item['genre_2'] = genre_2
		publish_date=response.meta['publish_date']
		item['publish_date'] = publish_date
		num_ratings = response.meta['num_ratings']
		item['num_ratings'] = num_ratings
		num_reviews=response.meta['num_reviews']
		item['num_reviews'] = num_reviews
		book_average_rating=response.meta['book_average_rating']
		item['book_average_rating'] = book_average_rating
		book_fullurl=response.meta['book_fullurl']
		item['book_fullurl'] = book_fullurl
		book_id = response.meta['book_id']
		item['book_id'] = book_id
		item['author_genres'] = author_genres
		score = response.meta['score']
		item['score'] = score

		yield item


