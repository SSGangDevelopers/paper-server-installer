import aiohttp
import tqdm


async def download_file(url: str, save_as: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            with open(save_as, 'wb') as f, \
                    tqdm.tqdm(
                        desc=save_as,
                        total=response.content.total_bytes,
                        unit='iB',
                        unit_scale=True,
                        unit_divisor=1024) as bar:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    size = f.write(chunk)
                    bar.update(size)
