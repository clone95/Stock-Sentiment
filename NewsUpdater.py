import pandas as pd
import requests
from MongOps import connect
import datetime, time
from GoogleNews import GoogleNews
from newspaper import Article

start_time = time.time()

class NewsUpdater():

    def __init__(self):

        # get selected stocks from file
        with open('selected_stocks.txt', 'r') as file:
            self.companies = file.readlines()
            self.companies = [tuple(x.strip().split(',')) for x in self.companies]

    def update_db(self):       

        for company in self.companies:
            updater = TickerUpdater(company)  
            updater.update_workflow()

class TickerUpdater():

    def __init__(self, company):
        print('Updating', company)
        # selected company
        self.ticker = company[0]
        self.company_name = company[1]
        # db connection
        self.db = 'advisor'
        self.collection = 'news'
        self.connection = connect(self.db, self.collection)
        # downalod time span 
        self.today = datetime.datetime.today
        self.history_start = datetime.datetime(2020, 9, 27)


    def update_workflow(self):

        all_articles = self.fetch_articles()
        valid_articles = self.remove_noise(all_articles)
        self.save_articles(valid_articles)


    def fetch_articles(self):

        # how many pages to scrape
        N_pages = 1
        links = []
        # how many days from last update
        # TODO: look for the last update datetime in the DB
        days_from_last_update = (datetime.datetime.today() - self.history_start).days
        # for each day between start date and today:
        for day in range(0, days_from_last_update + 1):
            download_date = self.history_start + datetime.timedelta(days=day)
            googlenews = GoogleNews(start=download_date.strftime("%m/%d/%Y"),end=download_date.strftime("%m/%d/%Y"))
            googlenews.search(self.ticker)
            # iterate N_pages of Google News
            for i in range(0, N_pages):
                googlenews.getpage(i)
                result = googlenews.result()
                links = links + result

        links = list(set([x['link'] for x in links]))
        
        # for each link (without dups) get the article and its metadata
        articles = []
        for link in links:
            try:
                downloaded = self.download_and_parse_article(link)
                articles.append(downloaded)
            except Exception as e:
                print(e)

        return articles

           

    def download_and_parse_article(self, link):

        article = Article(link)
        article.download()
        article.parse()
        article.nlp()
        # build a dict with the Article data
        article_item = {}
        # main data
        article_item['ticker'] = self.ticker
        article_item['title'] = article.title
        article_item['summary'] = article.summary
        article_item['text'] = article.text
        article_item['authors'] = article.authors
        article_item['url'] = article.url
        # additional metadata
        article_item['keywords'] = article.keywords
        article_item['meta_keywords'] = article.meta_keywords
        article_item['meta_lang'] = article.meta_lang
        article_item['publish_date'] = article.publish_date
        article_item['top_image'] = article.top_image
        print(type(article))
        return article_item


    def remove_noise(self, articles):
        return articles


    def save_articles(self, articles):
        
        print(type(articles))
        self.connection.insert_many(articles)
        print('Saving')