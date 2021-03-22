from multiprocessing.pool import ThreadPool
import requests
import click
import os
import json


class Hanime:
    def __init__(self, folder='./hanime'):
        self.page = 1
        self.last_id = 0
        self.folder = folder
        if not os.path.isdir(self.folder):
            os.makedirs(self.folder)

    def scrape_images(self):
        if self.last_id == 0:
            link = "https://hr.hanime.tv/api/v8/community_uploads?channel_name__in[]=media&channel_name__in[]=nsfw-general&kind=landing&loc=https://hanime.tv"
        else:
            link = f"https://hr.hanime.tv/api/v8/community_uploads?channel_name__in[]=media&channel_name__in[]=nsfw-general&channel_name__in[]=yuri&query_method=seek&before_id={self.last_id}&loc=https://hanime.tv"
        r = requests.get(link).json()
        self.last_id = r['data'][-1]['id']
        return r['data']

    def next_page(self):
        self.page += 1

    def download(self, image):
        filename = "id='{}' channel_name='{}' uploader='{}'.{}".format(image['id'], image['channel_name'], image['username'], image['extension'])
        illegal = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for i in illegal:
            if i in filename:
                filename = filename.replace(i, '')

        filepath = os.path.join(self.folder, filename)

        if os.path.isfile(filepath + '.temp'):
            os.remove(filepath + '.temp')
        if not os.path.isfile(filepath):
            with open(filepath + '.temp', 'wb') as f:
                print("Downloading: ", filename)
                f.write(requests.get(image['url']).content)
            os.replace(filepath + '.temp', filepath)


@click.command()
@click.option('--pages', '-p', required=False, default=0)
@click.option('--download-dir', '-d', 'folder', required=False, default='./hanime', type=str)  # noqa
def main(pages, folder):
    imgs = []
    scraper = Hanime(folder)

    if not pages:
        pages = [1]
    else:
        pages = [x for x in range(pages)]
    for i in pages:
        print('Current page: {}'.format(scraper.page))
        posters = scraper.scrape_images()

        results = ThreadPool(15).imap_unordered(scraper.download, posters)
        for i in results:
            pass
        scraper.next_page()

    print('Done!')


main()
