import scrapy
from scrapy import Request, FormRequest

from crawl.scrapy.spiders.base import *
from ..validators import TrackingMeta

def textify(text):
    if text !=[]:
        text = ','.join(text).encode('ascii','ignore').strip().decode('utf-8').replace('\t','').replace('\r','')
    else:
        text = ''
    return text

def rightSideInfo(self, response):
    rightSideData = {}
    title = textify(response.xpath("//div[@class='SPZz6b']/div[@data-attrid='title']/span/text()").extract())
    if title=='':
        title = textify(response.xpath("//div[@class='DRolee']/text()").extract())
    if title=='See results about':
        return {}
    companyType = textify(response.xpath("//div[@class='SPZz6b']/div[@data-attrid='subtitle']/span/text()").extract())
    if companyType=='':
        typeNode = response.xpath("//span[@class='YhemCb']")
        for each in typeNode:
            txt = textify(each.xpath('./text()').extract())
            companyType+=txt
    desc = textify(response.xpath("//h2[@class='bNg8Rb']/following-sibling::span/text()").extract())
    if desc =='':
        desc = textify(response.xpath("//span[@class='ILfuVd UiGGAb']/span[@class='e24Kjd']/text()").extract())
    if desc=='':
        desc = textify(response.xpath("//span[@class='ILfuVd rjOVwe']/span[@class='e24Kjd']/text()").extract())
    siteUrl = textify(response.xpath("//span[@class='ellip']/text()").extract())
    rightSideData['title']=title
    rightSideData['type']=companyType
    rightSideData['description']=desc
    rightSideData['siteUrl']=siteUrl

    rightSideBoxLabels = response.xpath("//span[@class='w8qArf']/a")
    rightSideBoxValues = response.xpath("//span[@class='w8qArf']//following-sibling::span")
    j=0
    labelsValues={}
    for i in rightSideBoxLabels:
        logo = textify(i.xpath('./text()').extract())
        if (logo=='Hours' and len(rightSideBoxLabels)!=len(rightSideBoxValues)):
            val = textify(response.xpath("//span[@class='TLou0b']/span/text()").extract())
        else:
            val =   textify(rightSideBoxValues[j].xpath('./a/text()').extract())
            val1 =  textify(rightSideBoxValues[j].xpath('./span/text()').extract()).replace(',',' ')
            val = val+val1
            if val=='':
                val = textify(rightSideBoxValues[j].xpath('./span//text()').extract()) 
            if val=='':
                val = textify(rightSideBoxValues[j].xpath('./text()').extract())
            j+=1
        rightSideData[logo]=val
    return rightSideData
    

def mainPageInfo(self, response):
    descriptionList = []
    listOfUrls          = response.xpath('//div[@class="r"]/a/@href').extract()
    listOfTitles        = response.xpath('//h3[@class="LC20lb DKV0Md"]/text()').extract()
    listOfDescription   = response.xpath('//div[@class="s"]/div/span[@class="st"]')
    for i in range(len(listOfUrls)):
        desc = textify(listOfDescription[i].xpath('.//text()').extract())
        descriptionList.append(desc)
    return [listOfUrls,listOfTitles,descriptionList]

class PageMeta(BasePage):
    def request(self):
        url = 'https://www.google.com/search?q=%s'%(self.key)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US',
            'Connection': 'keep-alive',
        }
        return Request(url, headers=headers)

    def parse(self, response):
        metaData=TrackingMeta()
        metaData['searchData']=[]
        rightSideData = rightSideInfo(self, response)
        mainPageData = mainPageInfo(self, response)
        urls,title,description = mainPageData
        for i in range(len(urls)):
            metaData['searchData'].append({'url':urls[i],'title':title[i],'description':description[i]})
        metaData['rightSideData']=rightSideData
        anotherKey = response.xpath("//span[contains(text(),'Did you mean:')]/parent::p[@class='gqLncc card-section']/a[@class='gL9Hy']/b/i/text()").extract()
        if anotherKey:
            metaData.groups.append(
                                    SchemaItemGroup({
                                                    'name': 'related',
                                                    'keys': anotherKey,
                                                })
            )
        return metaData


class GoogleSearchSpider(BaseSpider):
    name = 'google'
    main_page_class = PageMeta

