from typing import Dict, Any, List
from abc import ABC, abstractmethod


class AgentRegistry:
    _agents = {}
    
    @classmethod
    def register(cls, agent):
        for capability in agent.get_capabilities():
            if capability not in cls._agents:
                cls._agents[capability] = []
            cls._agents[capability].append(agent)
    
    @classmethod
    def discover(cls, capability: str):
        return cls._agents.get(capability, [])
    
    @classmethod
    def list_all(cls):
        all_agents = set()
        for agents in cls._agents.values():
            all_agents.update(agents)
        return list(all_agents)


class Message:
    def __init__(self, msg_type: str, capability: str, data: Dict[str, Any]):
        self.msg_type = msg_type
        self.capability = capability
        self.data = data
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.msg_type,
            'capability': self.capability,
            'payload': self.data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        return cls(
            msg_type=data['type'],
            capability=data['capability'],
            data=data['payload']
        )


class Agent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.version = "1.0.0"
        self.description = ""
        AgentRegistry.register(self)
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_capability_schemas(self) -> Dict[str, Dict[str, Any]]:
        pass
    
    def get_agent_card(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": self.get_capabilities(),
            "schemas": self.get_capability_schemas()
        }
    
    @abstractmethod
    def handle_request(self, message: Message) -> Message:
        pass
    
    def send_request(self, capability: str, data: Dict[str, Any]) -> Message:
        request = Message('request', capability, data)
        return self.handle_request(request)
