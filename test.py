import arcade
import math
import random
import serial  # Import the serial library

TANK_SPEED_PIXELS = 40  # How many pixels per second the tank travels
TANK_TURN_SPEED_DEGREES = 40  # How fast the tank's body can turn
BULLET_SPEED_PIXELS = 6  # How many pixels per second the bullet travels
ZOMBIE_SPEED_PIXELS = 1  # How many pixels per second the zombie travels

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_MIDDLE = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

SCREEN_TITLE = "Rotating Tank Example"

from PIL import Image

image = Image.open("code/ui/942355.png")
image = image.resize((20, 24))
image = image.rotate(180)
image.save("code/ui/942355_rotated.png")

image = Image.open("code/ui/export_move.gif")
image = image.resize((20, 24))
image.save("code/ui/export_move_rotated.gif")
# These paths are built-in resources included with arcade
TANK_BODY_PATH = "code/ui/942355_rotated.png"
ZOMBIE_PATH = "code/ui/export_move_rotated.gif"

class ExampleWindow(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Initialize serial port
        self.serial_port = '/dev/cu.usbmodem1303'  # Update with your serial port
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
            "Arrow keys to move tank, SPACE to shoot",
            SCREEN_MIDDLE[0], 15,
            anchor_x='center')

        self.game_over = False
        self.game_over_text = arcade.Text(
            "Game Over! Press R to Restart",
            SCREEN_MIDDLE[0], SCREEN_MIDDLE[1],
            anchor_x='center', color=arcade.color.RED, font_size=24)

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
            x_value, y_value = self.read_serial_data()

            # Use the x_value to control the tank's turning
            if x_value < -10:
                self.tank_turning = -1  # Turn left
            elif x_value > 10:
                self.tank_turning = 1  # Turn right
            else:
                self.tank_turning = 0  # No turning

            # Use the y_value to control the tank's movement
            if y_value > 5:
                self.tank_direction = 1  # Move forward
            elif y_value < -5:
                self.tank_direction = -1  # Move backward
            else:
                self.tank_direction = 0  # No movement

            self.move_tank(delta_time)
            self.bullet_list.update()
            self.zombie_list.update()
            self.spawn_zombies()
            self.check_for_collisions()
            self.check_bullet_hits()
            self.update_score_texts(delta_time)

    def read_serial_data(self):
        try:
            serial_data = self.ser.readline().decode()
            print(serial_data)
            x_value_str = serial_data.split(",")[0].split(":")[1].strip()
            x_value = float(x_value_str)
            y_value_str = serial_data.split(",")[1].split(":")[1].strip()
            y_value = float(y_value_str)
        except (ValueError, serial.SerialException):
            x_value = 0
            y_value = 0
        return x_value, y_value

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
        self.tank.position = self.tank.center_x + x_dir, self.tank.center_y + y_dir

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.UP:
            self.tank_direction += 1
        elif symbol == arcade.key.DOWN:
            self.tank_direction -= 1
        elif symbol == arcade.key.LEFT:
            self.tank_turning += 1
        elif symbol == arcade.key.RIGHT:
            self.tank_turning -= 1
        elif symbol == arcade.key.SPACE:
            self.shoot_bullet()
        elif symbol == arcade.key.R and self.game_over:
            self.restart_game()

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.UP:
            self.tank_direction -= 1
        elif symbol == arcade.key.DOWN:
            self.tank_direction += 1
        elif symbol == arcade.key.LEFT:
            self.tank_turning -= 1
        elif symbol == arcade.key.RIGHT:
            self.tank_turning += 1

    def shoot_bullet(self):
        bullet = arcade.SpriteCircle(5, arcade.color.YELLOW)
        bullet.position = self.tank.position
        bullet.angle = self.tank.angle
        bullet.change_x = math.cos(self.tank.radians - math.pi / 2) * BULLET_SPEED_PIXELS
        bullet.change_y = math.sin(self.tank.radians - math.pi / 2) * BULLET_SPEED_PIXELS
        self.bullet_list.append(bullet)

    def spawn_zombies(self):
        if random.random() < 0.01:  # Slow spawn rate
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

    def check_for_collisions(self):
        if arcade.check_for_collision_with_list(self.tank, self.zombie_list):
            self.game_over = True

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
            anchor_x='center', color=arcade.color.WHITE, font_size=12)
        self.score_texts.append((score_text, 2.0))  # 2 seconds duration

    def update_score_texts(self, delta_time):
        for i, (score_text, time_left) in enumerate(self.score_texts):
            time_left -= delta_time
            if time_left <= 0:
                self.score_texts.pop(i)
            else:
                self.score_texts[i] = (score_text, time_left)

    def draw_score(self):
        score_display = arcade.Text(
            f"Score: {self.score}", 10, SCREEN_HEIGHT - 20,
            anchor_x='left', color=arcade.color.WHITE, font_size=14)
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
    window.run()

if __name__ == '__main__':
    main()