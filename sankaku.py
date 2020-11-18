from multiprocessing.pool import ThreadPool
import requests
import click
import os
import json


class Scraper:
    def __init__(self, folder):
        self.link = 'https://capi-v2.sankakucomplex.com/posts/keyset'
        self.download_dir = folder
        if not os.path.isdir(self.download_dir):
            os.makedirs(self.download_dir)

        self.params = {
            "lang": "en",
            "default_threshold": 1,
            "limit": 999,
            "tags": "rating:18"
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'  # noqa
            }
        self.page_num = 1

    def getImages(self):
        JSON = requests.get(self.link, headers=self.headers, params=self.params).json()  # noqa
        images = [x['file_url'] for x in JSON['data']]
        self.params['next'] = JSON['meta']['next']
        self.page_num += 1
        return images

    def downloadMedia(self, link):
        filepath = os.path.join(self.download_dir, link.split('?')[0].split('/')[-1]).replace('\\', '/')  # noqa
        if not os.path.isfile(filepath):
            if os.path.isfile(filepath + '.temp'):
                os.remove(filepath + '.temp')
            with open(filepath + '.temp', 'wb') as f:  # noqa
                print('Downloading: {}'.format(filepath.split('/')[-1]))
                f.write(requests.get(link, headers=self.headers).content)
            os.replace(filepath + '.temp', filepath)
        else:
            print("Skipping download: {}".format(filepath.split('/')[-1]))


@click.command()
@click.option('--pages', '-p', required=False, default=0)
@click.option('--download-dir', '-d', 'folder', required=False, default='./sankaku', type=str)  # noqa
def main(pages, folder):
    imgs = []
    scraper = Scraper(folder)

    if not pages:
        pages = [1]
    else:
        pages = [x for x in range(pages)]
    for i in pages:
        print('Current page: {}'.format(scraper.page_num))
        posters = scraper.getImages()

        results = ThreadPool(15).imap_unordered(scraper.downloadMedia, posters)
        for i in results:
            pass

    print('Done!')


main()
