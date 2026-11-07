"""Load test for the Node Registry API.

This Locust test sends synthetic load to the /health and /api/nodes endpoints
to evaluate auto-scaling under the Horizontal Pod Autoscaler (HPA).
"""

import uuid
from locust import HttpUser, between, task


class NodeRegistryUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        # Register a unique node for this user so lookup requests target an existing record
        self.node_name = f"node-{uuid.uuid4().hex[:8]}"
        self.client.post(
            "/api/nodes",
            json={"name": self.node_name, "host": "10.0.0.1", "port": 8000},
            name="/api/nodes [POST]",
        )

    @task(5)
    def health_check(self):
        self.client.get("/health", name="/health")

    @task(3)
    def list_nodes(self):
        self.client.get("/api/nodes", name="/api/nodes [GET]")

    @task(2)
    def get_node(self):
        self.client.get(f"/api/nodes/{self.node_name}", name="/api/nodes/{name}")

    @task(1)
    def register_node(self):
        new_name = f"node-{uuid.uuid4().hex[:8]}"
        self.client.post(
            "/api/nodes",
            json={"name": new_name, "host": "10.0.0.2", "port": 8080},
            name="/api/nodes [POST]",
        )
