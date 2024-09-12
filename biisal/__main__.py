# (c) @biisal
# (c) adarsh-goel
import os
import sys
import glob
import asyncio
import logging
import importlib
from pathlib import Path
from pyrogram import idle
from .bot import StreamBot
from .vars import Var
from aiohttp import web
from .server import web_server
from .utils.keepalive import ping_server
from biisal.bot.clients import initialize_clients
from pyrogram import types
from pyrogram import utils as pyroutils

pyroutils.MIN_CHAT_ID = -999999999999
pyroutils.MIN_CHANNEL_ID = -100999999999999

LOGO = """
 ____ ___ ___ ____    _    _     
| __ )_ _|_ _/ ___|  / \  | |    
|  _ \| | | |\___ \ / _ \ | |    
| |_) | | | | ___) / ___ \| |___ 
|____/___|___|____/_/   \_\_____|"""

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

ppath = "biisal/bot/plugins/*.py"
files = glob.glob(ppath)
StreamBot.start()

async def start_services():
    print('\n')
    print('------------------- Initalizing Telegram Bot -------------------')
    bot_info = await StreamBot.get_me()
    StreamBot.username = bot_info.username
    print("------------------------------ DONE ------------------------------")
    print()
    print(
        "---------------------- Initializing Clients ----------------------"
    )
    await initialize_clients()
    print("------------------------------ DONE ------------------------------")
    print('\n')
    print('--------------------------- Importing ---------------------------')
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"biisal/bot/plugins/{plugin_name}.py")
            import_path = ".plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["biisal.bot.plugins." + plugin_name] = load
            print("Imported => " + plugin_name)
    
    if Var.ON_HEROKU:
        print("------------------ Starting Keep Alive Service ------------------")
        print()
        asyncio.create_task(ping_server())
    
    print('-------------------- Initalizing Web Server -------------------------')
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0" if Var.ON_HEROKU else Var.BIND_ADRESS
    await web.TCPSite(app, bind_address, Var.PORT).start()
    print('----------------------------- DONE ---------------------------------------------------------------------')
    print('\n')
    print('----------------------- Service Started -----------------------------------------------------------------')
    print(f"Bot => {StreamBot.username}")
    print(f"Server running on => {bind_address}:{Var.PORT}")
    print(f"Owner => {Var.OWNER_USERNAME}")
    
    if Var.ON_HEROKU:
        print(f"App running on => {Var.FQDN}")
    
    print('---------------------------------------------------------------------------------------------------------')
    print(LOGO)
    
    try:
        await StreamBot.send_message(chat_id=Var.OWNER_ID[0], text='<b>Bot restarted successfully!</b>')
    except Exception as e:
        print(f'Error sending restart message: {e}')
    
    await idle()

if __name__ == '__main__':
    try:
        # Using asyncio.run() for better event loop handling
        asyncio.run(start_services())
    except KeyboardInterrupt:
        logging.info('----------------------- Service Stopped -----------------------')
