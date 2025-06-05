import zmq
import json
import time  # <-- Required for timestamp
from threading import Thread


class VisionBridge:
    def __init__(self):
        # MCP Setup (PUB pattern)
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind("tcp://*:5570")  # Dedicated vision channel
        print("[MCP DEBUG] VisionBridge publisher bound to tcp://*:5570")

    def publish_result(self, agent_type: str, data: dict):
        """Standardized MCP message format"""
        message = {
            "source": "vision",
            "agent": agent_type,
            "data": data,
            "timestamp": time.time()
        }
        print(f"[MCP DEBUG] Publishing message from '{agent_type}': {json.dumps(message, indent=2)}")
        self.publisher.send_json(message)


# Singleton bridge instance
vision_bridge = VisionBridge()
