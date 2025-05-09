import arcade
import math
import random
import serial  # Import the serial library

TANK_SPEED_PIXELS = 55  # How many pixels per second the tank travels
TANK_TURN_SPEED_DEGREES = 40  # How fast the tank's body can turn
BULLET_SPEED_PIXELS = 6  # How many pixels per second the bullet travels
ZOMBIE_SPEED_PIXELS = 1  # How many pixels per second the zombie travels

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
SIZE_TANK = 100
SIZE_ZOMBIE = 100
SCREEN_MIDDLE = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
SPAWN_RATE = 0.02
SCREEN_TITLE = "Rotating Tank Example"

from PIL import Image

image = Image.open("code/ui/tank.png")
image = image.resize((SIZE_TANK, SIZE_TANK))
image = image.rotate(180)
image.save("code/ui/tank_rotated.png")

image = Image.open("code/ui/zombie.gif")
image = image.resize((SIZE_ZOMBIE, SIZE_ZOMBIE))
image.save("code/ui/zombie_rotated.gif")
# These paths are built-in resources included with arcade
TANK_BODY_PATH = "code/ui/tank_rotated.png"
ZOMBIE_PATH = "code/ui/zombie_rotated.gif"

class ExampleWindow(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Initialize serial port
        self.serial_port = '/dev/cu.usbmodem11303'  # Update with your serial port
        self.ser = serial.Serial(port=self.serial_port, baudrate=115200)
        print(f"Using serial port: {self.serial_port}")

        # Set Background to be green
        self.background_color = arcade.csscolor.SEA_GREEN

        # The tank sprite
        self.tank = arcade.Sprite(TANK_BODY_PATH)
        self.tank.position = SCREEN_MIDDLE

        self.tank_direction = 0.0  # Forward & backward throttle 
        self.tank_turning = 0.0  # Turning strength to the left or right

        self.tank_sprite_list = arcade.SpriteList()
        self.tank_sprite_list.append(self.tank)

        self.bullet_list = arcade.SpriteList()
        self.zombie_list = arcade.SpriteList()
        self.score = 0
        self.score_texts = []

        self.control_text = arcade.Text(
            "Use the board to move the tank and shoot with the blue button",
            SCREEN_MIDDLE[0], 15,
            anchor_x='center')

        self.game_over = False
        self.game_over_text = arcade.Text(
            "Game Over! Press R to Restart",
            SCREEN_MIDDLE[0], SCREEN_MIDDLE[1],
            anchor_x='center', color=arcade.color.RED, font_size=24)

        self.pressed_keys = set()  # Initialize pressed_keys as a set

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        self.pressed_keys.add(key)

    def on_key_release(self, key, modifiers):
        """Called whenever a key is released."""
        self.pressed_keys.discard(key)

    def on_draw(self):
        self.clear()
        self.tank_sprite_list.draw()
        self.bullet_list.draw()
        self.zombie_list.draw()
        self.control_text.draw()
        if self.game_over:
            self.game_over_text.draw()
        self.draw_score()

    def on_update(self, delta_time: float):
        if not self.game_over:
            # Read the x_value from the serial port
            x_value, y_value, shoot = self.read_serial_data()

            # Use the x_value to control the tank's turning
            if x_value < -10:
                self.tank_turning = -1  # Turn left
            elif x_value > 10:
                self.tank_turning = 1  # Turn right
            else:
                self.tank_turning = 0  # No turning

            # Use the y_value to control the tank's movement
            if y_value > 5:
                self.tank_direction = -1  # Move forward
            elif y_value < -5:
                self.tank_direction = 1  # Move backward
            else:
                self.tank_direction = 0  # No movement

            # Shoot bullet if shoot value is 1
            if shoot == 1:
                self.shoot_bullet()

            self.move_tank(delta_time)
            self.bullet_list.update()
            self.zombie_list.update()
            self.update_zombie_directions()  # Update zombie directions towards the tank
            self.spawn_zombies()
            self.check_for_collisions()
            self.check_bullet_hits()
            self.update_score_texts(delta_time)
        else:
            # Check if R key is pressed to restart the game
            if arcade.key.R in self.pressed_keys:
                tx_string = "GAME_OVER\n"
                bytes_written = self.ser.write(tx_string.encode())
                print(f"Bytes written: {bytes_written}")
                self.restart_game()

    def read_serial_data(self):
        try:
            serial_data = self.ser.readline().decode()
            print(serial_data)
            if 'calibration' in serial_data or 'Calibration' in serial_data:
                return 0, 0, 0
            else:
                data_parts = serial_data.split(",")
                x_value_str = data_parts[0].split(":")[1].strip() if len(data_parts) > 0 else "0"
                x_value = float(x_value_str)
                y_value_str = data_parts[1].split(":")[1].strip() if len(data_parts) > 1 else "0"
                y_value = float(y_value_str)
                shoot_str = data_parts[3].split(":")[1].strip() if len(data_parts) > 3 else "0"
            shoot = int(shoot_str)
        except (ValueError, serial.SerialException):
            x_value = 0
            y_value = 0
            shoot = 0
        return x_value, y_value, shoot

    def move_tank(self, delta_time):
        """
        Perform all calculations for moving the tank's body
        """

        # Rotate the tank's body in place without changing position
        self.tank.angle += TANK_TURN_SPEED_DEGREES * self.tank_turning * delta_time

        # Calculate how much the tank should move forward or back
        move_magnitude = self.tank_direction * TANK_SPEED_PIXELS * delta_time
        x_dir = math.cos(self.tank.radians - math.pi / 2) * move_magnitude
        y_dir = math.sin(self.tank.radians - math.pi / 2) * move_magnitude

        # Move the tank's body
        new_x = self.tank.center_x + x_dir
        new_y = self.tank.center_y + y_dir

        # Ensure the tank does not move out of the boundary
        if 0 <= new_x <= SCREEN_WIDTH and 0 <= new_y <= SCREEN_HEIGHT:
            self.tank.position = new_x, new_y


    def shoot_bullet(self):
        bullet = arcade.SpriteCircle(5, arcade.color.YELLOW)
        bullet.position = self.tank.position
        bullet.angle = self.tank.angle
        bullet.change_x = math.cos(self.tank.radians - math.pi / 2) * BULLET_SPEED_PIXELS
        bullet.change_y = math.sin(self.tank.radians - math.pi / 2) * BULLET_SPEED_PIXELS
        self.bullet_list.append(bullet)

    def spawn_zombies(self):
        if random.random() < SPAWN_RATE:  # Slow spawn rate
            margin = random.choice(['top', 'bottom', 'left', 'right'])
            if margin == 'top':
                x = random.randint(0, SCREEN_WIDTH)
                y = SCREEN_HEIGHT
            elif margin == 'bottom':
                x = random.randint(0, SCREEN_WIDTH)
                y = 0
            elif margin == 'left':
                x = 0
                y = random.randint(0, SCREEN_HEIGHT)
            else:  # right
                x = SCREEN_WIDTH
                y = random.randint(0, SCREEN_HEIGHT)

            zombie = arcade.Sprite(ZOMBIE_PATH)
            zombie.position = x, y
            zombie.angle = math.degrees(math.atan2(self.tank.center_y - y, self.tank.center_x - x))
            zombie.change_x = math.cos(math.radians(zombie.angle)) * ZOMBIE_SPEED_PIXELS
            zombie.change_y = math.sin(math.radians(zombie.angle)) * ZOMBIE_SPEED_PIXELS
            self.zombie_list.append(zombie)

    def update_zombie_directions(self):
        for zombie in self.zombie_list:
            zombie.angle = math.degrees(math.atan2(self.tank.center_y - zombie.center_y, self.tank.center_x - zombie.center_x))
            zombie.change_x = math.cos(math.radians(zombie.angle)) * ZOMBIE_SPEED_PIXELS
            zombie.change_y = math.sin(math.radians(zombie.angle)) * ZOMBIE_SPEED_PIXELS

    def check_for_collisions(self):
        if arcade.check_for_collision_with_list(self.tank, self.zombie_list):
            self.game_over = True
            tx_string = "GAME_OVER\n"
            bytes_written = self.ser.write(tx_string.encode())
            print(f"Bytes written: {bytes_written}")

    def check_bullet_hits(self):
        for bullet in self.bullet_list:
            hit_zombies = arcade.check_for_collision_with_list(bullet, self.zombie_list)
            if hit_zombies:
                bullet.remove_from_sprite_lists()
                for zombie in hit_zombies:
                    self.show_score_text(zombie.position)
                    zombie.remove_from_sprite_lists()
                    self.score += 1

    def show_score_text(self, position):
        score_text = arcade.Text(
            "+1", position[0], position[1],
            anchor_x='center', color=arcade.color.WHITE, font_size=10)
        self.score_texts.append((score_text, 2.0))  # 2 seconds duration

    def update_score_texts(self, delta_time):
        self.score_texts = [(score_text, time_left - delta_time) for score_text, time_left in self.score_texts if time_left - delta_time > 0]

    def draw_score(self):
        score_display = arcade.Text(
            f"Score: {self.score}", 10, SCREEN_HEIGHT - 45,
            anchor_x='left', color=arcade.color.WHITE, font_size=30)
        score_display.draw()

    def restart_game(self):
        self.game_over = False
        self.tank.position = SCREEN_MIDDLE
        self.zombie_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.score = 0
        self.score_texts = []

def main():
    window = ExampleWindow()
    arcade.run()

if __name__ == '__main__':
    main()