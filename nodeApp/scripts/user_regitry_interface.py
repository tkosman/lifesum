# user_registry_interface.py

import os
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
import json

class UserRegistryInterface:
    def __init__(self):
        load_dotenv()

        infura_project_id = os.getenv('WEB3_INFURA_PROJECT_ID')
        infura_url = f'https://mainnet.infura.io/v3/{infura_project_id}'
        self.web3 = Web3(Web3.HTTPProvider(infura_url))

        if not self.web3.isConnected():
            raise ConnectionError("Failed to connect to Ethereum network")

        private_key = os.getenv('PRIVATE_KEY')
        if not private_key:
            raise ValueError("Private key not found in environment variables")
        self.account = Account.from_key(private_key)
        self.web3.eth.default_account = self.account.address

        contract_address = os.getenv('USER_REGISTRY_ADDRESS')
        if not contract_address:
            raise ValueError("Contract address not found in environment variables")
        self.contract_address = self.web3.toChecksumAddress(contract_address)

        with open('UserRegistry.json') as f:
            contract_abi = json.load(f)

        self.contract = self.web3.eth.contract(
            address=self.contract_address,
            abi=contract_abi['abi']
        )

    def register_user(self, nick, public_key, additional_data, is_bot):
        try:
            tx = self.contract.functions.registerUser(
                nick,
                public_key,
                additional_data,
                is_bot
            ).buildTransaction({
                'from': self.account.address,
                'nonce': self.web3.eth.getTransactionCount(self.account.address),
                'gas': 300000,
                'gasPrice': self.web3.toWei('10', 'gwei'),
            })

            signed_tx = self.web3.eth.account.signTransaction(tx, private_key=self.account.key)
            tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
            print(f"Transaction hash: {tx_hash.hex()}")


            return tx_hash.hex()
        except Exception as e:
            print(f"An error occurred during register_user: {e}")
            return None

    def add_expert_field(self, nick, field_id):
        try:
            tx = self.contract.functions.addExpertField(
                nick,
                field_id
            ).buildTransaction({
                'from': self.account.address,
                'nonce': self.web3.eth.getTransactionCount(self.account.address),
                'gas': 200000,
                'gasPrice': self.web3.toWei('10', 'gwei'),
            })

            signed_tx = self.web3.eth.account.signTransaction(tx, private_key=self.account.key)
            tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
            print(f"Transaction hash: {tx_hash.hex()}")

            return tx_hash.hex()
        except Exception as e:
            print(f"An error occurred during add_expert_field: {e}")
            return None

    def get_user_info(self, nick):
        try:
            public_key, expert_fields, additional_data, is_bot = self.contract.functions.getUserInfo(nick).call()
            user_info = {
                'nick': nick,
                'public_key': public_key,
                'expert_fields': expert_fields,
                'additional_data': additional_data,
                'is_bot': is_bot
            }
            return user_info
        except Exception as e:
            print(f"An error occurred during get_user_info: {e}")
            return None

    def get_nick_by_address(self, address):
        try:
            nick = self.contract.functions.getNickByAddress(address).call()
            return nick
        except Exception as e:
            print(f"An error occurred during get_nick_by_address: {e}")
            return None
