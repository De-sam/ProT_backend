# contracts/escrow_contract.py

from pyteal import *
from algosdk.v2client import algod
from algosdk.future.transaction import LogicSig, LogicSigTransaction

def escrow_contract(tailor_address: str, asa_id: int):
    """
    Define an escrow contract for handling payments in ASAs.
    
    - tailor_address: Address of the tailor who receives funds if conditions are met.
    - asa_id: ID of the ASA to be used for the transaction.
    """

    # Define the transaction conditions:
    # 1. Ensure the transaction is a payment in ASAs (Algorand Standard Assets).
    # 2. Verify the receiver is the tailor's address.
    # 3. Limit the transaction to a specific ASA ID.
    # 4. Include additional checks as needed.

    # Check if the transaction is an Asset Transfer and the correct ASA is used
    program = And(
        Txn.type_enum() == TxnType.AssetTransfer,
        Txn.xfer_asset() == Int(asa_id),  # Only allow transfers of the specified ASA
        Txn.asset_receiver() == Addr(tailor_address),  # Ensure tailor receives the ASA
        Txn.asset_amount() > Int(0)  # Only allow transactions with a non-zero amount
    )

    return compileTeal(program, mode=Mode.Signature)

def compile_and_deploy(client: algod.AlgodClient, tailor_address: str, asa_id: int):
    """
    Compile and deploy the escrow contract to Algorand TestNet.

    - client: An instance of AlgodClient connected to the network.
    - tailor_address: Address of the tailor for whom the contract is created.
    - asa_id: ID of the ASA involved in the transaction.
    """
    contract_code = escrow_contract(tailor_address, asa_id)
    
    # Compile the PyTeal code to TEAL bytecode
    response = client.compile(contract_code)
    contract_address = response["hash"]
    print("Contract Address:", contract_address)
    
    # The contract address can now be shared with the customer to initiate payments.
    return contract_address
