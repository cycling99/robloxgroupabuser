import requests
from colorama import Fore, Style
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os
from queue import Queue

# THIS IS MICROSOFT WINDOWS ONLY
# THIS IS MICROSOFT WINDOWS ONLY
# THIS IS mICROSOFT WINDOWS ONLY


os.system('title syphoncore company - roblox group nuker [PUBLIC BUILD]')
def cls():
    os.system('cls' if os.name == 'nt' else 'clear')
def pause():
    os.system('pause' if os.name == 'nt' else 'pause')

statement = '''
[2024] syphoncore company

Syphoncore company software does NOT log cookies, or information of anykind.
Syphoncore does NOT permit the resale of this software or any other redistribution other than the offical GitHub page.

We are not responsible if anything happens to your Roblox account during, or after the use of our software.
-----
https://github.com/cycling99/robloxgroupabuser
https://github.com/cycling99/robloxgroupabuser/blob/main/main.py

'''

print(Fore.WHITE + f"{statement}")
time.sleep(5)
cls

BANNER = '''
 ░██████╗░██████╗░░█████╗░██╗░░░██╗██████╗░  ███╗░░██╗██╗░░░██╗██╗░░██╗███████╗
 ██╔════╝░██╔══██╗██╔══██╗██║░░░██║██╔══██╗  ████╗░██║██║░░░██║██║░██╔╝██╔════╝
 ██║░░██╗░██████╔╝██║░░██║██║░░░██║██████╔╝  ██╔██╗██║██║░░░██║█████═╝░█████╗░░
 ██║░░╚██╗██╔══██╗██║░░██║██║░░░██║██╔═══╝░  ██║╚████║██║░░░██║██╔═██╗░██╔══╝░░
 ╚██████╔╝██║░░██║╚█████╔╝╚██████╔╝██║░░░░░  ██║░╚███║╚██████╔╝██║░╚██╗███████╗
 ░╚═════╝░╚═╝░░╚═╝░╚════╝░░╚═════╝░╚═╝░░░░░  ╚═╝░░╚══╝░╚═════╝░╚═╝░░╚═╝╚══════╝
'''

RATE_LIMIT = 45  # seconds
ERROR_LIMIT = 30 # errors before aborting

cls()
os.system('title syphoncore company - roblox group nuker [PUBLIC BUILD] \\ Idling')
print(Fore.MAGENTA + Style.BRIGHT + BANNER)
print(Fore.RED + " [ Public Build ]\n")
print(Fore.BLUE + f"   [-] Rate limit cooldown: {RATE_LIMIT} seconds.")
print(Fore.BLUE + f"   [-] Error limit: {ERROR_LIMIT} errors.")
print(Fore.BLUE + "   [-] Recommended workers: 100 - 300.\n")

ROBLOX_SECURITY_COOKIE = input(Fore.WHITE + " [INPUT] Enter your ROBLOX .ROBLOSECURITY cookie >>> ")
GROUP_ID = int(input("[INPUT]  Enter the group ID >>> "))
NEW_RANK = input(" [INPUT] Enter the rank to rank users to >>> ")
MAX_WORKERS = int(input(" [INPUT] (Recommended: 100-300) Enter max workers >>> "))

cls()

HEADERS = {
    'Cookie': f'.ROBLOSECURITY={ROBLOX_SECURITY_COOKIE}',
    'Content-Type': 'application/json',
    'X-CSRF-TOKEN': ''
}

# get csrf
def get_csrf_token():
    response = requests.post('https://auth.roblox.com/v2/logout', headers=HEADERS)
    if response.status_code == 403:
        return response.headers['x-csrf-token']
    raise Exception(Fore.RED + "[ERROR] Unable to fetch CSRF token.")

# get group roles
def get_group_roles():
    response = requests.get(f'https://groups.roblox.com/v1/groups/{GROUP_ID}/roles', headers=HEADERS)
    response.raise_for_status()
    return response.json()['roles']

