import cv2
import matplotlib.pyplot as plt

image = cv2.imread(r"../photo/Portugal/NDVI_before_Portugal.jpg")

if image is None:
    print("Error: Image not found or path is incorrect.")
else:
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    plt.imshow(image_rgb)
    plt.axis("off")  # Hide axes
    plt.show()

