import sys

sys.path.append("./easy_nano")

import pytest

from lib import Account


def _process_block(self, block, subtype):
    return "test_hash"


def _call_node_url(self, payload):
    if payload["action"] == "account_history":
        return {
            "account": "nano_3cpz7oh9qr5b7obbcb5867omqf8esix4sdd5w6mh8kkknamjgbnwrimxsaaf",
            "history": [
                {
                    "type": "send",
                    "account": "nano_1dz83htcqdwdzdhc6bwhdggxf8g7qjkxykq8h6pqt1g3mwnmkqhcb4km8irr",
                    "amount": "950000000000000000000000000000",
                    "local_timestamp": "1622707606",
                    "height": "43470",
                    "hash": "CF2318AD0780FAD5A64438BA64D442F14457F8F99882E9F93D3F266B47BF561E",
                },
                {
                    "type": "receive",
                    "account": "nano_3o1x6z5yjaebbme8dya8m54ochtfcsoispj7hts6b1ggnwtst4dspckwqt6n",
                    "amount": "74742451100000000000000000000000",
                    "local_timestamp": "1622707068",
                    "height": "43469",
                    "hash": "B579B841C6E1916CB8B84347894F5221E274C25073FC956B9BD3C90E070699FF",
                },
            ],
        }
    elif payload["action"] == "account_info":
        return {
            "frontier": "023B94B7D27B311666C8636954FE17F1FD2EAA97A8BAC27DE5084FBBD5C6B02C",
            "open_block": "991CF190094C00F0B68E2E5F75F6BEE95A2E0BD93CEAA4A6734DB9F19B728948",
            "representative_block": "023B94B7D27B311666C8636954FE17F1FD2EAA97A8BAC27DE5084FBBD5C6B02C",
            "balance": "325586539664609129644855132177",
            "modified_timestamp": "1598514077",
            "block_count": "44",
            "account_version": "2",
            "confirmation_height": "44",
            "confirmation_height_frontier": "023B94B7D27B311666C8636954FE17F1FD2EAA97A8BAC27DE5084FBBD5C6B02C",
        }
    elif payload["action"] == "block_info":
        return {
            "block_account": "nano_1ipx847tk8o46pwxt5qjdbncjqcbwcc1rrmqnkztrfjy5k7z4imsrata9est",
            "amount": "30000000000000000000000000000000000",
            "balance": "5606157000000000000000000000000000000",
            "height": "58",
            "local_timestamp": "0",
            "confirmed": "true",
            "contents": {
                "type": "state",
                "account": "nano_1ipx847tk8o46pwxt5qjdbncjqcbwcc1rrmqnkztrfjy5k7z4imsrata9est",
                "previous": "CE898C131AAEE25E05362F247760F8A3ACF34A9796A5AE0D9204E86B0637965E",
                "representative": "nano_1stofnrxuz3cai7ze75o174bpm7scwj9jn3nxsn8ntzg784jf1gzn1jjdkou",
                "balance": "5606157000000000000000000000000000000",
                "link": "5D1AA8A45F8736519D707FCB375976A7F9AF795091021D7E9C7548D6F45DD8D5",
                "link_as_account": "nano_1qato4k7z3spc8gq1zyd8xeqfbzsoxwo36a45ozbrxcatut7up8ohyardu1z",
                "signature": "82D41BC16F313E4B2243D14DFFA2FB04679C540C2095FEE7EAE0F2F26880AD56DD48D87A7CC5DD760C5B2D76EE2C205506AA557BF00B60D8DEE312EC7343A501",
                "work": "8a142e07a10996d5",
            },
            "subtype": "send",
        }
    elif payload["action"] == "pending":
        return {
            "blocks": [
                "0EF695810BEC8B4AE3DC217DA495885A42956456A4B168C0B788ADB17A5ED7F4",
                "142A538F36833D1CC78B94E11C766F75818F8B940771335C6C1B8AB880C5BB1D",
                "1AAE335A94C5DA1E4E1D0B45C3B100CCA241CC5BC557E24BB367C779D55E3A0C",
                "1F04048431842B8875CD0040B9F2B2AAC2E8B88A0256D11E7AE6769F4DF2B61A",
                "20D5D6EA5CA355B11A0E3C11A74FBB4E91D126F4B3FD97232945D451A621E6F7",
            ]
        }
    return {}


def _prepare_block(self, block):
    return


def test_send(mocker):
    mocker.patch("lib.Account._process_block", _process_block)
    mocker.patch("lib.Account._call_node_url", _call_node_url)
    mocker.patch("lib.Account._prepare_block", _prepare_block)

    account = Account()
    hash = account.send(
        "nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3", 0.01
    )
    assert hash == "test_hash"


def test_receive(mocker):
    mocker.patch("lib.Account._process_block", _process_block)
    mocker.patch("lib.Account._call_node_url", _call_node_url)
    mocker.patch("lib.Account._prepare_block", _prepare_block)

    account = Account()
    data = account.receive()
    assert data == {
        "nano_1ipx847tk8o46pwxt5qjdbncjqcbwcc1rrmqnkztrfjy5k7z4imsrata9est": {
            "amount": 30000.0,
            "hash": "20D5D6EA5CA355B11A0E3C11A74FBB4E91D126F4B3FD97232945D451A621E6F7",
        }
    }
