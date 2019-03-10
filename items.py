# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class goodreads25Item(scrapy.Item):
	# define the fields for your item here like:
	# name = scrapy.Field()
	
	pages = scrapy.Field()
	genre_1 = scrapy.Field()
	genre_2 = scrapy.Field()
	publish_date = scrapy.Field()
	num_ratings = scrapy.Field()
	num_reviews = scrapy.Field()
	book_average_rating = scrapy.Field()
	book_fullurl = scrapy.Field()
	book_id = scrapy.Field()
	book_title = scrapy.Field()
	author_name = scrapy.Field()
	author_gender = scrapy.Field()
	author_rating_count = scrapy.Field()
	author_review_count = scrapy.Field()
	author_average_rating = scrapy.Field()
	birthplace = scrapy.Field()
	author_id = scrapy.Field()
	author_page_url = scrapy.Field()
	author_genres = scrapy.Field()
	score = scrapy.Field()
	# list_links = scrapy.Field()
	# list_title = scrapy.Field()
