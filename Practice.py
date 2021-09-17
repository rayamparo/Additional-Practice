from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class TransactionType(Enum):
    Debit = "Debit"
    Credit = "Credit"

@dataclass
class Transaction:
  amount: int
  timestamp: datetime = field(default_factory=datetime.now)
  
  @property
  def type(self) -> TransactionType:
    if self.amount >= 0:
      return TransactionType.Credit
    else:
      return TransactionType.Debit

  def __str__(self):
    return f"{self.type}:\t{abs(self.amount)}"
  
class BankAccountOverdrawn(Exception):
  """Do Something with This Maybe?"""
  pass

@dataclass
class TransactionSummary:
  num_transactions: int
  net_change: int
  first_transaction_time: datetime
  last_transaction_time: datetime

@dataclass
class BankAccount:
  transactions: list[Transaction] = field(default_factory=list)
  balance: int = 0

  ttd = TransactionType.Debit
  ttc = TransactionType.Credit

  @property
  def id(self) -> int:
    return id(self)

  def __str__(self):
    return (
      f"BankAccount[{self.id}]\n\t"
      f"balance:\t{self.balance}\n\t"
      f"transactions:\t{len(self.transactions)}\n\n"
    )
  
  def transact(self, transaction: Transaction):
    """Takes a transaction and applies it to the account."""
    self.transactions.append(transaction)
    self.balance += transaction.amount

  def credit(self, amount: int) -> Transaction:
    """Takes an amount and adds a new transaction, 
    then returns the Transaction."""
    self.transactions.append(Transaction(amount))
    self.balance += amount
    return self.transactions[-1]

  def debit(self, amount: int) -> Transaction:
    """Takes an amount and adds a new transaction, 
    then returns the Transaction."""
    self.transactions.append(Transaction(-amount))
    self.balance -= amount
    return self.transactions[-1]

  def recent_summary(self, num_transactions: int) -> TransactionSummary:
    """Returns a summary of last [num_transactions] transactions."""
    if num_transactions > len(self.transactions):
      return "Amount of requested transactions exceed amount of transactions in account"
    i = 1
    first_transaction_time = None
    last_transaction_time = None
    period_net_change = 0
    while i <= num_transactions:
      if i == 1:
        first_transaction_time = self.transactions[-i].timestamp
      if i == num_transactions:
        last_transaction_time = self.transactions[-i].timestamp
      period_net_change += self.transactions[-i].amount
      i += 1
    print(period_net_change)
    return TransactionSummary(num_transactions, period_net_change, first_transaction_time.strftime('%m/%d/%Y'), last_transaction_time.strftime('%m/%d/%Y'))

  def time_summary(self, start_date: datetime, end_date: datetime = None) -> TransactionSummary:
    """Takes a start_date and optionally and end_date and 
    returns a summary of all transactions between those dates."""
    transactions_between = 0
    transaction_timestamps = []
    period_net_change = 0
    if end_date == None:
      end_date = datetime.now()
    for transaction in self.transactions:
      if transaction.timestamp >= start_date and transaction.timestamp <= end_date:
        transactions_between += 1
        transaction_timestamps.append(transaction.timestamp)
        period_net_change += transaction.amount
    return TransactionSummary(transactions_between, period_net_change, min(transaction_timestamps), max(transaction_timestamps))

def test():
  start_time = datetime.now()
  t1 = Transaction(-200)
  t2 = Transaction(100)
  ba = BankAccount()
  account_creation = datetime.now()
  transactions: list[Transaction] = [
    ba.credit(100),
    ba.credit(500),
    ba.debit(200),
    ba.credit(1),
    ba.debit(300),
  ]
  
  tests = [
    ba.recent_summary(1).net_change == -300,
    ba.recent_summary(5).net_change == 101,
    ba.balance == 101,
    ba.time_summary(account_creation).num_transactions == 5,
    ba.time_summary(start_time, transactions[2].timestamp).net_change == 400,
  ]

  try:
    ba.transact(t1)
    tests.append(ba.recent_summary(1).net_change == -300)
    tests.append(ba.balance == -99)
  except BankAccountOverdrawn:
    print(f"Nice, you dont need to handle this though. This is just extra credit.")

  ba.transact(t2)
  tests.append(ba.balance == 201)
  tests.append(ba.recent_summary(ba.time_summary(start_time).num_transactions).net_change == 201)
  # Shouldn't this be 7 due to the two previous transactions added onto the transactions list?
  tests.append(ba.time_summary(start_time).num_transactions == 6)

  for i,r in enumerate(tests):
    result = "Pass" if r else "Fail"
    print(f"Test {i+1}: {result}")


if __name__ == "__main__":
  test()