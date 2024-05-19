from flask import Flask, jsonify, request, render_template
from time import time
import hashlib
import json
from typing import List, Dict, Optional, Union


class Blockchain:
    def __init__(self):
        """
        Inicjalizuje blockchain z pustym łańcuchem i bieżącymi danymi.
        """
        self.chain: List[Dict[str, Union[int, float, str, List[Dict[str, Union[str, int]]]]]] = []
        self.current_data: List[Dict[str, Union[str, int]]] = []
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof: int, previous_hash: Optional[str] = None) -> Dict[
        str, Union[int, float, str, List[Dict[str, Union[str, int]]]]]:
        """
        Tworzy nowy blok i dodaje go do łańcucha.
            proof (int): Dowód z algorytmu Proof of Work.
            previous_hash (str, opcjonalnie): Hash poprzedniego bloku. Domyślnie None.
        Returns:
            dict: Nowy blok.
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'data': self.current_data,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_data = []
        self.chain.append(block)
        return block

    def new_entry(self, owner: str, stamp: str, year: int) -> int:
        """
        Dodaje nowy wpis do bieżących danych.
            owner (str): Właściciel znaczka.
            stamp (str): Nazwa znaczka.
            year (int): Rok wydania znaczka.
        Returns:
            int: Indeks bloku, który będzie zawierał tę transakcję.
        """
        self.current_data.append({
            'owner': owner,
            'stamp': stamp,
            'year': year,
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block: Dict[str, Union[int, float, str, List[Dict[str, Union[str, int]]]]]) -> str:
        """
        Tworzy SHA-256 hash z bloku.
            block (dict): Blok.
        Returns:
            str: Hash bloku.
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self) -> Dict[str, Union[int, float, str, List[Dict[str, Union[str, int]]]]]:
        """
        Zwraca ostatni blok w łańcuchu.
        Returns:
            dict: Ostatni blok.
        """
        return self.chain[-1]

    def proof_of_work(self, last_proof: int) -> int:
        """
        Prosty algorytm Proof of Work:
            last_proof (int): Poprzedni dowód.
        Returns:
            int: Nowy dowód.
        """
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        """
        Sprawdza, czy dowód jest poprawny: czy hash(last_proof, proof) zaczyna się od 4 zer.
            last_proof (int): Poprzedni dowód.
            proof (int): Bieżący dowód.
        Returns:
            bool: True, jeśli dowód jest poprawny, False w przeciwnym razie.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


# Inicjalizacja aplikacji
app = Flask(__name__)
blockchain = Blockchain()


@app.route('/')
def index() -> str:
    """
    Wyświetla stronę główną.
    Returns:
        str: strona główna.
    """
    return render_template('index.html')


@app.route('/mine', methods=['GET'])
def mine() -> (str, int):
    """
    Returns:
        tuple: Słownik zawierający wiadomość i szczegóły nowego bloku oraz kod statusu HTTP.
    """
    last_proof = blockchain.last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    block = blockchain.new_block(proof)
    response = {
        'message': "Nowy Blok",
        'index': block['index'],
        'transactions': block['data'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction() -> (str, int):
    """
    Tworzy nową transakcję i dodaje ją do bieżącego bloku.
    Returns:
        tuple: Słownik zawierający wiadomość o dodaniu transakcji do bloku oraz kod statusu HTTP.
    """
    values = request.get_json()
    required = ['owner', 'stamp', 'year']
    if not all(k in values for k in required):
        return 'Brakujące wartości', 400
    index = blockchain.new_entry(values['owner'], values['stamp'], values['year'])
    response = {'message': f'Transakcja zostanie dodana do Bloku {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain() -> (str, int):
    """
    Zwraca pełny łańcuch blockchain.
    Returns:
        tuple: Słownik zawierający pełny łańcuch blockchain oraz kod statusu HTTP.
    """
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
