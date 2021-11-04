import argparse
import asyncio
import logging
import os
import sys

from src.utility import find_torrents_recursively, download_file


async def main(root_url: str, target_dir: str):
    logging.info(f'Searching torrent files recursively, starting at {root_url}')
    torrent_file_urls = await find_torrents_recursively(root_url)
    logging.info(f'Found {len(torrent_file_urls)} image torrent files')

    downloaded, skipped = 0, 0
    for torrent_file_url in torrent_file_urls:
        filename = os.path.basename(torrent_file_url)
        download_file_path = os.path.join(target_dir, filename)
        if not os.path.isfile(download_file_path):
            logging.info(f'Downloading new torrent file {filename}')
            await download_file(torrent_file_url, download_file_path)
            downloaded += 1
        else:
            logging.debug(f'Skipping existing torrent file {filename}')
            skipped += 1

    logging.info(f'Downloaded {downloaded} new torrent files')
    logging.info(f'Skipped {skipped} existing torrent files')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get all available ISO torrents from a Linux distro release directory')
    parser.add_argument('--root-url', help='URL of distro release directory (e.g. https://releases.ubuntu.com/)',
                        type=str, required=True)
    parser.add_argument('--target-dir', help='Path to directory to download torrent files into', type=str,
                        required=True)
    parser.add_argument('--debug', help='Output tons of debugging information', dest='debug', action='store_true')
    parser.set_defaults(debug=False)
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s', stream=sys.stdout)
    asyncio.run(main(args.root_url, os.path.realpath(args.target_dir)))
