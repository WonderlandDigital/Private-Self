import os
import requests
import sys
sys.path.insert(0, 'discord.py-self')
sys.path.insert(0, 'discord.py-self_embed')
import ctypes
import time
import discord
import colorama
from colorama import Fore
import ctypes
import random
import json
import openapi
import hashlib
import re
import socket
import subprocess
from datetime import datetime
from discord.ext import commands

#allowed_user_ids = [1190316592911892574, 176217706440294400]
processed_messages = set()
actions_completed = False
cooldown_active = False
logo = requests.get('https://pastebin.com/raw/dwnnXdY9').text
version = "1"
remaining_days = ""

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def Line(msg):
    print(f"[{Fore.LIGHTGREEN_EX} + {Fore.RESET}] {msg}", end='')

def Error_Line(msg):
    print(f"[{Fore.RED} X {Fore.RESET}]", msg, end='')

def authentication():
    global remaining_days
    # Get HWID (Hardware ID)
    change_window_title("[Private Self] - Authentication")
    hwid = hashlib.sha256(subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip().encode()).hexdigest()

    # Get Local IP address
    ip_address = [i[4][0] for i in socket.getaddrinfo(socket.gethostname(), None) if i[0] == socket.AF_INET and not i[4][0].startswith("127.")][0] if socket.has_ipv6 else None

    Line(f"Your HWID: {hwid}\n")
    Line(f"Your IP Address: {ip_address}\n")

    # Retrieve authentication data from Pastebin link
    pastebin_url = 'https://pastebin.com/raw/GRxXtT0r'
    auth_data = requests.get(pastebin_url).text

    # Search for IP and HWID in the text
    pattern = re.compile(r'(\w+):(\d+\.\d+\.\d+\.\d+):([a-fA-F0-9]+):(\d{4}-\d{2}-\d{2})')
    match = pattern.search(auth_data)
    while match:
        username, stored_ip, stored_hwid, expiration_date = match.groups()
        if ip_address == stored_ip and hwid == stored_hwid:
            Line(f"Name: {username}\n")
            # Calculate remaining days
            expiration_datetime = datetime.strptime(expiration_date, "%Y-%m-%d")
            remaining_days = (expiration_datetime - datetime.now()).days
            if remaining_days > 0:
                Line(f"Remaining Days: {remaining_days}\n")
                time.sleep(2)
                return remaining_days
                return True
            else:
                if remaining_days < -1:
                    Error_Line(f"Authentication failed due to expiration {str(remaining_days)[1:]} days ago!\n")
                else:
                    Error_Line(f"Authentication failed due to expiration {str(remaining_days)[1:]} day ago!\n")
                return False
                
            
        # Search for next IP and HWID in the text
        match = pattern.search(auth_data, match.end())

    print("Authentication failed!")
    return False
    
    


def change_window_title(msg):
    ctypes.windll.kernel32.SetConsoleTitleW(f"{msg}")
  
def read_settings(settings_file_path):

    if not os.path.exists(settings_file_path):
        name, prefix, discord_password, auto_reply, ping_detection, nitro_gifts, message_to_reply, _token = create_settings()
        default_settings = {
            'Who are you?': f'{name}',
            'Token?': f'{_token}',
            'Prefix?': f'{prefix}',
            'Discord Password?': f'{discord_password}',
            'Do you want to auto reply to messages?': auto_reply,
            'Want to snipe Nitro gifts?': nitro_gifts,
            'Want to detect pings?': ping_detection,
            'How would you like to reply to pings?': f'{message_to_reply}'
        }
        os.makedirs(os.path.dirname(settings_file_path), exist_ok=True)
        with open(settings_file_path, 'w') as file:
            json.dump(default_settings, file, indent=4)

    try:
        with open(settings_file_path, 'r') as file:
            config = json.load(file)
            return config
        
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error loading settings: {e}")
        return None
    
def create_settings():
    change_window_title(f"[Private Self] - Setup") 
    try:
        questions = [
            "What is your name?: ",
            "What prefix would you like to use?: ",
            "What is your Discord Password?: ",
            "Do you want to automatically reply to messages? (Y/n): ",
            "Want to detect pings in a log file? (Y/n): ",
            "Want to snipe Nitro Gifts? (Y/n): ",
            "Lastly, what is your token?: "
        ]
        answers = []
        auto_reply_desired = False

        for i, question in enumerate(questions):
            Line(question)
            temp = input()
            answers.append(temp)
            if i == 3 and temp.lower() == "y":
                auto_reply_desired = True

                # If user wants to automatically reply, ask for automatic message reply to a ping
                if auto_reply_desired:
                    Line("What would you like your automatic message reply to a ping?: ")
                    auto_reply = input()
                    answers.append(auto_reply)
            elif i == 3 and temp.lower() == "n":
                auto_reply = ""
                answers.append(auto_reply)

    except Exception as e:
        print(e)

    ping_detection = True if answers[4].lower() == "y" else False
    nitro_gifts = True if answers[6].lower() == "y" else False
    answers[5] = True if answers[5].lower() == "y" else False
    answers[3] = True if answers[3].lower() == "y" else False

    return answers[0], answers[1], answers[2], answers[3], answers[5], nitro_gifts, auto_reply, answers[7]
    

