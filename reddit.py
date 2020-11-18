from multiprocessing.pool import ThreadPool
import requests
import json
import os
import click


class Scroller:
    def __init__(self, subreddit, folder):
        self.subreddit = subreddit
        self.download_dir = folder
        if not os.path.isdir(self.download_dir):
            os.makedirs(self.download_dir)

        self.current_repeat = 1


    def getMedia(self):
        query = """
        query SubredditQuery(
            $url: String!
            $filter: SubredditPostFilter
            $iterator: String
        ) {
            getSubreddit(url: $url) {
                children(limit: 100, iterator: $iterator, filter: $filter) {
                    iterator
                    items {
                        url
                        title
                        isNsfw
                        mediaSources {
                            url
                            width
                            height
                            isOptimized
                        }
                    }
                }
            }
        }
        """
        variables = {
            "url": self.subreddit,
            "filter": "PICTURE"
        }
        r = requests.post(
            'https://api.scrolller.com/api/v2/graphql',
            json={'query': query, 'variables': variables, "authorization": None}
        ).json()

        r = r['data']['getSubreddit']['children']['items']
        self.current_repeat += 1
        return [x['mediaSources'][-1]['url'] for x in r]

    def downloadMedia(self, link):
        filename = link.split('/')[-1]
        if not os.path.isfile(os.path.join(self.download_dir, filename)):
            if os.path.isfile(os.path.join(self.download_dir, filename + '.temp')):  # noqa
                os.remove(os.path.join(self.download_dir, filename + '.temp'))
            with open(os.path.join(self.download_dir, filename + '.temp'), 'wb') as f:  # noqa
                print('Downloading: {}'.format(filename))
                f.write(requests.get(link).content)
            os.replace(os.path.join(self.download_dir, filename + '.temp'),
                       os.path.join(self.download_dir, filename))
        else:
            print("Skipping download: {}".format(filename))


@click.command()
@click.option('--repeat', '-r', default=0, required=False, type=int)
@click.option('--subreddit', '-s', default='/r/hentai', required=False, type=str)
@click.option('--download-dir', '-d', 'folder', required=False, default='./reddit', type=str)  # noqa
def main(repeat, subreddit, folder):
    scraper = Scroller(subreddit, folder)
    if repeat == 1:
        times_repeating = [1]
    else:
        times_repeating = range(repeat)
    for i in times_repeating:
        print('Current repeat: {}'.format(scraper.current_repeat))
        links = scraper.getMedia()
        results = ThreadPool(15).imap_unordered(scraper.downloadMedia, links)
        for i in results:
            pass


main()
