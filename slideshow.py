from time import sleep
from sys import exit
from os import listdir
import json
import pygame

class Slideshow:
    """Make a slideshow from a given folder of pictures."""

    def __init__(self):
        """Initialize variables."""
        pygame.init()
        pygame.mouse.set_visible(False)

        # Open, load, and associate the contents of the file with a variable.
        with open('slideshow_config.json') as f:
            try:
                self.config = json.load(f)
            except json.decoder.JSONDecodeError as error:
                print(f"---\nError: Decode error with 'slideshow_config.json'.\nMake sure there are not any misplaced or extra characters in the file.\n\nOutput: {error}\n---")
                exit()

        try:
            # Create variables for each value in the config.
            folder_dir = self.config['folder_directory']
            font_dir = self.config['font_directory']
            font_size = self.config['font_size']
            text = self.config['end_message']
            color = self.config['end_message_color']
            self.fade_color = self.config['fade_to_from']
            self.fade_amount = self.config['fade_amount']
            self.FPS = self.config['FPS']
            self.pic_display_time = (self.config['FPS'] *
                                        self.config['picture_display_time'])
            self.loop = self.config['loop']
            
        except KeyError as error:
            print(f"---\nError: Couldn't find {error} in 'slideshow_config.json'.\n---")
            exit()

        # Create the other variables.
        self.manage_fps = pygame.time.Clock()
        self.clock = 0
        self.wait_time = 0
        self.paused = False
        self.check_number = 0
        self.picture = None
        self.alpha_value = 0
        self.fade = 'in'

        # Create the screen, and get its aspect ratio.
        self.screen = pygame.display.set_mode((0,0) ,pygame.FULLSCREEN)
        self.screen_rect = self.screen.get_rect()
        self.screen_ratio = self.screen_rect.width / self.screen_rect.height

        # Get the name of each item in the folder, and add that name to the end of the folder directory so pygame can be given the image directory.
        picture_dirs = []
        try:
            for picture in listdir(folder_dir):
                picture_dir = folder_dir + '/' + picture
                picture_dirs.append(picture_dir)
        except FileNotFoundError:
            print("---\nError: Not a valid folder directory.\n---")
            exit()

        # Load each image, if there's an issue loading the image, just skip it.
        # Scale each image to fit the display and retain its aspect ratio.
        self.loaded_pictures = []
        for picture in picture_dirs:
            try:
                load_picture = pygame.image.load(picture).convert_alpha()

            except pygame.error as error:

                print(f"---\n{error}.\n---")

            except FileNotFoundError as error:
                print(f"---\nCan't process folders.\n---")

            else:
                load_picture_rect = load_picture.get_rect()
                aspect_ratio = load_picture_rect.width / load_picture_rect.height

                if aspect_ratio <= self.screen_ratio:
                    y = self.screen_rect.height
                    x = int(y * aspect_ratio)

                elif aspect_ratio > self.screen_ratio:
                    x = self.screen_rect.width
                    y = int(x / aspect_ratio)

                scaled_picture = pygame.transform.smoothscale(load_picture, (x,y))
                scaled_rect = scaled_picture.get_rect()
                scaled_rect.center = self.screen_rect.center
                scaled_picture.set_alpha(0, pygame.RLEACCEL)
                self.loaded_pictures.append([scaled_picture, scaled_rect])

        # Pop the first picture from the list.
        # If looping is enabled then append it to the back of the list as well.
        self.picture = self.loaded_pictures.pop(0)
        if self.loop == 'yes':
            self.loaded_pictures.append(self.picture)

        # Configure the end_screen text.
        try:
            font = pygame.font.Font(font_dir, font_size)
        except FileNotFoundError:
            print("---\nError: Not a valid font directory.\n---")
            exit()
        except OverflowError:
            print("---\nError: Font size is to big.\n---")
            exit()

        try:
            end_text = font.render(text, True, color, self.fade_color)
        except ValueError:
            print("---\nError: RGB color values have to be 0 to 255.\n---")
            exit()
        except TypeError:
            print("---\nError: end_message must be a string.\n---")
            exit()

        end_text.set_alpha(0, pygame.RLEACCEL)

        end_text_rect = end_text.get_rect()
        end_text_rect.center = self.screen_rect.center

        self.end_screen = [end_text, end_text_rect]

    def play_slideshow(self):
        """Slideshow loop to run it."""
        while True:
            self.manage_fps.tick(self.FPS)
            self.manage_keybinds()
            self.cycle_pictures()
            self.update_screen()

    def manage_keybinds(self):
        """Manage the slideshow key binds."""
        for event in pygame.event.get():
            # Exit the slideshow.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit()
                # Pause the slideshow.
                elif event.key == pygame.K_SPACE:
                    if self.paused == False:
                        self.paused = True
                    elif self.paused == True:
                        self.paused = False

    def cycle_pictures(self):
        """Play the slideshow once."""
        if not self.paused:
            # Keep the clock updated.
            self.clock += 1
            # Configure how the pictures fade in.
            if self.fade == 'in':
                self.alpha_value += self.fade_amount
                self.picture[0].set_alpha(self.alpha_value)
                if self.alpha_value >= 255:
                    if self.picture == self.end_screen:
                        None
                    else:
                        self.fade = 'out'
                        self.wait_time = self.clock + self.pic_display_time
            # Configure how the pictures fade out.
            elif self.fade == 'out':
                if self.clock >= self.wait_time:
                    self.alpha_value -= self.fade_amount
                    self.picture[0].set_alpha(self.alpha_value)
                    if self.alpha_value <= 0:
                        self.fade = 'in'
                        try:
                            self.picture = self.loaded_pictures.pop(0)
                            if self.loop == 'yes':
                                self.loaded_pictures.append(self.picture)
                        except IndexError:
                            self.picture = self.end_screen

    def update_screen(self):
        self.screen.fill(self.fade_color)

        self.screen.blit(self.picture[0], self.picture[1])

        pygame.display.flip()

if __name__ == '__main__':
    # Make a slideshow instance, and run it.
    ss = Slideshow()
    ss.play_slideshow()