# easy_nano

Send and receive nano (without having to understand the nano protocol). Built on top of [nanolib](https://github.com/Matoking/nanolib).

## Installation

```
pip install easy_nano
```

## Usage

### Python

```python
from easy_nano import Account

acc = Account()

# get new account nano address
print(acc.public_address)

# processes any pending transactions
acc.recieve()

# sends nano to address
acc.send("nano_1zfnwwk5xq74tddsq9t13oemxfkyqhz6f6jzej3wfqe4q3y39381qtq98dmo", 0.01)
```

### CLI

```bash
# processes any pending blocks
easy_nano receive

# sends nano to address (input via stdin)
easy_nano send
```
