import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os

print(" ")
print("░██████╗░██████╗░░█████╗░██╗░░░██╗██████╗░  ░█████╗░██████╗░██╗░░░██╗░██████╗███████")
print("██╔════╝░██╔══██╗██╔══██╗██║░░░██║██╔══██╗  ██╔══██╗██╔══██╗██║░░░██║██╔════╝██╔════╝")
print("██║░░██╗░██████╔╝██║░░██║██║░░░██║██████╔╝  ███████║██████╦╝██║░░░██║╚█████╗░█████╗░░")
print("██║░░╚██╗██╔══██╗██║░░██║██║░░░██║██╔═══╝░  ██╔══██║██╔══██╗██║░░░██║░╚═══██╗██╔══╝░░")
print("╚██████╔╝██║░░██║╚█████╔╝╚██████╔╝██║░░░░░  ██║░░██║██████╦╝╚██████╔╝██████╔╝███████╗")
print("░╚═════╝░╚═╝░░╚═╝░╚════╝░░╚═════╝░╚═╝░░░░░  ╚═╝░░╚═╝╚═════╝░░╚═════╝░╚═════╝░╚══════╝")
print(" ")
print("Made by trippomg")
print("made better by cycling99")
print(" ")

ratelimit = 45 # May be raised if there is problems

# enter in info
ROBLOX_SECURITY_COOKIE = input("Enter your ROBLOX .ROBLOSECURITY cookie: ")
GROUP_ID = int(input("Enter the group ID: "))
New_Rank = input("Enter the rank to promote users to: ")
MAX_WORKERS = int(input("Enter the maximum number of workers: "))
send_shout = input("Do you want to send a group shout? (y/n): ").lower() == 'y'
if send_shout:
    message_to_send = input("Enter the shout message: ")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

clear_screen()

# headers and settings
HEADERS = {
    'Cookie': f'.ROBLOSECURITY={ROBLOX_SECURITY_COOKIE}',
    'Content-Type': 'application/json',
    'X-CSRF-TOKEN': ''
}

def send_group_shout(message):
    shout_data = {'message': message}
    response = requests.patch(
        f'https://groups.roblox.com/v1/groups/{GROUP_ID}/status',
        headers=HEADERS,
        json=shout_data
    )
    response.raise_for_status()
    print("Sent the shout.")

def get_csrf_token():
    response = requests.post('https://auth.roblox.com/v2/logout', headers=HEADERS)
    if response.status_code == 403:
        return response.headers['x-csrf-token']
    raise Exception("Can't get CSRF token")
    exit(3)

def get_bot_user_id():
    response = requests.get('https://users.roblox.com/v1/users/authenticated', headers=HEADERS)
    response.raise_for_status()
    return response.json()['id']

def get_user_rank_in_group(user_id):
    response = requests.get(f'https://groups.roblox.com/v1/users/{user_id}/groups/roles', headers=HEADERS)
    response.raise_for_status()
    groups = response.json()['data']
    for group in groups:
        if group['group']['id'] == GROUP_ID:
            return group['role']['rank']
    return None

def get_group_roles():
    response = requests.get(f'https://groups.roblox.com/v1/groups/{GROUP_ID}/roles', headers=HEADERS)
    response.raise_for_status()
    return response.json()['roles']

def get_role_id_by_name(role_name):
    roles = get_group_roles()
    for role in roles:
        if role['name'].lower() == role_name.lower():
            return role['id']
    raise ValueError(f"The '{role_name}' role was not found")

def get_all_users():
    users = []
    cursor = None
    limit = 100

    while True:
        params = {'limit': limit}
        if cursor:
            params['cursor'] = cursor

        response = requests.get(
            f'https://groups.roblox.com/v1/groups/{GROUP_ID}/users',
            headers=HEADERS,
            params=params
        )
        response.raise_for_status()
        data = response.json()
        users.extend(data['data'])
        cursor = data.get('nextPageCursor')

        if not cursor:
            break

    return users

def change_user_role(user, role_id, error_counter, success_counter):
    user_id = user['user']['userId']
    username = user['user']['username']
    user_rank = user['role']['rank']
    
    if error_counter[0] >= 6:
        print("Max error limit reached. Stopping the process.")
        return False

    if user['role']['id'] == role_id:
        print(f"{username} is already ranked {New_Rank}.")
        return False

    if user_rank >= bot_rank:
        print(f"Skipping {username} due to same or higher rank ({user_rank}) than the bot ({bot_rank}).")
        return False

    try:
        while True:
            response = requests.patch(
                f'https://groups.roblox.com/v1/groups/{GROUP_ID}/users/{user_id}',
                headers=HEADERS,
                json={'roleId': role_id}
            )

            if response.status_code == 429:  # Rate limit
                print(f"Rate limit hit. Waiting {t} seconds before retrying for {username}.")
                time.sleep(ratelimit)
                continue
            response.raise_for_status()
            success_counter[0] += 1
            print(f"User {username} promoted to {New_Rank}. (Total promoted: {success_counter[0]})")
            return True
    except requests.RequestException as e:
        if response.status_code != 429:  # Non-rate-limit error
            error_counter[0] += 1
            print(f"Failed to promote user {username}: {e}. Response: {response.text if response else 'No response'}")
        return False

# get the CSRF token and bot details
HEADERS['X-CSRF-TOKEN'] = get_csrf_token()

try:
    TARGET_ROLE_ID = get_role_id_by_name(New_Rank)
except ValueError as e:
    print(e)
    exit(3)

bot_user_id = get_bot_user_id()
bot_rank = get_user_rank_in_group(bot_user_id)
if bot_rank is None:
    print("Bot is not a member of the group.")
    exit(3)

print(f"Bot's rank in the group is {bot_rank}")
print(f"Loading all group members, this may take a while...")

all_users = get_all_users()

if all_users:
    print("Users loaded successfully.")
ranked_users_count = 0
error_counter = [0] # trackers errors until it reaches 6 errors
success_counter = [0]  # keeps track of successful promotions

# process the users in parallel
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(change_user_role, user, TARGET_ROLE_ID, error_counter, success_counter) for user in all_users]

    for future in as_completed(futures):
        if error_counter[0] >= 6:
            print("Process stopped due to too many errors.")
            break
        try:
            future.result()
        except Exception as e:
            print(f"Error ranking user: {e}")

# final output
print(f"All users have been processed. {success_counter[0]} user(s) were promoted to {New_Rank}.")
if error_counter[0] >= 6:
    print(f"Stopped after {error_counter[0]} errors.")

# send shout if enabled
if send_shout:
    shout_message = f"{message_to_send}"
    send_group_shout(shout_message)
else:
    print("Shout is disabled.")

# made by trippomg
# made better by cycling99
# last update 10/6/24
