import scrapy
import re


class StudapartSpider(scrapy.spiders.SitemapSpider):
    name = "studapart_spider"

    sitemap_urls = [
        "https://www.studapart.com/sitemap/ads.xml",
    ]
    
    sitemap_rules = [
        (r"/fr/", "parse"),
    ]

    def clean_text(self, s: str | None) -> str | None:
        if not s:
            return None
        s = re.sub(r"\s+", " ", s).strip()
        return s if s else None

    def extract_number(self, s: str | None) -> str | None:
        """
        Extracts digits only from a string.
        '70 m²' -> '70'
        '650 €' -> '650'
        """
        if not s:
            return None
        m = re.search(r"\d+", s.replace(" ", ""))
        return m.group() if m else None

    def parse_main_info(self, listing_props: list[str]) -> dict:
        data = {
            "listing_type": None,
            "furnished": None,
            "floor": None,
            "rooms": None,
            "size": None,
        }

        listing_props = [self.clean_text(x) for x in listing_props]
        listing_props = [x for x in listing_props if x]

        if listing_props:
            data["listing_type"] = listing_props[0]

        for line in listing_props[1:]:
            parts = [p.strip() for p in re.split(r"\s*•\s*", line) if p.strip()]
            for part in parts:
                part_l = part.lower()

                if "meublé" in part_l:
                    data["furnished"] = part

                elif "étage" in part_l or part_l in {
                    "rdc", "rez-de-chaussée", "rez de chaussée"
                }:
                    data["floor"] = part

                elif re.search(r"\b\d+\s*pi[eè]ce", part_l):
                    data["rooms"] = part

                elif re.search(r"\b\d+\s*m²\b", part_l):
                    data["size"] = part

        return data

    def parse(self, response):
        listing_address = self.clean_text(
            response.css("div.PropertyPage_location p.ft-s::text").get()
        )

        listing_title = self.clean_text(
            response.css("div.PropertyPage_title h1::text").get()
        )

        listing_price_raw = self.clean_text(
            response.css("div.PropertyPage_sidePrice p b::text").get()
        )

        listing_props = response.css("div.PropertyPage_body p.ft-s::text").getall()
        info = self.parse_main_info(listing_props)

        yield {
            "AdUrl": response.url,
            "AdTitle": listing_title,
            "RentalPrice_EUR": self.extract_number(listing_price_raw),
            "RentalAddrese": listing_address,
            "RentalSize_m2": self.extract_number(info["size"]),
            "RentalRooms": self.extract_number(info["rooms"]),
            "RentalFloor": info["floor"],
            "RentalType": info["listing_type"],
            "Furnished": info["furnished"],
        }


# For running the spider directly
if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess(settings={
        "FEEDS": {
            "output_all.json": {"format": "json", "overwrite": True},
        },
    })

    process.crawl(StudapartSpider)
    process.start()
