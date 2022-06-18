import aiohttp

# /builds/27/downloads/paper-1.19-27.jar


async def get(version: str = "1.19"):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.papermc.io/v2/projects/paper/versions/{version}") as response:
            r = await response.json()
            latest_build = max(r["builds"])

        async with session.get(f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{latest_build}") as response:
            r = await response.json()
            artifact_name = r["downloads"]["application"]["name"]

        return f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{latest_build}/downloads/{artifact_name}"

