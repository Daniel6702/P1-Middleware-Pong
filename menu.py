import pygame
import socket
import random
import psutil
import socket

def get_wifi_ip():
    possible_interface_names = ['wlan0', 'wlp3s0', 'Wi-Fi', 'wifi0', 'wlan1']

    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        if any(interface_name.lower().startswith(name.lower()) for name in possible_interface_names):
            for address in interface_addresses:
                if address.family == socket.AF_INET:
                    return address.address

    return None

def run_client_menu():
    # Initialize pygame
    pygame.init()

    # Define screen dimensions
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Client Menu")

    # Define colors
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Fonts
    font = pygame.font.Font(None, 36)

    # Get the client's IP address
    client_ip = get_wifi_ip()
    client_port = random.randint(5000, 6000)
    local_client = f"{client_ip}:{client_port}"

    # Text input for adding other clients
    input_box = pygame.Rect(100, 150, 300, 32)
    input_text = ''
    clients = []

    # Buttons
    start_button = pygame.Rect(100, 500, 200, 50)
    add_button = pygame.Rect(450, 150, 100, 32)

    def draw_text(text, font, color, surface, x, y):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        text_rect.topleft = (x, y)
        surface.blit(text_obj, text_rect)

    def validate_ip_port(input_str):
        try:
            ip, port = input_str.split(':')
            socket.inet_aton(ip)  # Validates IP format
            port = int(port)
            if 5000 <= port <= 6000:  # Validates port range
                return True
        except Exception:
            return False
        return False

    running = True
    while running:
        screen.fill(black)

        draw_text(f"Your IP: {client_ip}", font, white, screen, 100, 50)
        draw_text(f"Your Port: {client_port}", font, white, screen, 100, 100)

        # Draw the input box
        pygame.draw.rect(screen, white, input_box, 2)

        # Draw the buttons
        pygame.draw.rect(screen, white, start_button)
        pygame.draw.rect(screen, white, add_button)
        draw_text("Start", font, black, screen, start_button.x + 10, start_button.y + 10)
        draw_text("Add", font, black, screen, add_button.x + 10, add_button.y + 5)

        # Render the input text
        txt_surface = font.render(input_text, True, white)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        input_box.w = max(300, txt_surface.get_width() + 10)

        # Display added clients
        y_offset = 200
        for client in clients:
            draw_text(f"Client: {client}", font, white, screen, 100, y_offset)
            y_offset += 40

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box, toggle the active variable.
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False

                # If the user clicked on the add_button, validate and add the input to clients
                if add_button.collidepoint(event.pos) and input_text:
                    if validate_ip_port(input_text):
                        clients.append(input_text)
                        input_text = ''
                    else:
                        print("Invalid IP or Port. Use format IP:Port with port in range 5000-6000.")

                # If the user clicked on the start_button, close the window
                if start_button.collidepoint(event.pos):
                    running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_text:
                        if validate_ip_port(input_text):
                            clients.append(input_text)
                            input_text = ''
                        else:
                            print("Invalid IP or Port. Use format IP:Port with port in range 5000-6000.")
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        pygame.display.flip()

    pygame.quit()
    return local_client, clients

# Example usage:
if __name__ == "__main__":
    local_client, clients = run_client_menu()
    print("Clients added:", clients)
