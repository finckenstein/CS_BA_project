import scrapy
import time
from scrapy_splash import SplashRequest


class SplashVideoSpider(scrapy.Spider):
    name = 'video'
    allowed_domains = ['tasty.co',  'vid.tasty.co']
    start_urls = ['https://tasty.co/compilation/when-froyo-is-your-fav']

    def start_requests(self):
        accept_and_exit = """function main(splash)
                                assert(splash:go(splash.args.url))
                                splash:wait(5)
                            
                                local get_element_dim_by_xpath = splash:jsfunc([[
                                    function(xpath) {
                                        var element = document.evaluate(xpath, document, null,
                                            XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                                        var element_rect = element.getClientRects()[0];
                                        return {"x": element_rect.left, "y": element_rect.top}
                                    }
                                ]])
                            
                                local agree_and_accept = get_element_dim_by_xpath(
                                    '//button[contains(@class, " css-15dhgct") and contains(text(), "AGREE  & EXIT")]')
                                splash:set_viewport_full()
                                splash:mouse_click(agree_and_accept.x, agree_and_accept.y)
                                splash:wait(5)
                            
                                return {
                                    html = splash:html()
                                }
                            end """
        for url in self.start_urls:
            yield SplashRequest(url=url, callback=self.parse, endpoint='execute', args={'lua_source': accept_and_exit})

    def parse(self, response):
        time.sleep(5)
        video_src = response.xpath('//video/@src')
        print("\n\n", video_src, "\n\n")

