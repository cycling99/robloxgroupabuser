import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')
def pause():
    os.system('pause' if os.name == 'nt' else 'pause')

# Variables (adjust if you want)

ratelimit = 45  # Default: 45 seconds, if you are still being ratelimited after the 45 second countdown change this to something higher
errorLimit = 25  # Default: 30 errors, change if there are errors that are not affecting ranking

cls()
print(" ")
print(" ░██████╗░██████╗░░█████╗░██╗░░░██╗██████╗░  ███╗░░██╗██╗░░░██╗██╗░░██╗███████╗")
print(" ██╔════╝░██╔══██╗██╔══██╗██║░░░██║██╔══██╗  ████╗░██║██║░░░██║██║░██╔╝██╔════╝")
print(" ██║░░██╗░██████╔╝██║░░██║██║░░░██║██████╔╝  ██╔██╗██║██║░░░██║█████═╝░█████╗░░")
print(" ██║░░╚██╗██╔══██╗██║░░██║██║░░░██║██╔═══╝░  ██║╚████║██║░░░██║██╔═██╗░██╔══╝░░")
print(" ╚██████╔╝██║░░██║╚█████╔╝╚██████╔╝██║░░░░░  ██║░╚███║╚██████╔╝██║░╚██╗███████╗")
print(" ░╚═════╝░╚═╝░░╚═╝░╚════╝░░╚═════╝░╚═╝░░░░░  ╚═╝░░╚══╝░╚═════╝░╚═╝░░╚═╝╚══════╝")
print(" made by cycling99")
print(" ")
print("══════════════════════════════════════════════════╗")
print(f" - Ratelimit cooldown is set to {ratelimit} seconds.")
print(f" - Error limit is set to {errorLimit} errors.")
print(" - The recommended amount of workers is 100 - 200.")
print("══════════════════════════════════════════════════╝")

# Checks if the script can connect to roblox
def internet_connection():
    try:
        response = requests.get("https://www.roblox.com/", timeout=5)
        return True
    except requests.ConnectionError:
        return False    
if internet_connection():
    print(" ")
    print(" - Connected to Roblox!")
else:
    print(" ")
    print(" - Unable to connect to Roblox!")
    print(" ")
    pause()
    exit()
print(" ")

# Enter in info
ROBLOX_SECURITY_COOKIE = input("Enter your ROBLOX .ROBLOSECURITY cookie: ")
GROUP_ID = int(input("Enter the group ID: "))
New_Rank = input("Enter the rank to rank users to: ")
MAX_WORKERS = int(input("(Recommended: 100-200) Enter the maximum number of workers: "))
send_shout = input("Do you want to send a group shout? (y/n): ").lower() == 'y'
if send_shout:
    message_to_send = input("Enter the shout message: ")

cls()

# Headers and settings
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
    pause()
    exit()

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
    retries = 5  

    while True:
        params = {'limit': limit}
        if cursor:
            params['cursor'] = cursor

        for attempt in range(retries):
            try:
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
                    return users
                break  
            except requests.HTTPError as e:
                if response.status_code == 500:
                    print(f"Server Error 500 {attempt + 1}. Retrying...")
                    time.sleep(2 ** attempt)
                    continue
                else:
                    print(f"HTTP error: {e}. Response: {response.text}")
                    raise  
            except requests.RequestException as e:
                print(f"Request failed: {e}")
                raise  

        else:
            print("Max retries reached. Returning somewhat loaded data.")
            return users

def change_user_role(user, role_id, error_counter, success_counter):
    user_id = user['user']['userId']
    username = user['user']['username']
    user_rank = user['role']['rank']

    if error_counter[0] >= errorLimit:
        print("Max error limit reached. Stopping the ranking.")
        return False

    if user['role']['id'] == role_id:
        print(f"{username} is already ranked {New_Rank}.")
        return False

    if user_rank >= bot_rank:
        print(f"Skipping {username} due to same or higher rank ({user_rank}) than the bot ({bot_rank}).")
        return False

# ranking script

    try:
        while True:
            response = requests.patch(
                f'https://groups.roblox.com/v1/groups/{GROUP_ID}/users/{user_id}',
                headers=HEADERS,
                json={'roleId': role_id}
            )

            if response.status_code == 429:
                print(f"Rate limit hit. Waiting {ratelimit} seconds before retrying for {username}.")
                time.sleep(ratelimit)
                continue
            response.raise_for_status()
            success_counter[0] += 1
            print(f"User {username} ranked to {New_Rank}. (Total ranked: {success_counter[0]})")
            return True
    except requests.RequestException as e:
        if response.status_code != 429:
            error_counter[0] += 1
            print(f"Failed to rank user {username}: {e}. Response: {response.text if response else 'No response'}")
        return False

# Get the CSRF token and acc details
HEADERS['X-CSRF-TOKEN'] = get_csrf_token()

try:
    TARGET_ROLE_ID = get_role_id_by_name(New_Rank)
except ValueError as e:
    print(e)
    pause()
    exit()

bot_user_id = get_bot_user_id()
bot_rank = get_user_rank_in_group(bot_user_id)
if bot_rank is None:
    print("Bot is not a member of the group.")
    pause()
    exit()

print(f"Bot's rank in the group is {bot_rank}")
print(f"Loading all group members, this may take a while...")

try:
    all_users = get_all_users()
    if all_users:
        print(" ")
        print("Users loaded successfully.")
        print(" ")
    else:
        print("No users found or unable to fetch users.")
except Exception as e:
    print(f"Failed to load users: {e}")
    all_users = []  

ranked_users_count = 0
error_counter = [0]
success_counter = [0]

# Start timing
start_time = time.time()

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(change_user_role, user, TARGET_ROLE_ID, error_counter, success_counter) for user in all_users]

    for future in as_completed(futures):
        if error_counter[0] >= errorLimit:
            print("Process stopped due to too many errors.")
            break
        try:
            future.result()
        except Exception as e:
            print(f"Error ranking user: {e}")

# End timing
end_time = time.time()
elapsed_time = end_time - start_time

# After Action Report (AAR)
print(" ")
print("After Action Report")
print("-----------------------------")
print(f"All users have been processed. {success_counter[0]} user(s) were ranked to {New_Rank}.")
print(f"Elapsed time: {elapsed_time:.2f} seconds.")
print(" ")
pause()
exit()

if error_counter[0] >= errorLimit:
    print(f"Stopped after {error_counter[0]} errors.")
    pause()
    exit()

if send_shout:
    shout_message = f"{message_to_send}"
    send_group_shout(shout_message)
else:
    print("Shout is disabled.")

