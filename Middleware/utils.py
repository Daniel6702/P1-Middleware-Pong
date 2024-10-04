import socket
import os
import uuid

def validate_ip_port(input_str):
    """Checks if the ip port is within the specified range."""
    try:
        ip, port = input_str.split(':')
        socket.inet_aton(ip)  # Validates IP format
        port = int(port)
        if 5000 <= port <= 6000:  # Validates port range
            return True
    except Exception:
        return False
    return False

def get_ipv4():
    """Finds the ip address connected to the internet."""
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_socket.settimeout(2)
        test_socket.connect(("8.8.8.8", 80)) 
        ip = test_socket.getsockname()[0]
        test_socket.close()
        return ip
    except Exception as e:
        return None

def get_broadcast_address():
    local_ip = get_ipv4()
    subnet = '.'.join(local_ip.split('.')[:3]) + '.255'
    return subnet

def uuid_to_number(input_val):
    """
    Convert a UUID string, UUID object, or integer to an integer.
    
    Args:
    input_val: The input value to convert. It can be a UUID string, UUID object, or an integer.
    
    Returns:
    int: The integer representation of the UUID, or the input itself if it's already an integer.
    """
    if isinstance(input_val, int):
        # If the input is already an integer, return it as is
        return input_val
    elif isinstance(input_val, uuid.UUID):
        # If the input is a UUID object, convert it to an integer
        return int(input_val)
    elif isinstance(input_val, str):
        try:
            # Convert the string to a UUID object, then to an integer
            uuid_obj = uuid.UUID(input_val)
            return int(uuid_obj)
        except ValueError as e:
            print(f"Invalid UUID string: {input_val}. Error: {e}")
            return None
    else:
        print(f"Unsupported input type: {type(input_val)}. Expected int, uuid.UUID, or str.")
        return None