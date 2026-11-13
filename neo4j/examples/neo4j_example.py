# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "neo4j>=6.1,<6.2",
#     "neomodel>=7,<8",
# ]
# ///

import os

from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


class HelloWorldExample:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def print_greeting(self, message):
        with self.driver.session() as session:
            greeting = session.execute_write(self._create_and_return_greeting, message)
            print(greeting)

    @staticmethod
    def _create_and_return_greeting(tx, message):
        result = tx.run(
            "CREATE (a:Greeting) "
            "SET a.message = $message "
            "RETURN a.message + ', from node ' + elementId(a)",
            message=message,
        )
        return result.single()[0]


if __name__ == "__main__":
    greeter = HelloWorldExample(URI, USER, PASSWORD)
    greeter.print_greeting("hello, world")
    greeter.close()
