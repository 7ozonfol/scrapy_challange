import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from ..property import Property
from ..loaders import ListingLoader
from ..helper import *

class VermietungsProfiDeSpider(scrapy.Spider):
    name = "londonrelocations"
    start_urls = ['https://smartsite2.myonoffice.de/kunden/vermietungsprofi/47/alle-immobilien.xhtml?f%5B2861-21%5D=0&f%5B2861-23%5D=0&f%5B2861-55%5D=0&f%5B2861-5%5D=wohnung&f%5B2861-41%5D=&f%5B2861-9%5D=&f%5B2861-8%5D=&f%5B2861-47%5D=&f%5B2861-49%5D=&f%5B2861-13%5D=',
                  'https://smartsite2.myonoffice.de/kunden/vermietungsprofi/47/alle-immobilien.xhtml?f%5B2861-21%5D=0&f%5B2861-23%5D=0&f%5B2861-55%5D=0&f%5B2861-5%5D=haus&f%5B2861-41%5D=&f%5B2861-9%5D=&f%5B2861-8%5D=&f%5B2861-47%5D=&f%5B2861-49%5D=&f%5B2861-13%5D=']
    allowed_domains = ["vermietungs-profi.de","smartsite2.myonoffice.de", "image.onoffice.de"]
    country = 'Germany' # Fill in the Country's name
    locale = 'de' # Fill in the Country's locale, look up the docs if unsure
    external_source = "{}_PySpider_{}_{}".format(
        name.capitalize(), country, locale)
    execution_type = 'testing'

    position = 1

    # 1. SCRAPING level 1
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    # 2. SCRAPING level 2
    def parse(self, response, **kwargs):
        urls = response.css('.link ::attr(href)').extract()
        urls = ['https://smartsite2.myonoffice.de/kunden/vermietungsprofi/47/' + x for x in urls]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.populate_item)

    # 3. SCRAPING level 3
    def populate_item(self, response):
        item_loader = ListingLoader(response=response)
        title = response.css('h1 ::text')[0].extract()
        #print(title)
        external_id = response.url.split('[obj0]')[1][1:]
        descriptions = response.css('.freetext span span ::text').extract()
        description = ''
        for i in descriptions:
            description += i
        available_date = None
        if 'verfügbar ab ' in description:
            available_date = description.split('verfügbar ab ')[1].split(',')[0]
        description = description_cleaner(description)


        detailsTable = response.css('.datablock-half td ::text').extract()
        city = detailsTable[detailsTable.index('Town')+1]
        zipcode = detailsTable[detailsTable.index('ZIP code:')+1]
        floor = None
        property_type = detailsTable[detailsTable.index('Property class')+1]
        square_meters = detailsTable[detailsTable.index('Living area')+1][:-3]
        room_count = detailsTable[detailsTable.index('Number of bedrooms')+1]
        bathroom_count= detailsTable[detailsTable.index('Number of bathrooms')+1]
        try:
            address = response.xpath('/html/body/div[1]/div/div/div[3]/div[2]/div[3]/div[3]/span/span/text()')[0].extract()
        except:
            address = zipcode+' '+city
        longitude, latitude = extract_location_from_address(city)

        balcony = None
        if 'Balcony' in detailsTable:
            balcony = True
        elevator = None
        if 'Lift' in detailsTable:
            elevator = True
        terrace = None
        if 'Terrace' in detailsTable:
            terrace = True
        parking = None
        if 'Type of parking spaces' in detailsTable:
            parking = True
        furnished = None
        if 'Furnished' in detailsTable:
            furnished = True
        washing_machine = None
        if 'waschmaschinenanschluss' in description:
            washing_machine = True
        dishwasher = None
        if 'geschirrspüler' in description:
            washing_machine = True
        swimming_pool = None
        if 'schwimmbad' in description:
            swimming_pool = True


        rent = detailsTable[detailsTable.index('Basic rent')+1][:-2]
        rent = rent.replace('.','')
        #heating_cost = int(detailsTable[detailsTable.index('Rent including heating') + 1][:-2].replace('.','')) - int(rent)
        utilities= detailsTable[detailsTable.index('Utilities') + 1][:-2]
        utilities = utilities.replace('.','')
        deposit = detailsTable[detailsTable.index('Deposit') + 1][:-2]
        deposit = deposit.replace('.','')

        landlord_name = response.xpath('/html/body/div[1]/div/div/div[3]/div[3]/div[1]/p[@class="name"]/text()')[0].extract()
        landlord_number = response.xpath('/html/body/div/div/div/div[3]/div[3]/div[1]/p[3]/span[1]/span/span/text()')[0].extract()
        landlord_email = response.xpath('/html/body/div/div/div/div[3]/div[3]/div[1]/p[3]/span[3]/span/span/a/text()')[0].extract()

        images = response.css('.fotorama ::attr(data-img)').extract()



        # Your scraping code goes here
        # Dont push any prints or comments in the code section
        # if you want to use an item from the item loader uncomment it
        # else leave it commented
        # Finally make sure NOT to use this format
        #    if x:
        #       item_loader.add_value("furnished", furnished)
        # Use this:
        #   balcony = None
        #   if "balcony" in description:
        #       balcony = True

        # Enforces rent between 0 and 40,000 please dont delete these lines
        if int(rent) <= 0 and int(rent) > 40000:
           return

        # # MetaData
        item_loader.add_value("external_link", response.url) # String
        item_loader.add_value("external_source", self.external_source) # String

        item_loader.add_value("external_id", external_id) # String
        item_loader.add_value("position", self.position) # Int
        item_loader.add_value("title", title) # String
        item_loader.add_value("description", description) # String

        # # Property Details
        item_loader.add_value("city", city) # String
        item_loader.add_value("zipcode", zipcode) # String
        item_loader.add_value("address", address) # String
        item_loader.add_value("latitude", latitude) # String
        item_loader.add_value("longitude", longitude) # String
        item_loader.add_value("floor", floor) # String
        item_loader.add_value("property_type", property_type) # String => ["apartment", "house", "room", "student_apartment", "studio"]
        item_loader.add_value("square_meters", square_meters) # Int
        item_loader.add_value("room_count", room_count) # Int
        item_loader.add_value("bathroom_count", bathroom_count) # Int

        item_loader.add_value("available_date", available_date) # String => date_format

        #item_loader.add_value("pets_allowed", pets_allowed) # Boolean
        item_loader.add_value("furnished", furnished) # Boolean
        item_loader.add_value("parking", parking) # Boolean
        item_loader.add_value("elevator", elevator) # Boolean
        item_loader.add_value("balcony", balcony) # Boolean
        item_loader.add_value("terrace", terrace) # Boolean
        item_loader.add_value("swimming_pool", swimming_pool) # Boolean
        item_loader.add_value("washing_machine", washing_machine) # Boolean
        item_loader.add_value("dishwasher", dishwasher) # Boolean

        # # Images
        item_loader.add_value("images", images) # Array
        item_loader.add_value("external_images_count", len(images)) # Int
        #item_loader.add_value("floor_plan_images", floor_plan_images) # Array

        # # Monetary Status
        item_loader.add_value("rent", rent) # Int
        item_loader.add_value("deposit", deposit) # Int
        #item_loader.add_value("prepaid_rent", prepaid_rent) # Int
        item_loader.add_value("utilities", utilities) # Int
        item_loader.add_value("currency", "EUR") # String

        #item_loader.add_value("water_cost", water_cost) # Int
        #item_loader.add_value("heating_cost", heating_cost) # Int

        #item_loader.add_value("energy_label", energy_label) # String

        # # LandLord Details
        item_loader.add_value("landlord_name", landlord_name) # String
        item_loader.add_value("landlord_phone", landlord_number) # String
        item_loader.add_value("landlord_email", landlord_email) # String

        self.position += 1
        yield item_loader.load_item()