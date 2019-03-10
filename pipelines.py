# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exporters import CsvItemExporter
import scrapy
from scrapy.item import Item, Field
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.item import Item, Field
from goodreads25.items import goodreads25Item

class Goodreads25Pipeline(object):
	def __init__(self):
		self.filename = 'IIIII0000.csv'
	def open_spider(self, spider):
		self.csvfile = open(self.filename, 'wb')
		self.exporter = CsvItemExporter(self.csvfile)
		self.exporter.start_exporting()
	def close_spider(self, spider):
		self.exporter.finish_exporting()
		self.csvfile.close()
	def process_item(self, item, spider):
		self.exporter.export_item(item)
		return item