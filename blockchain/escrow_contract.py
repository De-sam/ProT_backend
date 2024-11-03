from pyteal import *

# Define escrow conditions
def approval_program():
    # Define the conditions under which the funds are released
    is_customer = Txn.sender() == Addr("CFJYTKAYUAQJJY4BO3ZBBS6JZSZCYW36GOYZIJR5RSZQZIWYOBXVA5OBDI")
    is_tailor = Txn.sender() == Addr("H52NV44MLLK3R4G7OYKW62XYH453ZGRFIJTIXPKB73DHD6ZEBRVNYU4BJI")


    # Conditions for releasing funds
    release_funds = And(
        Txn.application_args[0] == Bytes("release"),  # action argument must be 'release'
        is_customer
    )

    # Conditions for refunding funds to tailor if the customer does not approve
    refund_funds = And(
        Txn.application_args[0] == Bytes("refund"),  # action argument must be 'refund'
        is_tailor
    )

    # Program logic
    program = Cond(
        [release_funds, Return(Int(1))],  # approve the release
        [refund_funds, Return(Int(1))],   # approve the refund
    )

    return program

# Clear state program
def clear_state_program():
    return Return(Int(1))

# Compile the program
if __name__ == "__main__":
    with open("escrow_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=2)
        f.write(compiled)
    with open("escrow_clear.teal", "w") as f:
        compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=2)
        f.write(compiled)
