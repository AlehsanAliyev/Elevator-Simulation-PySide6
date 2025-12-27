import pygame


# some_parameters
screen_width = 800
screen_height = 600

# Define some colors
BLACK = (0, 0, 0)
SKY = (13, 237, 247)
FIRUZAYI = (46, 241, 214)
DARK_GREEN = (26, 95, 85)
STONE = (247, 173, 13)
RED = (255, 0, 0)
BLUE = (0, 255, 0)
WHITE = (255, 255, 255)


class Elevator(pygame.sprite.Sprite):

    def __init__(self, floor_height):
        super(Elevator, self).__init__()

        self.floor_hei = floor_height

        self.image = pygame.Surface([200, floor_height])
        self.image.fill(DARK_GREEN)
        pygame.draw.rect(self.image, FIRUZAYI, (0, 0, 200, self.floor_hei))
        pygame.draw.rect(self.image, BLACK, (0, 0, 100, self.floor_hei), 2)
        pygame.draw.rect(self.image, BLACK, (100, 0, 100, self.floor_hei), 2)
        self.rect = self.image.get_rect()

    def update(self, is_up):
        if is_up:
            self.rect.y = self.rect.y - self.floor_hei
        else:
            self.rect.y = self.rect.y + self.floor_hei

    def draw(self, screen):
        # screen.blit(self.image, self.rect)
        screen.blit(self.image, (self.rect.x, self.rect.y))


class PygameWindow(object):

    def __init__(self):
        self.floor_number = 6
        self.destined_floor = 3
        self.floor_height = 100
        self.screen = None
        self.clock = pygame.time.Clock()

    def activate(self, floor_num):
        self.floor_number = floor_num

        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Skyscraper Drawing Tool")
        self.Elevator_Loop()

    def define_destination_floor(self, info):
        self.destined_floor = info

    def define_floor_height(self):
        self.floor_height = int(screen_height / self.floor_number)

    def draw_floor(self):

        my_width = 100
        # print("Floor hei: ", self.floor_height)
        my_height = screen_height - self.floor_height

        # Set the floor color
        if self.floor_number % 2 == 0:
            color = RED
        else:
            color = WHITE

        for i in range(self.floor_number):
            # Draw the floor
            pygame.draw.rect(self.screen, color, (my_width, my_height, 600, self.floor_height), 2)
            pygame.draw.rect(self.screen, DARK_GREEN, (300, my_height, 200, self.floor_height))
            self.draw_window(my_width + 100, my_height + 0.1 * self.floor_height, self.floor_height * 0.8)

            font1 = pygame.font.SysFont('chalkduster.ttf', 24)
            img1 = font1.render(str(i + 1), True, BLACK)
            self.screen.blit(img1, (650, my_height + self.floor_height / 2))

            my_height -= self.floor_height

    # Set the initial floor number

    def get_width(self):
        return screen_width

    def get_height(self):
        return screen_height

    def get_buffer(self):
        return pygame.Surface.get_buffer(self.screen)

    def draw_window(self, wid, hei, window_size):

        half_size = window_size / 2

        pygame.draw.rect(self.screen, BLACK, (wid, hei, half_size, half_size), 2)
        pygame.draw.rect(self.screen, BLACK, (wid + half_size, hei, half_size, half_size), 2)
        pygame.draw.rect(self.screen, BLACK, (wid, hei + half_size, half_size, half_size), 2)
        pygame.draw.rect(self.screen, BLACK, (wid + half_size, hei + half_size, half_size, half_size), 2)

    def Elevator_Loop(self):
        current = 1
        self.define_floor_height()

        running = True
        my_elevator = Elevator(self.floor_height)
        my_elevator.rect.x = 300
        my_elevator.rect.y = screen_height - self.floor_height

        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.fill(SKY)
            pygame.draw.rect(self.screen, STONE, (100, 0, 600, 600))
            self.draw_floor()

            my_elevator.draw(self.screen)
            pygame.display.update()
            self.clock.tick(1)

            if current != self.destined_floor:
                if current < self.destined_floor:
                    my_elevator.update(True)
                    current += 1
                else:
                    my_elevator.update(False)
                    current -= 1

            pygame.display.update()
            self.clock.tick(5)

        # Quit Pygame
        pygame.quit()
        quit()
