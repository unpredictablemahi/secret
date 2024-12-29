from web3 import Web3
from eth_account import Account
import time
import os
from data_bridge import data_bridge
from keys_and_addresses import private_keys, my_addresses, labels
from network_config import networks
import codecs

# Function to center the text
def center_text(text):
    terminal_width = os.get_terminal_size().columns
    lines = text.splitlines()
    centered_lines = [line.center(terminal_width) for line in lines]
    return "\n".join(centered_lines)

# Function to clear the terminal
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

ascii_art = """

\033[38;5;214m

  M   A   D   E       B   Y       R   E   V   E   R   B
  M   A   D   E       B   Y       R   E   V   E   R   B
  M   A   D   E       B   Y       R   E   V   E   R   B
  
\033[0m
"""

description = """
Bot Auto Bridge  https://bridge.t1rn.io/
"""

chain_symbols = {
    'Arbitrum Sepolia': '\033[34m',
    'OP Sepolia': '\033[91m',
    'Blast Sepolia': '\033[93m',
    'Base Sepolia': '\033[96m'
}

green_color = '\033[92m'
reset_color = '\033[0m'
menu_color = '\033[95m'

explorer_urls = {
    'Arbitrum Sepolia': 'https://sepolia.arbiscan.io/tx/',
    'OP Sepolia': 'https://sepolia-optimism.etherscan.io/tx/',
    'Blast Sepolia': 'https://testnet.blastscan.io/tx/',
    'Base Sepolia': 'https://sepolia.basescan.org/tx/',
    'BRN': 'https://brn.explorer.caldera.xyz/tx/'
}

def get_brn_balance(web3, my_address):
    balance = web3.eth.get_balance(my_address)
    return web3.from_wei(balance, 'ether')

def send_bridge_transaction(web3, account, my_address, data, network_name):
    nonce = web3.eth.get_transaction_count(my_address, 'pending')
    value_in_ether = 0.1
    value_in_wei = web3.to_wei(value_in_ether, 'ether')

    try:
        gas_estimate = web3.eth.estimate_gas({
            'to': networks[network_name]['contract_address'],
            'from': my_address,
            'data': data,
            'value': value_in_wei
        })
        gas_limit = gas_estimate + 1
    except Exception as e:
        print(f"Error estimating gas: {e}")
        return None

    base_fee = web3.eth.get_block('latest')['baseFeePerGas']
    priority_fee = web3.to_wei(1, 'gwei')
    max_fee = base_fee + priority_fee

    transaction = {
        'nonce': nonce,
        'to': networks[network_name]['contract_address'],
        'value': value_in_wei,
        'gas': gas_limit * 2,
        'maxFeePerGas': max_fee,
        'maxPriorityFeePerGas': priority_fee,
        'chainId': networks[network_name]['chain_id'],
        'data': data
    }

    try:
        signed_txn = web3.eth.account.sign_transaction(transaction, account.key)
    except Exception as e:
        print(f"Error signing transaction: {e}")
        return None

    try:
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        balance = web3.eth.get_balance(my_address)
        formatted_balance = web3.from_wei(balance, 'ether')

        brn_balance = get_brn_balance(Web3(Web3.HTTPProvider('https://brn.rpc.caldera.xyz/http')), my_address)

        explorer_link = f"{explorer_urls[network_name]}{web3.to_hex(tx_hash)}"

        print(f"{green_color} Sender Address: {account.address}")
        print(f"⛽ Gas Used: {tx_receipt['gasUsed']}")
        print(f"️ Block Number: {tx_receipt['blockNumber']}")
        print(f" ETH Balance: {formatted_balance} ETH")
        print(f" BRN Balance: {brn_balance} BRN")
        print(f" Explorer Link: {explorer_link}\n{reset_color}")

        return web3.to_hex(tx_hash), value_in_ether
    except Exception as e:
        print(f"Error sending transaction: {e}")
        return None, None

def process_network_transactions(network_name, bridges, chain_data, successful_txs):
    web3 = Web3(Web3.HTTPProvider(chain_data['rpc_url']))
    if not web3.is_connected():
        raise Exception(f"Unable to connect to network {network_name}")

    for bridge in bridges:
        for i, private_key in enumerate(private_keys):
            account = Account.from_key(private_key)
            data = data_bridge[bridge]
            result = send_bridge_transaction(web3, account, my_addresses[i], data, network_name)
            if result:
                tx_hash, value_sent = result
                successful_txs += 1

                if value_sent is not None:
                    print(f"{chain_symbols[network_name]} Total Successful Txs: {successful_txs} | {labels[i]} | Bridge: {bridge} | Bridge Amount: {value_sent:.5f} ETH ✅{reset_color}\n")
                else:
                    print(f"{chain_symbols[network_name]} Total Successful Txs: {successful_txs} | {labels[i]} | Bridge: {bridge} ✅{reset_color}\n")

                print(f"{'='*150}")
                print("\n")
            time.sleep(3)

    return successful_txs

