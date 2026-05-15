from dataclasses import dataclass


@dataclass
class ToolRegistryEntry:
    node_name: str
    display_name: str
    parallel: bool


ToolRegistry = dict[str, ToolRegistryEntry]
