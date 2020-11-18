from multiprocessing.pool import ThreadPool
import requests
import click
import os
import json


folder = '.'


class Scraper:
    def __init__(self):
        self.link = 'https://capi-v2.sankakucomplex.com/posts/keyset'
        self.params = {
            "lang": "en",
            "default_threshold": 1,
            "limit": 999,
            "tags": "rating:18"
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'
            }
        self.page_num = 1

    def nextPage(self):
        self.page_num += 1

    def getJSON(self):
        r = requests.get(self.link, headers=self.headers, params=self.params).json()
        self.params['next'] = r['meta']['next']

        return r['data']

    def getImages(self):
        images = [x['file_url'] for x in self.getJSON()]
        return images


class Media:
    def __init__(self, link):
        self.src = link
        self.filepath = os.path.join(folder, self.src.split('?')[0].split('/')[-1])
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'
            }

    def download(self):
        if not os.path.isfile(self.filepath):
            if os.path.isfile(self.filepath + '.temp'):
                os.remove(self.filepath + '.temp')
            with open(self.filepath + '.temp', 'wb') as f:
                print('Downloading: {}.'.format(self.filepath))
                f.write(requests.get(self.src, headers=self.headers).content)
            os.replace(self.filepath + '.temp', self.filepath)
        else:
            print(f'Skipping download of: {self.filepath}.')


def dl(link):
    Media(link).download()


@click.command()
@click.option('--pages', '-p', required=False, default=0)
def main(pages):
    imgs = []
    scraper = Scraper()

    if not pages:
        pages = [1]
    else:
        pages = [x for x in range(pages)]
    for i in pages:
        print('Current page: {}'.format(scraper.page_num))
        posters = scraper.getImages()

        results = ThreadPool(15).imap_unordered(dl, posters)
        for i in results:
            pass

        if len(pages) > 1:
            scraper.nextPage()
    print('Done!')


main()
