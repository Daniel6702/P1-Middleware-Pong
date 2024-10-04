import pygame
import sys
from Middleware.peer import Peer
from properties import FPS

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BACKGROUND_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
FONT_SIZE = 20
PEER_LIST_START_Y = 200
PEER_LIST_PADDING = 30

def menu() -> Peer:
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Peer-to-Peer Network")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, FONT_SIZE)

    # Initialize Peer
    peer = Peer()

    # Function to handle incoming data messages (optional for GUI)
    def handle_message(message):
        print(f"Received message: {message}")

    # Update the Peer instance to use the new message handler
    peer.on_message_received = handle_message

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen
        screen.fill(BACKGROUND_COLOR)

        # Display local peer information
        local_info = f"Local Peer ID: {peer.id},         IP: {peer.ip},          Port: {peer.bind_port}"
        local_id_surface = font.render(local_info, True, TEXT_COLOR)
        screen.blit(local_id_surface, (50, 50))

        # Display peers list title
        peers_title = "Connected Peers:"
        peers_title_surface = font.render(peers_title, True, TEXT_COLOR)
        screen.blit(peers_title_surface, (50, PEER_LIST_START_Y - 30))

        # Fetch the current list of peers
        peers = peer.get_peers()

        # Display each peer's information
        for index, peer_i in enumerate(peers):
            peer_id, peer_ip, peer_port = "N/A", "N/A", "N/A"
            if len(peer_i) == 2:
                peer_id = peer_i[1]
                peer_ip, peer_port = peer_i[0].split(":")

            peer_info = f"Peer {index + 1}: ID: {peer_id}, IP: {peer_ip}, Port: {peer_port}"
            peer_surface = font.render(peer_info, True, TEXT_COLOR)
            screen.blit(peer_surface, (50, PEER_LIST_START_Y + index * PEER_LIST_PADDING))

        # Create ready button
        ready_surface = font.render("Ready", True, TEXT_COLOR)
        screen.blit(ready_surface, (50, WINDOW_HEIGHT - 50))

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    # Graceful shutdown
    peer.discovery_service.stop_discovery()
    pygame.quit()

    return peer