import unittest
from Wordpress import Crawler
import os


class WordpressTest(unittest.TestCase):
    def setUp(self):
        self.crawler = Crawler("https://turismo.comuneacqui.it")
        pass
    def testFolderCreation(self):
        folder_path ="wordpress"
        self.crawler.run()
        self.assertEqual(os.path.exists(folder_path),True)



if __name__ == '__main__':
    unittest.main()
