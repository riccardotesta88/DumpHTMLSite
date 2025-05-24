import requests
import os
import xml.etree.ElementTree as ET

from alive_progress import alive_bar


class Crawler:
    def __init__(self, url):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.__setLocalSaveFolder("wordpress")
        self.namespaces = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    def readXMLSitemap(self, name="sitemap",url=None):
        if not url:
            sitemap_url = f"{self.url}/{name}.xml"
        else:
            sitemap_url = url
        response = self.session.get(sitemap_url)
        result=response.text.lstrip()
        for k in ['\n', '\r', '\t']:
            result = result.replace(k, '')
        return result

    def parseSubXMLSitemap(self, xml_sitemap, max_depth=2):

        root = ET.fromstring(xml_sitemap)

        sub_sitemaps = []
        for sitemap in root.findall('sm:sitemap', self.namespaces):
            loc = sitemap.find('sm:loc', self.namespaces).text
            lastmod = sitemap.find('sm:lastmod', self.namespaces).text

            sub_sitemaps.append(loc)

        print(f'sub_sitemaps: {len(sub_sitemaps)}')
        return sub_sitemaps[:max_depth]

    def extractRecordPage(self, xml_sitemap):

        root = ET.fromstring(xml_sitemap)
        html_urls = []
        records=root.findall('sm:url', self.namespaces)
        for sitemap in records:
            loc = sitemap.find('sm:loc', self.namespaces).text
            lastmod = sitemap.find('sm:lastmod', self.namespaces).text
            # print(f"URL: {loc}, Last Modified: {lastmod}")
            html_urls.append(loc)

        print(f'\nRecord: {len(records)}')
        return html_urls

    def urlDownload(self, html_urls):
        for url in html_urls:

            file_name = '.hmtl'.join(url.split("/")[-2:])
            if not os.path.exists(f"{self.folder_path}/{file_name}"):
                response = self.session.get(url)
                with open(f"{self.folder_path}/{file_name}", "wb") as file:
                    file.write(response.text.encode('utf-8'))
                sleep(0.1)


    def __setLocalSaveFolder(self, folder_path):
        self.folder_path = os.realpath(folder_path) if os.path.isabs(folder_path) else os.getcwd() + "/" + folder_path

        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        return self.folder_path

    def run(self):

            xml_sitemap = self.readXMLSitemap()
            sub_sitemaps = self.parseSubXMLSitemap(xml_sitemap)

            for sub_sitemap in sub_sitemaps:
                print(f'\n{sub_sitemap}\n')
                xml_sitemap_in = self.readXMLSitemap(url=sub_sitemap)


                pages=self.extractRecordPage(xml_sitemap_in)
                with alive_bar(len(pages), force_tty=True) as bar:
                    for page in pages:
                        self.urlDownload([page])
                        bar()



from time import sleep


if __name__ == "__main__":
    wordpress = Crawler("https://turismo.comuneacqui.it")
    wordpress.run()
