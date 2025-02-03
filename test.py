from PIL import Image, ImageDraw

def create_default_avatar(filename="avatar.png", size=100):
    img = Image.new("RGBA", (size, size), (200, 200, 200, 255))  # Gray background
    draw = ImageDraw.Draw(img)
    
    # Draw a circular face
    draw.ellipse((10, 10, size-10, size-10), fill=(150, 150, 150, 255))  # Darker gray face
    
    # Draw eyes
    eye_size = size // 10
    draw.ellipse((size//3 - eye_size//2, size//3, size//3 + eye_size//2, size//3 + eye_size), fill="black")
    draw.ellipse((2*size//3 - eye_size//2, size//3, 2*size//3 + eye_size//2, size//3 + eye_size), fill="black")

    # Draw a smile
    draw.arc((size//4, size//2, 3*size//4, 3*size//4), start=20, end=160, fill="black", width=3)
    
    img.save(filename)

# Create and save the default avatar
create_default_avatar()
