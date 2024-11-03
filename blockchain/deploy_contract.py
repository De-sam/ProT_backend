from algosdk import mnemonic, account
from algosdk.v2client import algod
from algosdk.transaction import ApplicationCreateTxn, OnComplete
from algosdk.transaction import StateSchema
import base64
from pyteal import compileTeal, Mode
from escrow_contract import approval_program, clear_state_program  # Assuming your PyTeal functions are here

# Constants
ALGOD_ADDRESS = "http://localhost:4001"  # Adjust for sandbox
ALGOD_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"  # Sandbox default
CREATOR_MNEMONIC = "reward abandon essence globe velvet leaf barely olympic margin wasp portion bonus fine call job typical vintage neutral dumb salute test lens render absorb axis"  # Use the sandbox mnemonic

# Initialize Algorand client
algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# Convert the mnemonic to a private key and derive the public address
creator_private_key = mnemonic.to_private_key(CREATOR_MNEMONIC)
creator_address = account.address_from_private_key(creator_private_key)

def deploy_smart_contract():
    # Compile the PyTeal code to TEAL
    approval_teal = compileTeal(approval_program(), mode=Mode.Application, version=2)
    clear_teal = compileTeal(clear_state_program(), mode=Mode.Application, version=2)
    
    # Compile approval and clear programs to binary
    approval_result = algod_client.compile(approval_teal)
    clear_result = algod_client.compile(clear_teal)
    
    # Convert compiled programs from base64 to bytes
    approval_program_bytes = base64.b64decode(approval_result["result"])
    clear_program_bytes = base64.b64decode(clear_result["result"])
    
    # Set global and local schema (number of integer and byte slots)
    global_schema = StateSchema(num_uints=1, num_byte_slices=1)
    local_schema = StateSchema(num_uints=0, num_byte_slices=0)
    
    # Define the transaction to create the application
    params = algod_client.suggested_params()
    txn = ApplicationCreateTxn(
        sender=creator_address,
        sp=params,
        on_complete=OnComplete.NoOpOC,
        approval_program=approval_program_bytes,
        clear_program=clear_program_bytes,
        global_schema=global_schema,
        local_schema=local_schema,
        app_args=[b"release"],  # Example argument; use "release" or "refund" as needed
    )
    
    # Sign and send the transaction
    signed_txn = txn.sign(creator_private_key)
    txid = algod_client.send_transaction(signed_txn)
    print(f"Transaction sent with txID: {txid}")
    
    # Wait for confirmation
    confirmed_txn = wait_for_confirmation(algod_client, txid)
    
    # Retrieve and print the application ID
    app_id = confirmed_txn["application-index"]
    print(f"Smart contract deployed with App ID: {app_id}")
    
    return app_id

def wait_for_confirmation(client, txid):
    """Utility function to wait until the transaction is confirmed."""
    last_round = client.status().get('last-round')
    while True:
        txinfo = client.pending_transaction_info(txid)
        if txinfo.get('confirmed-round', 0) > 0:
            return txinfo
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)

# Deploy the smart contract
if __name__ == "__main__":
    app_id = deploy_smart_contract()
    print("Contract successfully deployed with App ID:", app_id)
