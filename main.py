import warnings
from typing import Optional, Dict

import requests
from nanolib import (
    generate_seed,
    generate_account_id,
    generate_account_private_key,
    Block,
    accounts,
)

# from https://github.com/ealtamir/nano-simple-tutorial
def process_block(
    block: Block,
    node_hostname: str,
    subtype: str,
) -> any:
    if not validate_work(block, block["work"]):
        raise Exception("Work used in block is invalid.")
    if not validate_block_signature(block, block["signature"], block["account"]):
        raise Exception("Signature used in block is invalid.")
    data = {"subtype": subtype, "action": "process", "block": block, "json_block": True}
    print("Sending data to node:")
    pprint.PrettyPrinter(indent=2).pprint(data)
    r = requests.post(node_hostname, json=data)
    return r.json()


class Account:
    def __init__(
        self,
        seed: Optional[str] = None,
        idx: Optional[int] = 0,
        node_url: Optional[str] = "https://mynano.ninja/api/node",
        representative: Optional[
            str
        ] = "nano_1wenanoqm7xbypou7x3nue1isaeddamjdnc3z99tekjbfezdbq8fmb659o7t",
    ):
        self.seed = generate_seed() if seed is None else seed
        self.public_address = generate_account_id(
            self.seed, idx, prefix=accounts.AccountIDPrefix.NANO
        )
        self.private_key = generate_account_private_key(self.seed, idx)
        self.node_url = node_url
        self.representative = representative

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

    def recieve(self, count: Optional[int] = 5):
        data = self._call_node_url(
            {"action": "pending", "account": self.public_address, "count": count}
        )
        ret_data = {}
        for block_hash in data["blocks"]:
            try:
                block_info = self._get_block_info(block_hash)
                block_addr = block_info["block_account"]
                amount = float(block_info["amount"])
                block_hash = self._recieve_block(block_hash, amount)
                ret_data[block_addr] = {"amount": amount, "hash": block_hash}
            except Exception as e:
                warnings.warn(e)
                ret_data[block_addr] = None  # probably a better way to do this
        return ret_data

    def _process_block(self, block: Block):
        block_dict = block.to_dict()
        res = process_block(block_dict, self.node_url, "open")
        if "hash" not in res:
            raise Exception(f"Transaction not accepted: {res}")
        return res["hash"]

    def _prepare_block(self, block: Block):
        block.solve_work()
        if not block.has_valid_work:
            raise Exception("Block does not have valid PoW")

        block.sign(private_key)
        if not block.has_valid_signature:
            raise Exception("Block does not have valid signature")

        if not block.complete:
            raise Exception("Block not ready to be broadcast")

    def _recieve_block(self, previous: str, amount: float):
        block = Block(
            block_type="state",
            account=self.public_address,
            representative=self.representative,
            previous="0" * 64,
            balance=(10 ** 30) * amount,
            link=previous,
        )
        self._prepare_block(block)
        return self._process_block(block)

    def _get_previous_block_hash(self):
        data = self._call_node_url(
            {"action": "account_history", "account": self.public_address, "count": 1}
        )
        for obj in data["history"]:


    def send(self, address: str, amount: float):
        block = Block(
            block_type="state",
            account=self.public_address,
            representative=self.representative,
            previous="0" * 64,
            balance=(10 ** 30) * amount,
            link=address,
        )
        res = self._prepare_block(block)
        if "error" in res:
            raise Exception(res["error"])
        return res['hash']