# get role id by name
def get_role_id_by_name(role_name):
    roles = get_group_roles()
    for role in roles:
        if role['name'].lower() == role_name.lower():
            return role['id']
    raise ValueError(Fore.RED + f"[ERROR]: Role '{role_name}' not found.")

# get bot userid
def get_bot_user_id():
    response = requests.get('https://users.roblox.com/v1/users/authenticated', headers=HEADERS)
    response.raise_for_status()
    return response.json()['id']

# get username in the group
def get_user_rank_in_group(user_id):
    response = requests.get(f'https://groups.roblox.com/v1/users/{user_id}/groups/roles', headers=HEADERS)
    response.raise_for_status()
    groups = response.json()['data']
    for group in groups:
        if group['group']['id'] == GROUP_ID:
            return group['role']['rank']
    return None

# get all group users
def get_all_users():
    users = []
    cursor = None
    limit = 100
    while True:
        params = {'limit': limit, 'cursor': cursor} if cursor else {'limit': limit}
        response = requests.get(f'https://groups.roblox.com/v1/groups/{GROUP_ID}/users', headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        users.extend(data['data'])
        cursor = data.get('nextPageCursor')
        if not cursor:
            break
    return users

# Change user role
def change_user_role(user, role_id, bot_rank, error_counter, success_counter):
    user_id, username = user['user']['userId'], user['user']['username']
    user_rank = user['role']['rank']

    # Skip if users rank is the same or higher than the bots rank
    if user_rank >= bot_rank:
        print(Fore.YELLOW + f"[?] Skipping {username}: rank [{user_rank}] is the same or higher than the bot's rank [{bot_rank}].")
        return False

    try:
        response = requests.patch(
            f'https://groups.roblox.com/v1/groups/{GROUP_ID}/users/{user_id}',
            headers=HEADERS,
            json={'roleId': role_id}
        )
        if response.status_code == 429:
            os.system('title syphoncore company - roblox group nuker [PUBLIC BUILD] \\ Ratelimited!')
            print(Fore.YELLOW + f"[?] Rate limit hit. Waiting {RATE_LIMIT}s for {username}.")
            time.sleep(RATE_LIMIT)
            return False
        response.raise_for_status()
        success_counter.put(1)
        print(Fore.GREEN + f"[SUCCESS] Ranked {username} to {NEW_RANK}. Total ranked: {success_counter.qsize()}")
        return True
    except requests.RequestException as e:
        error_counter.put(1)
        print(Fore.RED + f"[ERROR] Error ranking {username}: {e}")
        return False


HEADERS['X-CSRF-TOKEN'] = get_csrf_token()
TARGET_ROLE_ID = get_role_id_by_name(NEW_RANK)

bot_user_id = get_bot_user_id()
bot_rank = get_user_rank_in_group(bot_user_id)

if bot_rank is None:
    print(Fore.RED + "[ERROR]: Bot is not a member of the group.")
    pause()
    exit()

print(Fore.WHITE + f"Bot's rank in the group: {bot_rank}")
all_users = get_all_users()
print(Fore.GREEN + f"[SUCCESS] Loaded {len(all_users)} users.\n")

error_counter = Queue()
success_counter = Queue()

start_time = time.time()

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(change_user_role, user, TARGET_ROLE_ID, bot_rank, error_counter, success_counter) for user in all_users]

    for future in as_completed(futures):
        if error_counter.qsize() >= ERROR_LIMIT:
            print(Fore.RED + "[ERROR] Process stopped due to too many errors.")
            break
        try:
            future.result()
        except Exception as e:
            print(Fore.RED + f"[ERROR] Unexpected error: {e}")

elapsed_time = time.time() - start_time
os.system('title syphoncore company - roblox group nuker [PUBLIC BUILD] \\ Finished Ranking!')
print(Fore.WHITE + f"\nFinished! Ranked {success_counter.qsize()} users in {elapsed_time:.2f} seconds.")
pause()

# trippomg helped with this
