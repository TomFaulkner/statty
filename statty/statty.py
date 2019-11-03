import asyncio
import json
import sys

from os import environ
from ssl import SSLError
from typing import Tuple

import httpx


async def main(interval: int = 5):
    while True:
        results = await asyncio.gather(*(check(site) for site in sites))
        # write_to_db(...)
        print(results)
        await asyncio.sleep(interval)


async def write_to_db(res_time: int, json_data: dict):
    pass


async def check(url: str, timeout: int = 5):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, timeout=timeout)
            await client.close()  # why do i need to close this, shouldn't the context manager handle this?
        except (httpx.exceptions.ReadTimeout, httpx.exceptions.ConnectTimeout, OSError, SSLError) as e:
            print(f"{url} \t\tdid not finish\t{str(e)}")
            return url, None
        else:
            if not r.status_code == 200:
                return url, r.elapsed.microseconds
            else:
                return url, r.elapsed.microseconds


if __name__ == "__main__":
    pre = 'STATTY_'
    interval = int(environ.get(f'{pre}INTERVAL', 5))
    raw_sites: str = environ.get(f'{pre}SITES')
    if raw_sites:
        sites = raw_sites.split(' ')
    else:
        f_name: str = environ.get(f'{pre}CONFIG', './config.json')
        try:
            with open(f_name) as f:
                json.load(f)
        except Exception as e:
            print(str(e))
            print(f'No {pre}SITES variable and could not load {pre}CONFIG or ./config.json. Exiting.')
            sys.exit(1)

    asyncio.run(main(interval))
