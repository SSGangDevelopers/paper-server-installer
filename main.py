import sys
import os
import tarfile
# Amazingly fast
import asyncio
import datetime

import log
import scrape_link
import downloader
import subprocess

import utils

HELP = """
==========================================================================
USAGE                                             DESCRIPTION
==========================================================================
backup (all|worlds|plugins|logs) <message>        Backup the server.
help                                              Show this help message.
init                                              Initialize the server.
"""


def init(quiet=False):
    print("Initializing...")
    plink = asyncio.run(scrape_link.paper.get())
    jlink = asyncio.run(scrape_link.java.get())

    async def download_both():
        await downloader.download_file(plink, "server/paper.jar")
        await downloader.download_file(jlink, "server/java.tar.gz")

    print("Downloading...")
    asyncio.run(download_both())
    with tarfile.open("server/java.tar.gz", "r:gz") as arc:
        arc.extractall("server/java")

    # Finds Java directory
    java_dir = os.listdir("server/java")[0] + "/bin/java"
    os.system(f"chmod +x server/java/{java_dir}")
    print("Running first time setup to initialize the server.")

    with open("server/start.sh", "w") as f:
        f.write(f"#!/bin/bash\ncd server\n{'java/' + java_dir} -jar  paper.jar -nogui")
    os.system("chmod +x server/start.sh")
    log.run_command_live_output("server/start.sh")
    with open("server/eula.txt", "r") as f:
        content = f.read()
    with open("server/eula.txt", "w") as f:
        if not quiet:
            if utils.is_affirmative(input("Do you accept Mojang's EULA? [y/N] ")) or quiet:
                f.write(content.replace("eula=false", "eula=true"))
            else:
                print("Abort.")
                sys.exit(1)
        else:
            f.write(content.replace("eula=false", "eula=true"))
    print("Starting server...")
    log.run_command_live_output("server/start.sh")


def backup(worlds: bool = True, plugins: bool = True, logs: bool = True, *, message: str):
    os.mkdir("backup")
    os.mkdir("backups")
    if worlds:
        os.mkdir("backup/worlds")
        os.mkdir("backups/worlds")
        print("Backing up world...")
        os.system("cp -r server/world backup/world")
        os.system("cp -r server/world_nether backup/world_nether")
        os.system("cp -r server/world_the_end backup/world_the_end")
    if plugins:
        print("Backing up plugins...")
        os.system("cp -r server/plugins backup/plugins")
    if logs:
        print("Backing up logs...")
        os.system("cp -r server/logs backup/logs")
    with open("backup/manifest.json", "w") as f:
        f.write(
            f"""{'{'}
                "timestamp": {datetime.datetime.now().timestamp()},
                "message": "{message}",
                "os": "{sys.platform}"
                {'}'}
            """
        )
    print("Packing up...")
    filename = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    os.system(f"tar -czf backups/{filename}.tar.gz backup")
    print("Cleaning up...")
    os.system("rm -rf backup")
    print(f"Done! Saved as backups/{filename}.tar.gz")


if __name__ == "__main__":
    print(
        """Advanced Minecraft Tools - v1.1.0-ALPHA
Copyright (C) 2022  SpikeBonjour.

This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions; in compliance with the GNU GPLv3.

"""
    )

    args = sys.argv[1:]
    QUIET = "--quiet" in args
    if QUIET:
        del args[args.index("--quiet")]

    match args:
        case ["init", *_]:
            print("Trying to create server directory...")
            try:
                os.mkdir("server")
                init(QUIET)
            except FileExistsError:
                if not QUIET:
                    if utils.is_affirmative(input("The server directory already exists. Do you really want to "
                                                  "overwrite it? [y/N] ")) or QUIET:
                        os.system("rm -rf server")
                        os.mkdir("server")
                        init()
                    else:
                        print("Aborted.")
                        init()
                else:
                    os.system("rm -rf server")
                    os.mkdir("server")
                    init()

        case ["backup", *option]:
            if option[0] not in ["worlds", "plugins", "logs"] or len(option) != 2:
                print("Invalid option.")
            elif option[0] == "all":
                backup(message=option[1].replace("\"", ""))
            else:
                backup(worlds="worlds" in option, plugins="plugins" in option, logs="logs" in option, message=option[1].replace("\"", ""))
        case ["help"]:
            print(HELP)
        case ["-h"]:
            print(HELP)
        case ["--help"]:
            print(HELP)

