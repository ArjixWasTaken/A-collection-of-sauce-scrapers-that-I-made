from multiprocessing.pool import ThreadPool
from bs4 import BeautifulSoup
import requests
import click
import json
import os


class Scraper:
    def __init__(self, folder):
        self.base_url = 'https://gelbooru.com/index.php'
        self.html = BeautifulSoup(requests.get(f'{self.base_url}?page=post&s=list&pid=0').text, 'html.parser')
        self.download_dir = folder
        self.current_page = 1
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'
        }

        if not os.path.isdir(self.download_dir):
            os.makedirs(self.download_dir)

    def nextPage(self):
        pagination = self.html.select_one('div#paginator > div.pagination').find('a', alt='next', href=True)  # noqa
        if pagination:
            next_page = pagination['href']
        self.html = BeautifulSoup(requests.get(f'{self.base_url}{next_page}').text, 'html.parser')  # noqa
        self.current_page += 1

    def getMedia(self):
        return ['https:' + x['href'] for x in self.html.find(
            'div', class_='thumbnail-container').select('div.thumbnail-preview.poopC > span > a')]  # noqa

    def downloadImage(self, link):
        soup = BeautifulSoup(requests.get(link, headers=self.headers).text, 'html.parser')  # noqa
        for i in soup.select('script'):
            if "image = {'domain':" in str(i):
                data = i
        data = ' '.join(str(data).split()[3:-2]).split('= ')[1][:-1].replace("'", '"')  # noqa
        data = json.loads(data)
        link = data['domain'] + data['base_dir'] + '/' + data['dir'] + '/' + data['img']  # noqa
        media_name = link.split('/')[-1]

        if not os.path.isfile(os.path.join(self.download_dir, media_name)):
            if os.path.isfile(os.path.join(self.download_dir, media_name + '.temp')):  # noqa
                os.remove(os.path.join(self.download_dir, media_name + '.temp'))  # noqa

            with open(os.path.join(self.download_dir, media_name + '.temp'), 'wb') as f:  # noqa
                print('Downloading: {}'.format(media_name))
                f.write(requests.get(link, headers=self.headers).content)  # noqa

            os.replace(os.path.join(self.download_dir, media_name + '.temp'),
                       os.path.join(self.download_dir, media_name))
        else:
            print(f'Skipping download of: {media_name}.')


@click.command()
@click.option('--pages', '-p', required=False, default=1)
@click.option('--download-dir', '-d', 'folder', required=False, default='./gelbooru')
def main(pages, folder):
    scraper = Scraper(folder)
    for i in range(pages):
        all_media = scraper.getMedia()
        results = ThreadPool(15).imap_unordered(
            scraper.downloadImage, all_media)
        for i in results:
            pass
        scraper.nextPage()
    print('Done!')


if __name__ == '__main__':
    main()
