import requests
import os
import xml.etree.ElementTree as ET
import time
from time import sleep
from alive_progress import alive_bar
import re


class Crawler:

    def __init__(self, url:str):
        '''
        Wordpress Crawler
        General parameters and initialization variables
        :param url: default wordpress url xml sitemap
        '''
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self._setLocalSaveFolder("wordpress_{timestamp}".format(timestamp=time.strftime("%Y-%m-%d")))
        self.namespaces = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        self.lastr_update = 0
        self.datainsight={}

    def readXMLSitemap(self, name:str="sitemap", url:str=None)->str:
        '''
        Estract Sitemap from xml structure
        :param name: file name
        :param url: file url (optional)
        :return:
        '''

        print(f'Estract Sitemap: {name}')
        if not url:
            sitemap_url = f"{self.url}/{name}.xml"
        else:
            sitemap_url = url
        response = self.session.get(sitemap_url)
        result = response.text.lstrip()

        print(f'Text sanitize: {len(result)}')
        for k in ['\n', '\r', '\t']:
            result = result.replace(k, '')
        return result

    def parseSubXMLSitemap(self, xml_sitemap:str, structure:list=['post', 'page'], max_depth:int=2)->list:
        '''
        Parse xml sitemap
        :param xml_sitemap: string xml data
        :param structure: [post, page, category, tag, author] tag types
        :param max_depth: max depth sitemap
        :return:
        '''

        root = ET.fromstring(xml_sitemap)

        sub_sitemaps = []
        for sitemap in root.findall('sm:sitemap', self.namespaces):
            # Controllo strutture sitemaps
            loc = sitemap.find('sm:loc', self.namespaces).text
            # lastmod = sitemap.find('sm:lastmod', self.namespaces).text
            if re.search('|'.join(structure), loc):
                sub_sitemaps.append(loc)

        print(f'Founded Sitemap ulrs type documents: {len(sub_sitemaps)}')
        if max_depth == 0:
            return sub_sitemaps
        else:
            max_depth = len(sub_sitemaps)
            return sub_sitemaps[:max_depth]


    def extractRecordPage(self, xml_sitemap):

        parsering = ET.XMLParser(encoding="utf-8")
        root = ET.fromstring(xml_sitemap, parser=parsering)

        html_urls = []
        records = root.findall('sm:url', self.namespaces)
        for sitemap in records:
            loc = sitemap.find('sm:loc', self.namespaces).text
            lastmod = sitemap.find('sm:lastmod', self.namespaces).text
            # print(f"URL: {loc}, Last Modified: {lastmod}")
            html_urls.append(loc)

        print(f'\nRecord: {len(records)}')
        return html_urls


    def urlDownload(self, html_urls):
        for url in html_urls:

            file_name = '.html'.join(url.split("/")[-2:])
            if not os.path.exists(f"{self.folder_path}/{file_name}"):
                response = self.session.get(url)
                with open(f"{self.folder_path}/{file_name}", "wb") as file:
                    self.__insigth('td_pages')
                    file.write(response.text.encode('utf-8'))
                sleep(0.1)
                self.lastr_update += 1


    def _setLocalSaveFolder(self, folder_path):
        self.folder_path = os.realpath(folder_path) if os.path.isabs(folder_path) else os.getcwd() + "/" + folder_path

        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        return self.folder_path


    def run(self):
        xml_sitemap = self.readXMLSitemap()
        sub_sitemaps = self.parseSubXMLSitemap(xml_sitemap)

        for sub_sitemap in sub_sitemaps:
            print(f'{sub_sitemap}\n')
            xml_sitemap_in = self.readXMLSitemap(url=sub_sitemap)
            pages = self.extractRecordPage(xml_sitemap_in)

            self.__insigth(f'{sub_sitemap}_pages', mode=None, value=len(pages))

            with alive_bar(len(pages), force_tty=True) as bar:

                for page in pages:
                    self.urlDownload([page])
                    bar()

            self.__insigth(f'{sub_sitemap}_downloaded', mode=None, value=self.datainsight['td_pages'])
            self.__insigth('td_pages', mode=None, value=0)

    def __insigth(self, element, value=None, mode='sum'):
        '''
        Funzione per aggiornare l'insight dei dati dell'ultima esecuzione
        :param element: nome chiave memoriazzione
        :param value: valore da memorizzare
        :param mode: tipolo di memorizzazione
        :return:
        '''
        if mode == 'sum':
            self.datainsight.update(
                {element: 0} if not element in self.datainsight
                else {element: self.datainsight[element] + 1}
            )
        else:
            self.datainsight.update(
                {element: 0} if not element in self.datainsight or not value
                else {element: value}
            )

if __name__ == "__main__":

    wordpress = Crawler("https://turismo.comuneacqui.it/")
    wordpress._setLocalSaveFolder("wordpress_dsada")
    wordpress.run()
    print(wordpress.datainsight)
