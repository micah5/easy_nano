import os
import time

import click
import pyqrcode
from easy_nano.lib import Account, generate_seed

SEED_PATH = os.getenv("SEED_PATH", "seed")


@click.group()
@click.option("--seed", required=False)
@click.pass_context
def main(ctx, seed):
    if seed is None:
        if os.path.exists(SEED_PATH):
            print("seed found, reading...")
            with open(SEED_PATH, "r") as file:
                seed = file.read()
        else:
            print("no seed found, generating...")
            seed = generate_seed()
            with open("seed", "w") as file:
                file.write(seed)
    ctx.obj = Account(seed=seed)


@main.command()
@click.pass_obj
def receive(account):
    """waits for new nano at account address"""
    qr = pyqrcode.create(account.public_address)
    print(qr.terminal(quiet_zone=1))
    while True:
        res = account.receive()
        if res:
            print(res)
            return
        time.sleep(5)


@main.command()
@click.pass_obj
@click.option("--address", prompt="Address", help="Nano address to send to")
@click.option("--amount", prompt="Amount", help="Amount of nano to send")
def send(account, address, amount):
    """sends nano to address"""
    print("Processing...")
    res = account.send(address, float(amount))
    print(res)
