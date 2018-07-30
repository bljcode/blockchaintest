from time import time
import json
import hashlib
from urllib.parse import urlparse
import requests

#存储区块链
class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        #避免重复添加节点
        self.nodes = set()

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

    def register_node(self,address):
        """
        添加一个网络节点 add a new node to the list of nodes
        :param address:<str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return:
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    #冲突是指不同的节点拥有不同的链，为了解决这个问题，规定最长的、有效的链才是最终的链，
    # 网络中有效最长链才是实际的链。
    def valid_chain(self,chain):
        """
        Determine if a given blockchain is valid
        主要是检查两个，一个检测hash值，一个检测工作量
        :param chain:<list> A blockchain
        :return:<bool> True if valid, False if not
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        共识算法解决冲突
        使用网络中最长的链.
        :return: <bool> True 如果链被取代, 否则为False
        """
        neighbours = self.nodes
        new_chain = None

        #We are only looking for chains longer than ours
        max_length = len(self.chain)

        #Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

                    # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False


