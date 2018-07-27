from time import time
import json
import hashlib
#存储区块链
class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        #创建一个最原始的起始block
        self.new_block(previous_hash=1,proof=100)


    def new_block(self, proof, previous_hash=None):
        """
        创建一个新的Block and add to chain
        :param proof:工作量证明
        :param previous_hash:上一个block的Hash
        :return:New Block
        """
        block={
            'index':len(self.chain) + 1,
            'timestamp':time(),
            'transactions':self.current_transactions,
            'proof':proof,
            'previous_hash':previous_hash or self.hash(self.chain[-1]),
        }
        #清空当前交易信息
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
       """
        生成新的交易，信息加入到下一个待挖的区块中
       :param sender: Address of the Sender
       :param recipient: Address of the Recipient
       :param amount:
       :return:The index of the Block that will hold this transaction
       """
       self.current_transactions.append({
           'sender':sender,
           'recipient':recipient,
           'amount':amount,
       })
       return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        #Hashes a Block
        block_string = json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        #返回 chain中最后一个block
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        建档的工作量证明：
            - 查找一个p' 使得 hash(pp')以4个0开头
            -p 是上一个块的证明，p'是当前的证明
        :param last_proof:
        :return:
        """
        proof = 0
        while self.valid_proof(last_proof,proof) is False:
            proof +=1
        return proof


    @staticmethod
    def valid_proof(last_proof,proof):
        """
        验证证明：是否hash(last_proof, proof)以4个0开头
        :param last_proof:
        :param proof:
        :return:
        """
        #f'是Python3.6字符串格式化用法
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"






