import hashlib
import json
from uuid import uuid4
from blockchain1.chain import Blockchain

from flask import Flask,request,jsonify
#
app = Flask(__name__)
#虚拟一个地址
node_identifier = str(uuid4()).replace('-','')
#初始化一个链
blockchain =Blockchain()
#mine:挖矿
"""
1.计算工作量证明PoW

"""
@app.route('/mine',methods=['GET'])
def mine():
    # "we will mine a new Block"
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    #给工作量证明的节点提供奖励
    #发送者为“0”表明是新挖出的币
    blockchain.new_transaction(
        sender="0",
        #用的上面虚拟的地址
        recipient=node_identifier,
        amount=1
    )
    #将新块添加到链上
    block = blockchain.new_block(proof)
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200



#transaction 交易
"""
交易信息：
{
 "sender": "my address",
 "recipient": "someone else's address",
 "amount": 5
}
"""
@app.route('/transactions/new',methods=['POST'])
def new_transaction():
    #we will add a new transaction
    values = request.get_json()
    #检查是否所有的属性都有
    required = ['sender','recipient','amount']
    if not all(k in values for k in required):
        return 'Missing values',400
    #建立一个新的交易
    index = blockchain.new_transaction(values['sender'],values['recipient'],values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain',methods=['GET'])
def full_chain():
    response = {
        'chain' : blockchain.chain,
        'length': len(blockchain.chain)
    }
    #直接返回一个元组
    return jsonify(response), 200
@app.route('/nodes/register',methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes",400
    for node in nodes:
        blockchain.register_node(node)
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve',methods=['GET'])
def consensus():
    #一致性
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)



















