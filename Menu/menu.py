import pygame
import random
from game_properties import *
from .menuService import *

class Menu:
    def __init__(self):
        # Initialize
        pygame.init()

        # Set up the screen
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Client menu')

        # Fonts
        self.font = pygame.font.Font(None, 36)

        # Get the client's IP address
        self.client_ip = get_ipv4()
        self.client_port = random.randint(5000, 6000)
        self.local_client = f"{self.client_ip}:{self.client_port}"

        # Text input for adding other clients
        self.input_box = pygame.Rect(100, 150, 300, 32)
        self.input_text = ''
        self.clients = []

        # Buttons
        self.start_button = pygame.Rect(100, 500, 200, 50)
        self.add_button = pygame.Rect(450, 150, 100, 32)

        self.running = True

    def _draw(self):
        self.screen.fill(BLACK)
        draw_text(f"Your IP: {self.client_ip}:{self.client_port}", self.font, WHITE, self.screen, 100, 50)

        # Draw the input box
        pygame.draw.rect(self.screen, WHITE, self.input_box, 2)

        # Draw the buttons
        pygame.draw.rect(self.screen, WHITE, self.start_button)
        pygame.draw.rect(self.screen, WHITE, self.add_button)
        draw_text("Start", self.font, BLACK, self.screen, self.start_button.x + 10, self.start_button.y + 10)
        draw_text("Add", self.font, BLACK, self.screen, self.add_button.x + 10, self.add_button.y + 5)

        # Render the input text
        txt_surface = self.font.render(self.input_text, True, WHITE)
        self.screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))
        self.input_box.w = max(300, txt_surface.get_width() + 10)

        # Display added clients
        y_offset = 200
        for client in self.clients:
            draw_text(f"Client: {client}", self.font, WHITE, self.screen, 100, y_offset)
            y_offset += 40

    def handle_mouseDown(self, event):
        # If the user clicked on the input_box, toggle the active variable.
        if self.input_box.collidepoint(event.pos):
            self.active = True
        else:
            self.active = False

        # If the user clicked on the add_button, validate and add the input to clients
        if self.add_button.collidepoint(event.pos) and self.input_text:
            if validate_ip_port(self.input_text):
                self.clients.append(self.input_text)
                self.input_text = ''
            else:
                print("Invalid IP or Port. Use format IP:Port with port in range 5000-6000.")

        # If the user clicked on the start_button, close the window
        if self.start_button.collidepoint(event.pos):
            self.running = False

    def handle_keyDown(self, event):
        if event.key == pygame.K_RETURN:
            if self.input_text:
                if validate_ip_port(self.input_text):
                    self.clients.append(self.input_text)
                    self.input_text = ''
                else:
                    print("Invalid IP or Port. Use format IP:Port with port in range 5000-6000.")
        elif event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
        else:
            self.input_text += event.unicode

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouseDown(event)
            if event.type == pygame.KEYDOWN:
                self.handle_keyDown(event)

    def run(self):
        """Runs the menu (Returns local client ip and port, as well as connected clients"""
        while self.running:
            self.handle_events()
            self._draw()
            pygame.display.flip()

        pygame.quit()
        return self.local_client, self.clients