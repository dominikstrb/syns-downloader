import scrapy
import csv

def authentication_failed(response):
    """ Test whether the authentication failed. This is the case when one gets returned to the login page.

    Args:
        response (scrapy.Response): response from the login FormRequest

    Returns:
        true if the authentication failed
    """
    # is the user returned to the login page?
    return response.url == "https://syns.soton.ac.uk/auth/login"


class DownloadLinkSpider(scrapy.Spider):
    name = 'syns'
    login_url = "https://syns.soton.ac.uk/auth/login"
    base_url = "https://syns.soton.ac.uk"

    def __init__(self, **kwargs):
        """ Setup the csv writer and write the header

        Args:
            **kwargs: kwargs passed to scrapy.Spider.__init__()
        """
        super().__init__(**kwargs)
        with open('urls.csv', 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(['Scene', 'URL', 'Type'])

    def start_requests(self):
        """ Login to the SYNS page with my credentials

        Yields:
            scrapy.FormRequest
        """
        yield scrapy.FormRequest(self.login_url,
                                 formdata={'email': 'dominikstraub@yahoo.com', 'password': '#ladida1'},
                                 callback=self.logged_in)

    def logged_in(self, response):
        """ Run after loggin in. Starts parsing of the scenes

        Args:
            response (scrapy.Response): (returned from the login request)

        Returns:
            scrapy.Request to https://syns.soton.ac.uk/browse/number, that is referred to self.parse()
        """
        if authentication_failed(response):
            self.logger.error("Login failed")

        return scrapy.Request("https://syns.soton.ac.uk/browse/number", callback=self.parse)

    def parse(self, response):
        """ Parse all scenes on https://syns.soton.ac.uk/browse/number

        Args:
            response (scrapy.Response): response from the Request sent in self.logged_in()

        Yields:
            Requests to the individual scene pages -> https://syns.soton.ac.uk/view/$NUMBER$/
        """
        a_selectors = response.xpath("//a")
        # Loop on each tag
        i = 1
        for selector in a_selectors:
            # Extract the link text
            text = selector.xpath("text()").extract_first()
            # Extract the link href
            link = selector.xpath("@href").extract_first()
            # Create a new Request object
            if "/view/" in link:
                request = response.follow(link, callback=self.parse_scene, cb_kwargs=dict(scene_number=i))
                # Return it thanks to a generator
                i += 1
                yield request

    def parse_scene(self, response, scene_number):
        """ Parse a scene page a la https://syns.soton.ac.uk/view/$NUMBER$/
            Save the URLs, file types and scene numbers as lines to urls.csv

        Args:
            response (scrapy.Response): response from the request to https://syns.soton.ac.uk/view/$NUMBER$/
            scene_number (int): scene number (actual, not the one in the link)

        Returns:
            None
        """

        a_selectors = response.xpath("//tr")
        # print(response.url[-1])

        # Loop on each tag
        for s in a_selectors:
            link = s.xpath("td[2]/a/@href").extract_first()
            kind = s.xpath("td[3]/text()").extract()
            # map = s.xpath(".//tr/td[3]/text()").extract()

            # Extract the link text
            # text = selector.xpath("text()").extract_first()
            # Extract the link href
            # link = selector.xpath("@href").extract_first()
            # Create a new Request object
            # Return it thanks to a generator
            # if text:
            #    if "StereoNEF.zip" in text:

            url = response.urljoin(link)

            data_line = [scene_number, url, kind[0]]

            with open('urls.csv', 'a') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(data_line)

            self.logger.info("Writing scene # {} at {} of type {}".format(*data_line))