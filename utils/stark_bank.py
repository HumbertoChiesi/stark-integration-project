import random
import os

import starkbank
from .random_person_data import PERSONS

private_key_content = os.getenv("PRIVATE_KEY")

project = starkbank.Project(
        environment="sandbox",
        id="6237131806605312",
        private_key=private_key_content
    )

starkbank.user = project

def get_sandbox_project() -> starkbank.Project:
    """# Get Sandbox Project
    Retrieves the Stark Bank Project set up for the sandbox environment.
    ## Return:
    - starkbank.Project object
    """
    return project

def generate_invoices():
    """# Generate Invoices
    Generate a random list of invoices with random amounts and associates them with random persons from the PERSONS list.
    This function creates between 8 to 12 invoices and sends them to the Stark Bank API for creation.
    ## Return:
    - list of Invoice objects with updated attributes
    """
    num_persons = random.randint(8, 12)
    selected_persons = random.sample(PERSONS, num_persons)
    invoices = []

    for person in selected_persons:
        invoices.append(starkbank.Invoice(amount=random.randint(10000, 100000), name=person["name"], tax_id=person["tax_id"]))
    
    return starkbank.invoice.create(invoices)

def create_transfer(amount: int) -> list:
    """# Create Transfer
    Creates a transfer to Stark Bank's specified account, with the specified amount.
    ## Parameters (required):
    - amount [int]: The amount to be transferred, in cents (e.g., 10000 equals 100.00 units of the currency)
    ## Return:
    - list of Transfer objects
    """
    transfer = starkbank.Transfer(
        bank_code="20018183",
        branch_code="0001",
        account_number="6341320293482496",
        name="Stark Bank S.A.",
        tax_id="20.018.183/0001-80",
        account_type="payment",
        amount=amount
    )

    return starkbank.transfer.create([transfer])