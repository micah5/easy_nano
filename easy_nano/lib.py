import decimal
import json
import warnings
import threading
from typing import Optional, Dict
from functools import partial

import requests
from nanolib import (
    generate_seed,
    generate_account_id,
    generate_account_private_key,
    Block,
    accounts,
    units,
)

ctx = decimal.Context()
ctx.prec = 20


# https://stackoverflow.com/questions/38847690/convert-float-to-string-in-positional-format-without-scientific-notation-and-fa
def float_to_str(f):
    """
    Convert the given float to a string,
    without resorting to scientific notation
    """
    d1 = ctx.create_decimal(repr(f))
    return format(d1, "f")


class Account:
    def __init__(
        self,
        seed: Optional[str] = None,
        idx: Optional[int] = 0,
        node_url: Optional[str] = "https://mynano.ninja/api/node",
        representative: Optional[
            str
        ] = "nano_1wenanoqm7xbypou7x3nue1isaeddamjdnc3z99tekjbfezdbq8fmb659o7t",  # wenano
    ):
        self.seed = generate_seed() if seed is None else seed
        account_id = generate_account_id(self.seed, idx)
        self.private_key = generate_account_private_key(self.seed, idx)
        self.public_address = accounts.get_account_id(
            private_key=self.private_key, prefix=accounts.AccountIDPrefix.NANO
        )
        self.node_url = node_url
        self.representative = representative
        self.threads = {}
        self.queue = []

    def _call_node_url(self, payload: Dict):
        res = requests.request("POST", self.node_url, data=payload)
        res.raise_for_status()
        data = res.json()
        if "error" in data:  # on error api returns 200 for some reason
            raise Exception(data["error"])
        else:
            return data

    def _get_block_info(self, block: str):
        data = self._call_node_url(
            {"action": "block_info", "json_block": True, "hash": block}
        )
        return data

    def _get_account_info(self, account_address: str):
        try:
            data = self._call_node_url(
                {"action": "account_info", "account": account_address}
            )
        except Exception as e:
            data = {"balance": 0}
        return data

    def receive(self, count: Optional[int] = 5, process_in_thread: bool = False):
        data = self._call_node_url(
            {"action": "pending", "account": self.public_address, "count": count}
        )
        ret_data = {}
        for idx, block_hash in enumerate(data["blocks"]):
            block_info = self._get_block_info(block_hash)
            block_addr = block_info["block_account"]
            amount = int(block_info["amount"])
            mnano_amount = self._get_mnano_amount(amount)
            # todo: implement proper logging
            print(f"Received {mnano_amount} nano from {block_addr}. Processing...")
            if process_in_thread:
                if block_hash in self.threads:
                    print(f"Thread {block_hash} already running...")
                else:
                    self.threads[block_hash] = None
                    t = threading.Thread(
                        target=partial(
                            self._receive_block,
                            link=block_hash,
                            amount=amount,
                            is_raw=True,
                            threading_enabled=True,
                        )
                    )
                    if len(self.queue) == 0 and idx == 0:
                        t.start()
                    else:
                        self.queue.append(t)
            else:
                self._receive_block(block_hash, amount, is_raw=True)
            ret_data[block_addr] = {
                "amount": mnano_amount,
                "hash": block_hash,
            }
        return ret_data if len(ret_data) > 0 else None

    def _process_block(self, block: Block, subtype: str):
        block_dict = block.to_dict()
        data = {
            "subtype": subtype,
            "action": "process",
            "block": block_dict,
            "json_block": True,
        }
        res = requests.post(self.node_url, json=data)
        data = res.json()
        if "hash" not in data:
            raise Exception(f"Transaction did not go through: {data}")
        return data["hash"]

    def _prepare_block(self, block: Block):
        block.solve_work()
        if not block.has_valid_work:
            raise Exception("Block does not have valid PoW")

        block.sign(self.private_key)
        if not block.has_valid_signature:
            raise Exception("Block does not have valid signature")

        if not block.complete:
            raise Exception("Block not ready to be broadcast")

    def _receive_block(
        self,
        link: str,
        amount: float,
        is_raw: bool = False,
        threading_enabled: bool = False,
    ):
        previous = self._get_previous_block_hash()
        amount = amount if is_raw else self._get_raw_amount(amount)
        account_info = self._get_account_info(self.public_address)
        total_amount = amount + int(account_info["balance"])
        block = Block(
            block_type="state",
            account=self.public_address,
            representative=self.representative,
            previous=previous,
            balance=total_amount,
            link=link,
        )
        is_genesis_block = previous == "0" * 64
        self._prepare_block(block)
        if threading_enabled:
            self.threads[link] = block.to_dict()
        res = self._process_block(block, "open" if is_genesis_block else "receive")
        if threading_enabled:
            if len(self.queue) > 0:
                t = self.queue.pop()
                t.start()
        return res

    def _get_raw_amount(self, amount: float):
        """to prevent rounding errors"""
        if amount < 1:
            # Über hack dont judge me!! FIXME
            num_zeros = float_to_str(amount).count("0")
            return (10 ** (30 - num_zeros)) * int(amount * 10 ** num_zeros)
        else:
            return (10 ** 30) * amount

    def _get_mnano_amount(self, amount: int):
        return amount / (10 ** 30)

    def _get_previous_block_hash(self):
        data = self._call_node_url(
            {"action": "account_history", "account": self.public_address, "count": 1}
        )
        history = data["history"]
        if len(history) < 1:
            return "0" * 64
        return history[0]["hash"]

    def send(self, address: str, amount: float, is_raw=False):
        previous = self._get_previous_block_hash()
        amount = amount if is_raw else self._get_raw_amount(amount)
        account_info = self._get_account_info(self.public_address)
        account_balance = int(account_info["balance"])
        if account_balance == 0:
            raise Exception(f"Account {self.public_address} has no nano avaliable")
        total_amount = account_balance - amount
        if total_amount < 0:
            raise Exception(
                f"Account {self.public_address} only has {self._get_mnano_amount(account_balance)} nano avaliable"
            )
        block = Block(
            block_type="state",
            account=self.public_address,
            representative=self.representative,
            previous=previous,
            balance=total_amount,
            link_as_account=address,
        )
        self._prepare_block(block)
        res = self._process_block(block, "send")
        return res
