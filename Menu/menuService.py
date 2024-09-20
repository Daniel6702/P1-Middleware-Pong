import socket
import psutil

def draw_text(text, font, color, surface, x, y):
    """Draws text at the specified position in the specified font and color."""
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


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
    """Gets the users ipv4 address"""
    possible_interface_names = ['wlan0', 'wlp3s0', 'Wi-Fi', 'wifi0', 'wlan1']

    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        if any(interface_name.lower().startswith(name.lower()) for name in possible_interface_names):
            for address in interface_addresses:
                if address.family == socket.AF_INET:
                    return address.address

    return None
