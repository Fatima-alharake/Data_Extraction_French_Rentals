import scrapy
import re
import json

class LaCarteDesColocsSpider(scrapy.Spider):
    name = "lacartedescolocs_spider"
    
    impersonate_browser = "safari15_5"

    def start_requests(self):
        yield scrapy.Request(
            url="https://www.lacartedescolocs.fr/",
            callback=self.parse_home,
            meta={"impersonate": self.impersonate_browser},
            headers={"Referer": "https://www.google.com/"}
        )

    def parse_home(self, response):
        if response.status == 200:
            yield scrapy.Request(
                url="https://www.lacartedescolocs.fr/sitemap.xml",
                callback=self.parse_sitemap,
                meta={"impersonate": self.impersonate_browser}
            )

    def parse_sitemap(self, response):
        xml_text = response.text
        raw_urls = re.findall(r'<loc>(.*?)</loc>', xml_text)
        
        listing_urls = []
        for url in raw_urls:
            url = url.strip()
            if "/colocations/" not in url:
                continue
            if "/paris/" not in url:
                continue
            if "/a/" not in url:
                continue
            listing_urls.append(url)

        listing_urls = list(set(listing_urls))

        for url in listing_urls:
            yield scrapy.Request(
                url, 
                callback=self.parse_ad,
                meta={"impersonate": self.impersonate_browser}
            )

    def parse_ad(self, response):
        json_data_raw = response.css('div#listing_data::attr(data-json)').get()

        if not json_data_raw:
            return

        try:
            data = json.loads(json_data_raw)
        except json.JSONDecodeError:
            return

        description = data.get('description', '').lower()
        floor_val = None
        
        if "rdc" in description or "rez-de-chaussée" in description:
            floor_val = "Rez-de-chaussée"
        elif "duplex" in description:
            floor_val = "Duplex"
        else:
            m = re.search(r"(\d+)(?:ème|er)?\s*étage", description)
            if m: 
                num = m.group(1)
                suffix = "er" if num == "1" else "ème"
                floor_val = f"{num}{suffix} étage"

        rooms_val = None
        if data.get('lodging_size'):
            rooms_val = str(data.get('lodging_size'))
        elif data.get('lodging_size_string'):
            m_rooms = re.search(r'(\d+)', str(data.get('lodging_size_string')))
            if m_rooms:
                rooms_val = m_rooms.group(1)

        item = {}
        
        item["AdUrl"] = response.url
        
        if data.get('main_title'):
            item["AdTitle"] = data.get('main_title')
            
        if data.get('cost_total_rent'):
            item["RentalPrice_EUR"] = str(data.get('cost_total_rent'))
            
        street = data.get('address_street', '')
        city = data.get('address_city', '')
        if street and city:
            item["RentalAddrese"] = f"{street}, {city}"
        elif city:
            item["RentalAddrese"] = city
            
        if data.get('lodging_surface'):
            item["RentalSize_m2"] = str(data.get('lodging_surface'))
            
        if rooms_val:
            item["RentalRooms"] = rooms_val
            
        if floor_val:
            item["RentalFloor"] = floor_val
            
        if data.get('lodging_type_string'):
            item["RentalType"] = data.get('lodging_type_string')
            
        if data.get('furnished') is True:
            item["Furnished"] = "Meublé"
        
        if data.get('latitude'):
            item["Lat"] = str(data.get('latitude'))
            
        if data.get('longitude'):
            item["Lon"] = str(data.get('longitude'))

        yield item