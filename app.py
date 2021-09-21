from requests import get 
from bs4 import BeautifulSoup as BS

import os
import shutil
import logging

app_info = """Downloads a Facebook album from a page"""
host = "https://free.facebook.com/"

def save_photo(path, link, counter):
    img = get(link, stream=True, allow_redirects=True)
    file_name = f'{path}/{counter}.png'

    with open(file_name, 'wb') as photo:
       shutil.copyfileobj(img.raw, photo)
       logging.info(f'Downloaded img {counter}: {link}')


def setup_logger(path):
    filename = path + '/download_logs'
    logging.basicConfig(filename=filename,
            level=logging.INFO)

def find_next_img(html):
    next_link = html.find('a',
            text='Seguinte' or 'Next').attrs['href']
    img_link = html.find('a', class_='sec').attrs['href']

    return {'nxt': host + next_link, 
            'img': img_link}
        

def get_limited_from_page(args):
    counter = 0

    page = get(args.url)
    html = BS(page.content, 'lxml')

    while counter <= args.count:
        links = find_next_img(html) 
        save_photo(args.path, links['img'], counter)
        page = get(links['nxt'])
        html = BS(page.content, 'lxml')

        print(f"downloading img  {counter}")
        counter +=1


def get_all_from_page(args):
    init_link = args.url
    next_link = None
    counter = 0

    page = get(args.url)
    html = BS(page.content, 'lxml')

    while next_link != init_link:
        next_link = html.find('a', {'class':'bb'},
            text='Next' or 'Seguinte')['href']
        img_link = html.find('a', {'class':'sec'},
                text='View Full Size' or 
                'Ver tamanho completo')['href']

        save_photo(args.path, host + img_link, counter)
        page = get(next_link)
        html = BS(page.content, 'lxml')

        logging.debug(f'getting {next_link}')
        counter +=1 

def make_download_dir(path):
    os.makedirs(path, exist_ok=True)

def main(args):
    make_download_dir(args.path)
    setup_logger(args.path)

    logging.info(args)
    
    if not 'group' in args.url:
        if args.count is None:
            get_all_from_page(args)
        else:
            get_limited_from_page(args)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=app_info)
    parser.add_argument('url', type=str,
            help='the album url')
    parser.add_argument('-path', metavar='path',
            type=str, help='the path to save the files',
            default='album')
    parser.add_argument('-count', type=int,
            help='how many images to download ?',
            default=None)
    args = parser.parse_args()


    main(args)

