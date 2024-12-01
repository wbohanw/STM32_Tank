# ECSE444 FINAL PROJECT - Tank Game

## Overview
This project is a Python-based tank shooting game implemented using the [Arcade](https://api.arcade.academy/) game development library. The player controls a tank using inputs from a serial-connected device (e.g., an Arduino or a similar controller). The goal is to shoot zombies while avoiding collisions. Zombies spawn randomly from the screen's edges and move toward the tank.


## Requirements
- Python 3.7+
- Libraries:
  - [Arcade](https://api.arcade.academy/) (`pip install arcade`)
  - [Pillow](https://pillow.readthedocs.io/) (`pip install pillow`)
  - [PySerial](https://pyserial.readthedocs.io/) (`pip install pyserial`)

## Setup

1. **Install Required Libraries:**
   Run the following command to install the required Python libraries:
   ```bash
   pip install arcade pillow pyserial

2. **Config Port Path (MacOS)**
   - run
    ```bash
     ls /dev/tty.*
    ```
   - You will see
     `/dev/cu.usbmodemXXXX`
     change line 39 in test.py
    ```python
      39 self.serial_port = '/dev/cu.usbmodemXXXX'  # Update with your serial port
    ```
  
3. **Run STM file**
   - Open main.c in STM32CUBE
   - Run debug mode and press continue on the top menu bar
4. **Run python**
   Run the following code in the terminal
   ```bash
   pyhton test.py

5. Once the game start, you will need to calibrate the sensor, press Blue button(user) on STM32 Board 4 times
6. Once you hear a sound indicating calibration is down, the game start
7. use the STM board as a Console and Blue button to shoot
8. Enjoy the game