def display_menu():
    print(f"{menu_color}Select the chain to perform the transactions:{reset_color}")
    print("")
    print(f"{chain_symbols['OP Sepolia']}1. OP -> BASE Sepolia{reset_color}")
    print(f"{chain_symbols['Base Sepolia']}2. BASE -> OP Sepolia{reset_color}")
    print(f"{chain_symbols['Arbitrum Sepolia']}3. BASE -> Arbitrum Sepolia{reset_color}")
    print(f"{chain_symbols['Blast Sepolia']}4. OP ↔ BLAST Sepolia Continuously{reset_color}")  # Added 4th option
    print(f"{menu_color}5. Run All Transactions Continuously{reset_color}")
    print("")
    choice = input("Enter your choice (1-5): ")
    return choice

def main():
    print("\033[92m" + center_text(ascii_art) + "\033[0m")
    print(center_text(description))
    print("\n\n")

    successful_txs = 0

    while True:
        choice = display_menu()
        clear_terminal()
        print("\033[92m" + center_text(ascii_art) + "\033[0m")
        print(center_text(description))
        print("\n\n")

        try:
            if choice == '1':
                print(f"{menu_color}Executing OP -> BASE Sepolia transactions continuously...{reset_color}")
                while True:
                    successful_txs = process_network_transactions('OP Sepolia', ["OP - BASE"], networks['OP Sepolia'], successful_txs)
                    print("Waiting for 10 seconds before retrying (OP -> BASE)...")
                    time.sleep(30)

            elif choice == '2':
                print(f"{menu_color}Executing BASE -> OP Sepolia transactions continuously...{reset_color}")
                while True:
                    successful_txs = process_network_transactions('Base Sepolia', ["BASE - OP"], networks['Base Sepolia'], successful_txs)
                    print("Waiting for 10 seconds before retrying (BASE -> OP)...")
                    time.sleep(30)

            elif choice == '3':
                print(f"{menu_color}Executing BASE -> Arbitrum Sepolia transactions continuously...{reset_color}")
                while True:
                    successful_txs = process_network_transactions('Base Sepolia', ["BASE - Arbitrum"], networks['Base Sepolia'], successful_txs)
                    print("Waiting for 10 seconds before retrying (BASE -> Arbitrum)...")
                    time.sleep(30)

            elif choice == '4':  # Added new option for two-way transactions
                print(f"{menu_color}Executing OP ↔ BLAST Sepolia transactions continuously...{reset_color}")
                while True:
                    successful_txs = process_network_transactions('OP Sepolia', ["OP - BLAST"], networks['OP Sepolia'], successful_txs)
                    print("Waiting for 10 seconds before retrying (OP -> BLAST)...")
                    time.sleep(30)

                    successful_txs = process_network_transactions('Blast Sepolia', ["BLAST - OP"], networks['Blast Sepolia'], successful_txs)
                    print("Waiting for 10 seconds before retrying (BLAST -> OP)...")
                    time.sleep(30)

            elif choice == '5':
                print(f"{menu_color}Executing transactions continuously from OP -> BASE, BASE -> OP, BASE -> Arbitrum, Arbitrum -> BASE, and OP ↔ BLAST...{reset_color}")
                while True:
                    successful_txs = process_network_transactions('OP Sepolia', ["OP - BASE"], networks['OP Sepolia'], successful_txs)
                    print("Waiting for 10 seconds before retrying (OP -> BASE)...")
                    time.sleep(30)

                    successful_txs = process_network_transactions('Base Sepolia', ["BASE - OP"], networks['Base Sepolia'], successful_txs)
                    print("Waiting for 10 seconds before retrying (BASE -> OP)...")
                    time.sleep(30)

                    successful_txs = process_network_transactions('Base Sepolia', ["BASE - Arbitrum"], networks['Base Sepolia'], successful_txs)
                    print("Waiting for 10 seconds before retrying (BASE -> Arbitrum)...")
                    time.sleep(30)

                    successful_txs = process_network_transactions('Arbitrum Sepolia', ["Arbitrum - BASE"], networks['Arbitrum Sepolia'], successful_txs)
                    print("Waiting for 10 seconds before retrying (Arbitrum -> BASE)...")
                    time.sleep(30)

                    successful_txs = process_network_transactions('OP Sepolia', ["OP - BLAST"], networks['OP Sepolia'], successful_txs)
                    print("Waiting for 10 seconds before retrying (OP -> BLAST)...")
                    time.sleep(30)

                    successful_txs = process_network_transactions('Blast Sepolia', ["BLAST - OP"], networks['Blast Sepolia'], successful_txs)
                    print("Waiting for 10 seconds before retrying (BLAST -> OP)...")
                    time.sleep(30)

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Waiting for 10 seconds before retrying...")
            time.sleep(30)

if __name__ == "__main__":
    main()

