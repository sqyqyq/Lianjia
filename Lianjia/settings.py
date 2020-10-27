# Scrapy settings for Lianjia project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'Lianjia'

SPIDER_MODULES = ['Lianjia.spiders']
NEWSPIDER_MODULE = 'Lianjia.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'Lianjia (+http://www.yourdomain.com)'
# USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'

# Obey robots.txt rules
# ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 220

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 220
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': "en-US,zh-CN;q=0.7,en;q=0.3"
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'Lianjia.middlewares.LianjiaSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'Lianjia.middlewares.LianjiaDownloaderMiddleware': 543,
#    'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': None,
# }
DOWNLOADER_MIDDLEWARES = {
    # 'Lianjia.middlewares.RandomProxyMiddleware2': 10,
    # 'Lianjia.middlewares.IPProxyDownloadMiddleware': 100,
    'Lianjia.middlewares.RandomProxyMiddleware': 101,
    # 'gerapy_proxy.middlewares.ProxyPoolMiddleware': 543,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
    # 'scrapy_random_useragent_pro.middleware.RandomUserAgentMiddleware': 100
}

FAKEUSERAGENT_PROVIDERS = [
    'scrapy_fake_useragent.providers.FakeUserAgentProvider',  # this is the first provider we'll try
    'scrapy_fake_useragent.providers.FakerProvider',  # if FakeUserAgentProvider fails, we'll use faker to generate a user-agent string for us
    'scrapy_fake_useragent.providers.FixedUserAgentProvider',  # fall back to USER_AGENT value
]
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0'

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'Lianjia.pipelines.LianjiaPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 10
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 100
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = True

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# # HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = [301, 302, 404, 503, 500, 502, 504, 522, 524, 408, 429]
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# HTTPERROR_ALLOWED_CODES = []

LOG_LEVEL = 'INFO'
LOG_FILE = "log7.txt"

RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 403, 524, 408, 429, 301, 302, 404]
REDIRECT_ENABLED = False
METAREFRESH_ENABLED = False

LOG_FORMATTER = "Lianjia.logger.QuietLogFormatter"

# HTTPCACHE_POLICY = 'Lianjia.custompolicy.CustomPolicy'

# RETRY_HTTP_CODES = [500, 502, 504, 522, 524, 408, 429]
DOWNLOAD_FAIL_ON_DATALOSS = True
DOWNLOAD_TIMEOUT = 20
DEPTH_PRIORITY = 0
RETRY_PRIORITY_ADJUST = -1
# GERAPY_PROXY_POOL_URL = 'https://proxypool.scrape.center/random'
# GERAPY_PROXY_POOL_RANDOM_ENABLE_RATE = 0.9
# GERAPY_PROXY_POOL_TIMEOUT = 15
# RANDOM_UA_PER_PROXY = True
# TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
# RANDOM_UA_ENABLED = True
# RANDOM_UA_DEFAULT_TYPE = 'desktop'
# always change user-agent
# RANDOM_UA_OVERWRITE = False
FAKE_USERAGENT_RANDOM_UA_TYPE = 'desktop'
RETRY_TIMES = 0
