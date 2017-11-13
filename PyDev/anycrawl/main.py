from scrapy import cmdline
#cmdline.execute("scrapy crawl aitaotuCrawler -s LOG_FILE=scrapy.log".split())
cmdline.execute("scrapy crawl rentiyishu77Spider -s JOBDIR=crawls/rentiyishu77Spider-1 -s LOG_FILE=scrapy.log".split())
