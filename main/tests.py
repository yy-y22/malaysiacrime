from datetime import datetime
from xml.etree import ElementTree
from django.test import TestCase


class MainTestCase(TestCase):
    """
    Test accessing and browsing crime reports.
    """
    fixtures = ['main/fixtures/crimes', 'main/fixtures/comments']

    def setUp(self):
        pass

    def test_get_index(self):
        """
        Test accessing index page.
        """
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'main/index.html')

        self.assertEquals(len(response.context['crimes']), 3)
        self.assertEquals(response.context['crimes'][0].id, 1)
        self.assertEquals(response.context['crimes'][1].id, 2)
        self.assertEquals(response.context['crimes'][2].id, 3)

    def test_get_recent_updated(self):
        """
        Test accessing most updated page.
        """
        response = self.client.get('/recent/updated/')
        self.assertTemplateUsed(response, 'main/recent_updated.html')

        self.assertEquals(len(response.context['crimes']), 3)
        self.assertEquals(response.context['crimes'][0].id, 3)
        self.assertEquals(response.context['crimes'][1].id, 2)
        self.assertEquals(response.context['crimes'][2].id, 1)

    def test_get_recent_commented(self):
        """
        Test accessing most commented page.
        """
        response = self.client.get('/recent/commented/')
        self.assertTemplateUsed(response, 'main/recent_commented.html')

        self.assertEquals(len(response.context['crimes']), 2)
        self.assertEquals(response.context['crimes'][0].id, 2)
        self.assertEquals(response.context['crimes'][1].id, 1)

    def test_get_sitemap(self):
        """
        Test accessing sitemap.xml.
        """
        response = self.client.get('/sitemap.xml')

        self.assertEquals(response.status_code, 200)
        root = ElementTree.fromstring(response.content)
        namespace = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
        self.assertEquals(root.tag, namespace + 'urlset')
        self.assertEquals(
            [entry.find(namespace + 'loc').text for entry in root],
            [entry['location'] for entry in response.context['urlset']]
        )
        self.assertEquals(
            [entry.find(namespace + 'lastmod').text for entry in root],
            ['2009-04-01', '2009-04-30', '2009-05-01']
        )
        self.assertEquals(root.findall('.//' + namespace + 'priority'), [])

        self.assertEquals(response.context['urlset'][0]['location'], "http://example.com/crime/title/terrible-crime-2/")
        self.assertEquals(response.context['urlset'][1]['location'], "http://example.com/crime/title/kidnap-of-dpm/")
        self.assertEquals(response.context['urlset'][2]['location'], "http://example.com/crime/title/daylight-extortion/")

        self.assertEquals(response.context['urlset'][0]['lastmod'], datetime(2009,4,1))
        self.assertEquals(response.context['urlset'][1]['lastmod'], datetime(2009,4,30))
        self.assertEquals(response.context['urlset'][2]['lastmod'], datetime(2009,5,1))

    def tearDown(self):
        pass
