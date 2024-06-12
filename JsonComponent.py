import json

class JsonComponent:
    def __init__(self, name, properties=None, children=None):
        self.name = name
        self.properties = properties if properties else {}
        self.children = children if children else []

    def add_child(self, child):
        self.children.append(child)

    def to_dict(self):
        return {
            "name": self.name,
            "properties": self.properties,
            "children": [child.to_dict() for child in self.children]
        }
    
    @classmethod
    def from_dict(component, data):
        children = [component.from_dict(child) for child in data.get("children", [])]
        return component(name=data["name"], properties=data.get("properties", {}), children=children)

    def find(self, key, value):
        found = []
        if self.properties.get(key) == value:
            found.append(self)
        for child in self.children:
            found.extend(child.find(key, value))
        return found
    
    @classmethod
    def save(config, file_path):
        with open(file_path, 'w') as f:
            json.dump(config.to_dict(), f, indent=4)

    @classmethod
    def load(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        return JsonComponent.from_dict(data)