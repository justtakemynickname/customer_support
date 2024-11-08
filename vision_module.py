from torchvision import transforms
from PIL import Image
import torch
from torchvision.models import resnet50

# Load a pre-trained model
model = resnet50(pretrained=True)
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

def handle_image(image_path):
    image = Image.open(image_path).convert("RGB")
    image_tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        outputs = model(image_tensor)
    _, predicted = torch.max(outputs, 1)
    return f"Predicted class: {predicted.item()}"
