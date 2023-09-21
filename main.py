import json
from flask import Flask, jsonify
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def save(self, data):
        pass

    @abstractmethod
    def load(self):
        pass

class FileStorage(Storage):
    def __init__(self, filename="config.json"):
        self.filename = filename

    def save(self, data):
        with open(self.filename, 'w') as file:
            json.dump(data, file)

    def load(self):
        try:
            with open(self.filename, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            with open(self.filename, 'w') as file:
                json.dump([], file)
            return []

class Endpoint:
    def __init__(self, path, method, response_data):
        self.path = path
        self.method = method
        self.response_data = response_data

    def handle_request(self):
        return jsonify(self.response_data)

    def to_dict(self):
        return {
            "path": self.path,
            "method": self.method,
            "response_data": self.response_data
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["path"], data["method"], data["response_data"])

class EndpointManager:
    def __init__(self, storage):
        self.app = Flask(__name__)
        self.endpoints = []
        self.storage = storage
        self.load_endpoints()

    def load_endpoints(self):
        data = self.storage.load()
        self.endpoints = [Endpoint.from_dict(item) for item in data]

    def save_endpoints(self):
        data = [endpoint.to_dict() for endpoint in self.endpoints]
        self.storage.save(data)

    def add_endpoint(self, endpoint):
        view_func = endpoint.handle_request
        self.app.add_url_rule(endpoint.path, endpoint.path, view_func, methods=[endpoint.method])
        self.endpoints.append(endpoint)

    def list_endpoints(self):
        for idx, endpoint in enumerate(self.endpoints, 1):
            print(f"{idx}. {endpoint.path} ({endpoint.method})")

    def delete_endpoint_by_index(self, index):
        if index > 0 and index <= len(self.endpoints):
            deleted_endpoint = self.endpoints.pop(index - 1)
            print(f"Endpoint {deleted_endpoint.path} ({deleted_endpoint.method}) foi excluído.")
        else:
            print("Índice inválido.")

    def run(self):
        self.app.run(debug=False)

class CLI:
    def __init__(self, manager):
        self.manager = manager

    def start(self):
        action = input("Você deseja criar, listar ou deletar um endpoint? (criar/listar/deletar): ").lower()

        if action == "criar":
            self.create_endpoint()
        elif action == "listar":
            self.manager.list_endpoints()
        elif action == "deletar":
            self.delete_endpoint()

        self.manager.save_endpoints()
        self.manager.run()

    def create_endpoint(self):
        num_endpoints = int(input("Quantos endpoints você deseja criar? "))
        for _ in range(num_endpoints):
            path = input("Digite o nome do endpoint (ex: /hello): ")
            method = input("Digite o tipo do endpoint (GET ou POST): ").upper()
            message = input("Digite a mensagem de saída (ex: {\"id\": \"1\"}): ")
            response_data = json.loads(message)

            endpoint = Endpoint(path, method, response_data)
            self.manager.add_endpoint(endpoint)

    def delete_endpoint(self):
        self.manager.list_endpoints()
        endpoint_idx = int(input("Digite o número do endpoint que você deseja deletar: "))
        self.manager.delete_endpoint_by_index(endpoint_idx)

if __name__ == '__main__':
    storage = FileStorage()
    manager = EndpointManager(storage)
    cli = CLI(manager)
    cli.start()
