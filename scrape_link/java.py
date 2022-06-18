import aiohttp


async def get(version: str = "17"):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.github.com/repos/adoptium/temurin17-binaries/releases/latest") as response:
            r = await response.json()
            for i in r["assets"]:
                dl_link = i["browser_download_url"]
                if dl_link.endswith(".tar.gz") and "jdk" in dl_link and "x64_linux" in dl_link and "debug" not in dl_link:
                    return dl_link
            else:
                print("NO JAVA DOWNLOAD FOUND. THIS IS A FATAL ERROR.")
                return None
