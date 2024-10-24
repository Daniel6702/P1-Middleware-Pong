import json
from dataclasses import dataclass, field, asdict
import uuid
from datetime import datetime

@dataclass
class Message:
    id: str
    type: str
    data: dict
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4())) 
    send_timestamp: float = None   # Using float to store UNIX timestamp
    receive_timestamp: float = None

    def to_json(self):
        # Convert datetime fields to UNIX timestamp (seconds since the epoch)
        data_dict = asdict(self)
        if isinstance(self.send_timestamp, datetime):
            data_dict['send_timestamp'] = self.send_timestamp.timestamp()  # Convert to UNIX timestamp
        if isinstance(self.receive_timestamp, datetime):
            data_dict['receive_timestamp'] = self.receive_timestamp.timestamp()  # Convert to UNIX timestamp
        
        return json.dumps(data_dict)

    @staticmethod
    def from_json(json_str: str):
        try:
            data = json.loads(json_str)
            
            # Convert timestamps back to datetime objects if they exist
            send_timestamp = data.get('send_timestamp')
            if send_timestamp is not None:
                send_timestamp = datetime.fromtimestamp(send_timestamp)

            receive_timestamp = data.get('receive_timestamp')
            if receive_timestamp is not None:
                receive_timestamp = datetime.fromtimestamp(receive_timestamp)

            return Message(
                id=data.get("id", ""),
                type=data.get("type", ""),
                data=data.get("data", {}),
                msg_id=data.get("msg_id"),
                send_timestamp=send_timestamp,
                receive_timestamp=receive_timestamp
            )
        except json.JSONDecodeError:
            print("Failed to decode JSON to Message.")
            return None
