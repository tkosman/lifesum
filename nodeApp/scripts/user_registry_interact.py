from brownie import *

p = project.load('../../nodeApp', name="NodeappProject")
p.load_config()

from brownie.project.NodeappProject import *
network.connect('sepolia')

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load private key and set up deployer account (you must have the private key in your .env file)
private_key = os.getenv("PRIVATE_KEY")
deployer = accounts.add(private_key)

# Connect to Sepolia network
#network.connect('sepolia')

# Get contract ABI from build artifacts
user_registry = UserRegistry[-1]

# 1. Register a new user
def register_user(nick, public_key, additional_data, is_bot):
    try:
        tx = user_registry.registerUser(nick, public_key, additional_data, is_bot, {"from": deployer})
        tx.wait(1)  # Wait for the transaction to be mined
        print(f"User {nick} registered successfully!")
    except Exception as e:
        print(f"Error while registering user: {str(e)}")

# 2. Add an expert field to an existing user
def add_expert_field(nick, field_id):
    try:
        tx = user_registry.addExpertField(nick, field_id, {"from": deployer})
        tx.wait(1)  # Wait for the transaction to be mined
        print(f"Expert field {field_id} added to {nick}.")
    except Exception as e:
        print(f"Error while adding expert field: {str(e)}")

# 3. Get user information by nick
def get_user_info(nick):
    try:
        public_key, expert_fields, additional_data, is_bot = user_registry.getUserInfo(nick)
        print(f"User Info for {nick}:")
        print(f"  Public Key: {public_key}")
        print(f"  Expert Fields: {expert_fields}")
        print(f"  Additional Data: {additional_data}")
        print(f"  Is Bot: {is_bot}")
    except Exception as e:
        print(f"Error while getting user info: {str(e)}")

# 4. Get user nickname by address
def get_nick_by_address(address):
    try:
        nick = user_registry.getNickByAddress(address)
        print(f"Nick for address {address}: {nick}")
    except Exception as e:
        print(f"Error while getting nickname by address: {str(e)}")

# Example Usage
def main():
        # Register a user
    register_user("Alice", "0xYourPublicKeyHere", "Some additional data", False)

    # Add expert field for Alice
    add_expert_field("Alice", 1)

    # Get user info for Alice
    get_user_info("Alice")

    # Get nickname by address (replace with actual address)
    get_nick_by_address("0xYourPublicKeyHere")

if __name__ == '__main__':
    main()
