from multiprocessing.pool import ThreadPool
import requests
import json
import os
import click


folder = '.'
subreddit = '/r/hentai'

def download(link):
    filename = link.split('/')[-1]
    if not os.path.isfile(os.path.join(folder, filename)):
        if os.path.isfile(os.path.join(folder, filename + '.temp')):
            os.remove(os.path.join(folder, filename + '.temp'))
        with open(os.path.join(folder, filename + '.temp'), 'wb') as f:
            print('Downloading: {}'.format(filename))
            f.write(requests.get(link).content)
        os.replace(os.path.join(folder, filename + '.temp'),
                       os.path.join(folder, filename))
    else:
        print("Skipping download: {}".format(filename))


@click.command()
@click.option('--repeat', '-r', default=0, required=False)
def main(repeat):
    if repeat == 0:
        repeat_list = [0]
    else:
        repeat_list = [x for x in range(repeat)]
    for i in repeat_list:
        query = """
        query SubredditQuery(
            $url: String!
            $filter: SubredditPostFilter
            $iterator: String
        ) {
            getSubreddit(url: $url) {
                children(limit: 500, iterator: $iterator, filter: $filter) {
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
            "url": subreddit,
            "filter": "PICTURE"
        }
        r = requests.post('https://api.scrolller.com/api/v2/graphql', json={'query': query, 'variables': variables, "authorization": None}).json()
        r = r['data']['getSubreddit']['children']['items']

        links = [x['mediaSources'][-1]['url'] for x in r]
        results = ThreadPool(15).imap_unordered(download, links)
        for i in results:
            pass


main()
