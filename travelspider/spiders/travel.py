import scrapy
from bs4 import BeautifulSoup
from travelspider.items import TravelspiderItem
from selenium import webdriver

class TravelSpider(scrapy.Spider):
    name = "travel"
    allowed_domains = ["travel.qunar.com"]
    start_urls = [
        f"https://travel.qunar.com/p-cs299979-chongqing-jingdian",
        *[f"https://travel.qunar.com/p-cs299979-chongqing-jingdian-1-{page}" for page in range(2, 200)]
    ]

    #初始化webdriver.Chrome，用于自动化操作Chrome
    def __init__(self):
        self.driver = webdriver.Chrome()

    def parse(self, response):
        self.driver.get(response.url)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        reviews = soup.find_all('span', class_="icon_comment")
        names = soup.find_all('span', class_="cn_tit")
        ratings = soup.find_all('span', class_="total_star")


        #提取信息，生成条目
        for name, rating, review in zip(reviews, names,ratings ):
            name_text = name.get_text(strip=True)
            rating_value = rating.find('span', class_='cur_star')['style']
            rating_percentage = int(rating_value.split(':')[1].strip('%'))
            review_count = review.parent.find_next('div', class_='comment_sum').text.strip()

            item = TravelspiderItem()
            item['review_count'] = review_count
            item['name'] = name_text
            item['score'] = rating_percentage

            yield item

        next_page = soup.find('a', class_='next')
        if next_page:

            #提取下一页的绝对URL
            next_page_url = response.urljoin(next_page['href'])

            #回调函数
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def closed(self, reason):
        self.driver.quit()