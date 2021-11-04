import logging
from typing import List
from urllib.parse import urljoin

import aiofiles as aiofiles
import aiohttp
from bs4 import BeautifulSoup


async def find_torrents_recursively(root_url: str) -> List[str]:
    logging.debug(f'Fetching {root_url}')
    async with aiohttp.ClientSession() as session:
        resp = await session.get(root_url)
        text = await resp.text()
    soup = BeautifulSoup(text, 'html.parser')

    # Find all links to directories (excluding root)
    dir_urls = list(set([urljoin(root_url, link.get('href')) for link in
                         soup.select('a[href$="/"]:not([href^="http"]):not([href="/"])')]))
    logging.debug(f'Found {len(dir_urls)} unique links to directories')

    # Make sure url actually leads to sub directory and does not lead to self
    sub_dir_urls = [u for u in dir_urls if u.startswith(root_url) and u != root_url]
    logging.debug(f'Of those, {len(sub_dir_urls)} link to sub-directories')

    # Check for torrent files on current level
    torrents_file_urls = list(set([urljoin(root_url, link.get('href')) for link in
                                   soup.select('a[href$=".iso.torrent"], a[href$=".img.torrent"]')]))
    logging.debug(f'Found {len(torrents_file_urls)} unique image torrents in current directory')

    # Check for torrent files on sub-levels
    for sub_dir_url in sub_dir_urls:
        torrents_file_urls.extend(await find_torrents_recursively(sub_dir_url))

    return list(set(torrents_file_urls))


async def download_file(url: str, download_path: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(download_path, mode='wb')
                await f.write(await resp.read())
                await f.close()
