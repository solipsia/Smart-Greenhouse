from PIL import Image, ImageDraw, ImageFont
import datetime

def createoverlay():
    image_size = (4608, 2592)
    font_size = 50
    text_color = "black"
    # Get the current date and time
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_time="test"
    # Attempt to load the specified font and size
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    image = Image.new("RGBA", image_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # Calculate the text size and position
    text_size = draw.textbbox((0, 0), current_time, font=font)
    text_position = (10, image_size[1] - text_size[3] - 10)
    # Draw the date and time on the image
    draw.text(text_position, current_time, font=font, fill=text_color)
    # Save the image, overwrite if exists
    image_path = "/mnt/synology/public/greenhouse/test_image2.png"
    image.save(image_path)
    image.close()
    #print(f"Overlay saved to {image_path}")

createoverlay()

# Define the size and text parameters
image_size = (4608, 2592)
font_size = 50
text_color = "black"

# Get the current date and time
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Attempt to load the specified font and size
font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
image = Image.new("RGBA", image_size, (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Calculate the text size and position
text_size = draw.textbbox((0, 0), current_time, font=font)
text_position = (10, image_size[1] - text_size[3] - 10)

# Draw the date and time on the image
draw.text(text_position, current_time, font=font, fill=text_color)

# Save the image, overwrite if exists
image_path = "/mnt/synology/public/greenhouse/test_image.png"
image.save(image_path)

print(f"Overlay saved to {image_path}")
