import json
import os
import time
from engine import CryptoEngine

LEDGER_FILE = "global_ledger.json"


class Ledger:
    def __init__(self):
        if not os.path.exists(LEDGER_FILE):
            with open(LEDGER_FILE, "w") as f:
                json.dump([], f)

    def get_all_transactions(self):
        with open(LEDGER_FILE, "r") as f:
            return json.load(f)

    def get_balance(self, address):
        balance = 100.0  # Kezdő egyenleg minden gyakorló fióknak
        transactions = self.get_all_transactions()
        for tx in transactions:
            if tx['sender'] == address:
                balance -= tx['amount']
            if tx['receiver'] == address:
                balance += tx['amount']
        return balance

    def add_transaction(self, sender_pub, receiver_pub, amount, signature):
        # Hitelesítés
        msg = f"{sender_pub}-{receiver_pub}-{amount}"
        if not CryptoEngine.verify_signature(sender_pub, msg, signature):
            return False, "Érvénytelen digitális aláírás!"

        if self.get_balance(sender_pub) < amount:
            return False, "Nincs elég egyenleg!"

        tx = {
            "sender": sender_pub,
            "receiver": receiver_pub,
            "amount": amount,
            "signature": signature,
            "timestamp": time.time()
        }

        all_tx = self.get_all_transactions()
        all_tx.append(tx)

        with open(LEDGER_FILE, "w") as f:
            json.dump(all_tx, f, indent=4)

        return True, "Sikeres utalás!"