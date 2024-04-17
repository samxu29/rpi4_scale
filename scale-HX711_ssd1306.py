import time
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO
from hx711 import HX711

# Raspberry Pi pin configuration for the SSD1306 display:
RST = 24  # GPIO pin for the reset signal, change if necessary

# Initialize the HX711 using GPIO pins
hx711 = HX711(dout_pin=5, pd_sck_pin=6, channel='A', gain=64)
hx711.reset()  # Reset the HX711 before starting

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Load default font.
font = ImageFont.load_default()

def display_message(message):
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((0, 0), message, font=font, fill=255)
    disp.image(image)
    disp.display()

# Calibration
# Prompt the user to remove any weight from the load cell
display_message("Remove any object\nfor calibration!")
input("\nRemove any weight from the scale !!! \nThen press Enter to continue...")
tare_value = hx711.get_raw_data()[0]  # Get the initial raw value as tare weight

# Prompt the user to place a known weight on the load cell
display_message("Check terminal to\nenter known weight!")
known_weight_grams = float(input("\nPlace known weight object on the scale !!! \nEnter the known weight in grams: "))

raw_value = hx711.get_raw_data()[0] - tare_value  # Subtract tare value from raw reading
calibration_factor = raw_value / known_weight_grams
print("Calibration factor: ", calibration_factor)

while True:
    try:
        # Read raw data from HX711 and subtract tare value
        raw_data = hx711.get_raw_data()[0] - tare_value
        
        # Convert raw data to grams
        weight_grams = raw_data / calibration_factor
        
        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        
        # Draw the text.
        draw.text((0, 0), 'Current Weight: \n{:.2f}g'.format(weight_grams), font=font, fill=255)
        
        # Display image.
        disp.image(image)
        disp.display()
        
        # Print weight in grams to console
        print('Current weight: {:.2f} g'.format(weight_grams))

        time.sleep(0.5)
        
    except (KeyboardInterrupt, SystemExit):
        disp.clear()
        disp.display()
        GPIO.cleanup()
        break
