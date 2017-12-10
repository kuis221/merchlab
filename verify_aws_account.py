from scrapers.scraper_v3 import AmazonSearch

AMAZON_ACCESS_KEY = 'AKIAIQDFVQAP6TMLZWGA'
AMAZON_SECRET_KEY = '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'
AMAZON_ASSOC_TAG = 'kikim-20'

api = AmazonSearch(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)
print api.item_search_with_retry("dog", 1)
