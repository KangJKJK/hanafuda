from web3 import Web3
import json
import time
from colorama import init, Fore, Style

init(autoreset=True)

# Constants
RPC_URL = "https://mainnet.base.org"
CONTRACT_ADDRESS = "0xC5bf05cD32a14BFfb705Fb37a9d218895187376c"
AMOUNT_ETH = 0.0000000001  # 예치할 ETH 양

# Contract ABI
CONTRACT_ABI = '''
[
    {
        "constant": false,
        "inputs": [],
        "name": "depositETH",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]
'''

# Web3 Connection
web3 = Web3(Web3.HTTPProvider(RPC_URL))
amount_wei = web3.to_wei(AMOUNT_ETH, 'ether')
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=json.loads(CONTRACT_ABI))

# Load Private Keys
with open("pvkey.txt", "r") as file:
    private_keys = [line.strip() for line in file if line.strip()]
nonces = {key: web3.eth.get_transaction_count(web3.eth.account.from_key(key).address) for key in private_keys}

# Display Header
def display_header():
    print(Fore.CYAN + Style.BRIGHT + """\n
    *********************************************
              HANA 자동 디파짓 봇입니다.
    *********************************************
    """ + Style.RESET_ALL)

# Display Footer
def display_footer(start_time):
    elapsed_time = time.time() - start_time
    print(Fore.MAGENTA + Style.BRIGHT + f"\n모든 거래가 {elapsed_time:.2f} 초에 완료되었습니다.\n")
    print(Fore.CYAN + "**************************************************" + Style.RESET_ALL)
    print(Fore.CYAN + "HANA 자동 디파짓 봇을 이용해주셔서 감사합니다.\n" + Style.RESET_ALL)
    print(Fore.CYAN + "**************************************************" + Style.RESET_ALL)

# Send Transactions
def send_transactions(num_transactions):
    tx_count = 0
    for i in range(num_transactions):
        for private_key in private_keys:
            from_address = web3.eth.account.from_key(private_key).address
            short_from_address = f"{from_address[:4]}...{from_address[-4:]}"
            try:
                tx_hash = execute_transaction(private_key, from_address, short_from_address)
                tx_count += 1

                # 거래 배치 제한
                if tx_count >= 50:
                    tx_count = 0
                time.sleep(1)  # 필요에 따라 지연 시간 조정

            except Exception as e:
                handle_exception(e, private_key, from_address, short_from_address)

# Execute Transaction
def execute_transaction(private_key, from_address, short_from_address):
    transaction = contract.functions.depositETH().build_transaction({
        'from': from_address,
        'value': amount_wei,
        'gas': 100000,
        'gasPrice': web3.eth.gas_price,
        'nonce': nonces[private_key]
    })

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)  
    tx_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(Fore.GREEN + f"[{tx_time}] {short_from_address}에서 거래가 전송되었습니다 - 해시: {tx_hash.hex()}")

    # nonce 업데이트
    nonces[private_key] += 1
    return tx_hash

# Handle Exceptions
def handle_exception(e, private_key, from_address, short_from_address):
    if 'nonce too low' in str(e):
        print(Fore.YELLOW + f"[경고] {short_from_address}의 nonce가 너무 낮습니다. nonce를 업데이트합니다...")
        nonces[private_key] = web3.eth.get_transaction_count(from_address)
    else:
        print(Fore.RED + f"[오류] {short_from_address}에서 거래 실패: {str(e)}")

# Main Execution
if __name__ == "__main__":
    display_header()
    num_transactions = int(input(Fore.YELLOW + "실행할 거래 수를 입력하세요: " + Style.RESET_ALL))
    print(Fore.CYAN + "\n거래 시작...\n" + Style.RESET_ALL)
    
    start_time = time.time()
    send_transactions(num_transactions)
    display_footer(start_time)
