from dataclasses import dataclass, asdict
import json

@dataclass
class Message:
    id: str
    type: str
    data: dict

    def to_json(self):
        return json.dumps(asdict(self))

    @staticmethod
    def from_json(json_str: str):
        try:
            data = json.loads(json_str)
            return Message(
                id=data.get("id", ""),
                type=data.get("type", ""),
                data=data.get("data", {})
            )
        except json.JSONDecodeError:
            print("Failed to decode JSON to Message.")
            return None