def create_preset_commands():
    command_list = [
        "https://cdn.discordapp.com/attachments/1094392564200767499/1206405515849105418/utility.py?ex=65dbe3b0&is=65c96eb0&hm=0d69fbe46b48cb08d7ec3b82905ecc969e81f7cbdc7898742f8462ffa4da5f70&", # UTILITY COMMANDS
        "https://cdn.discordapp.com/attachments/1094392564200767499/1206405534031286342/troll.py?ex=65dbe3b5&is=65c96eb5&hm=2b22b546c9a44d422b98e4fbdd4bfd0aabf3ede8527049549d537ee6082f50d5&", # TROLL COMMANDS
        "https://cdn.discordapp.com/attachments/1094392564200767499/1206405547348459520/misc.py?ex=65dbe3b8&is=65c96eb8&hm=31e301a6680487ebcced8bcc4ed786b33b7fcf181a136dfe94bcec6f74fc7ff1&" # MISC COMMANDS
    ]
    
    directory = "./Configuration/Commands"
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        pass
        
    for url in command_list:
        filename = os.path.join(directory, url.split('/')[-1].split('?')[0])
        if not os.path.exists(filename):
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
            else:
                Error_Line(f"There was an error downloading required modules for file: {filename}")
        else:
            pass
                

def load_cogs(private, prefix):
    for filename in os.listdir('./Configuration/Commands'):
        if filename.endswith('.py'):
            private.load_extension(f'Configuration.Commands.{filename[:-3]}')

def changelog():
    clear()
    change_window_title("[Private Self] - Changelog")
    changelog = requests.get("https://raw.githubusercontent.com/WonderlandDigital/Private-Self/main/changelog.md").text
    print("\n", changelog)
            
def main():
    clear()    
    settings_file_path = os.path.join(os.path.dirname(__file__), 'Configuration', 'Settings.json')
    config = read_settings(settings_file_path)
    create_preset_commands()

    if config is not None:
        privatename = config.get('Who are you?', '')
        token = config.get('Token?', '')
        prefix = config.get('Prefix?', '')
        password = config.get('Discord Password?', '')
        message_to_reply = config.get('Auto Reply Message?', '')
        nitro_sniper = config.get("Want to snipe Nitro gifts?", False)
        ping_detection = config.get("Want to detect pings?", False)
        custom_snipe = config.get('Custom Snipe Message?', '')

        private = commands.Bot(command_prefix=prefix, self_bot=True, intents=None)
        
        @private.event
        async def on_ready():
            clear()
            change_window_title("[Private Self] - Retrieving necessary files")
            Line(f"Hi, {privatename} welcome to Private Self V{version}.\n      The program will start shortly.")
            time.sleep(2)
            changelog()
            time.sleep(3)

            
            change_window_title(f"[Private Self] - [Logged in as: {private.user.name}] - [Guild Count: {len(private.guilds)}] - [Remaining Days: {remaining_days}]")
            clear()
            print(logo, f"             [V{version}]\n")
            print(f"Logged in as {private.user.name}")
            print(f"We support custom self-bot commands, use {prefix} help to get started.")
            load_cogs(private, prefix)



        @private.listen("on_message")
        async def automaticpingreply(message):
            #now = datetime.datetime.now()
            #current_time = now.strftime("%H:%M:%S")
            if f'<@{private.user.id}>' in str(message.content):
                log = open(f'Configuration/Logs/pings.txt', 'a', encoding="utf-8")
                log.write(f"\n >>PING DETECTED<<\nMessage: {message.content}\nAuthor: {message.author}\nServer: {message.guild.name}\nChannel Name: {message.channel.name}\nChannel ID: {message.channel.id}\n")
                log.close()
                async with message.channel.typing():
                    time.sleep(1)
                    msg = await message.reply(message_to_reply)
                    print(Fore.LIGHTRED_EX + f"\n", ">>", Fore.RED + "PING DETECTED", Fore.LIGHTRED_EX + "<<", f"\nAuthor: {message.author}\nChannel: {message.guild.name}\nChannel ID: {message.channel.id}\nMessage {message.content}\n")
                    time.sleep(2)
                    await msg.delete()
                    
                
            
            

        private.run(token)

try:
    colorama.init()
    auth_result = authentication()
    
    if not auth_result:
        time.sleep(10)
        sys.exit()
        
    else:
        main()
        
except Exception as e:
    print(e)
