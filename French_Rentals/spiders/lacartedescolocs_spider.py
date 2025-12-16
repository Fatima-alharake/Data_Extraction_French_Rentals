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
            self.logger.info("✅ Asking for Sitemap...")
            yield scrapy.Request(
                url="https://www.lacartedescolocs.fr/sitemap.xml",
                callback=self.parse_sitemap,
                meta={"impersonate": self.impersonate_browser}
            )
        else:
            self.logger.error(f"❌ Error {response.status}")

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

        # Eliminar duplicados
        listing_urls = list(set(listing_urls))

        self.logger.info(f"🎉 Found {len(listing_urls)} valid listings.")

        for url in listing_urls:
            yield scrapy.Request(
                url, 
                callback=self.parse_ad,
                meta={"impersonate": self.impersonate_browser}
            )

    def parse_ad(self, response):
        json_data_raw = response.css('div#listing_data::attr(data-json)').get()

        if not json_data_raw:
            self.logger.warning(f"⚠️  JSON not found {response.url}")
            return

        try:
            data = json.loads(json_data_raw)
        except json.JSONDecodeError:
            self.logger.error(f"⚠️ Error decoding JSON {response.url}")
            return

        description = data.get('description', '').lower()
        floor = None
        if "rdc" in description or "rez-de-chaussée" in description:
            floor = "0"
        elif "duplex" in description:
            floor = "Duplex"
        else:
            m = re.search(r"(\d+)(?:ème|er)?\s*étage", description)
            if m: floor = m.group(1)

        is_furnished = "Oui" if data.get('furnished') is True else "Non"

        yield {
            "AdUrl": response.url,
            "AdTitle": data.get('main_title'),
            "RentalPrice_EUR": data.get('cost_total_rent'),
            "RentalAddrese": f"{data.get('address_street', '')}, {data.get('address_city', '')}",
            "RentalSize_m2": data.get('lodging_surface'),
            "RentalRooms": data.get('lodging_size_string'), 
            "RentalFloor": floor,
            "RentalType": data.get('lodging_type_string'),
            "Furnished": is_furnished,
            "Lat": data.get('latitude'),
            "Lon": data.get('longitude')
        }