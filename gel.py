from multiprocessing.pool import ThreadPool
from bs4 import BeautifulSoup
import requests
import click
import json
import os

folder = '.'
if not os.path.isdir(folder):
    os.makedirs(folder)


class Media:
    def __init__(self, link):
        self.link = link
        self.html = self.get_src()
        self.src = self.extract_media()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'
        }

    def get_src(self):
        soup = BeautifulSoup(requests.get(self.link).text, 'html.parser')
        return soup

    def extract_media(self):
        data = self.html
        for i in data.select('script'):
            if "image = {'domain':" in str(i):
                data = i
        data = ' '.join(str(data).split()[3:-2]
                        ).split('= ')[1][:-1].replace("'", '"')
        data = json.loads(data)
        link = data['domain'] + data['base_dir'] + \
            '/' + data['dir'] + '/' + data['img']
        return link

    def download(self):
        done = False
        count = 0
        media_name = self.src.split('/')[-1]

        if not os.path.isfile(os.path.join(folder, media_name)):
            if os.path.isfile(os.path.join(folder, media_name + '.temp')):
                os.remove(os.path.join(folder, media_name + '.temp'))
            while not done and count <= 5:
                try:
                    with open(os.path.join(folder, media_name + '.temp'), 'wb') as f:
                        print('Downloading: {}'.format(media_name))
                        f.write(requests.get(self.src, headers=self.headers).content)
                    done = True
                    count += 1
                except Exception:
                    pass
            os.replace(os.path.join(folder, media_name + '.temp'),
                       os.path.join(folder, media_name))
        else:
            print(f'Skipping download of: {media_name}.')


def download(link):
    f = Media(link)
    f.download()


@click.command()
@click.option('--pages', '-p', required=False, default=1)
def main(pages):
    base_url = 'https://gelbooru.com/index.php'
    current_page = 1
    r = requests.get(f'{base_url}?page=post&s=list&pid=0').text

    for i in range(pages):
        print('Current page is: ', current_page)
        soup = BeautifulSoup(r, 'html.parser')
        pagination = soup.select_one('div#paginator > div.pagination').find(
            'a', alt='next', href=True)

        all_media = ['https:' + x['href'] for x in soup.find(
            'div', class_='thumbnail-container').select('div.thumbnail-preview.poopC > span > a')]

        results = ThreadPool(15).imap_unordered(download, all_media)
        for i in results:
            pass
        # download(all_media)

        if pagination:
            next_page = pagination['href']
            r = requests.get(f'{base_url}{next_page}').text
            current_page += 1
        else:
            break
    print('Done!')


main()
