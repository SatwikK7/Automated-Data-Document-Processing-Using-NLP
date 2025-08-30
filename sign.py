# enrollment.py
import torch
import numpy as np
import pickle
from PIL import Image
from torchvision import transforms
import os

# Import SigNet model from sigver package
from sigver.featurelearning.models import SigNet

# -- Change this to your folder with reference signature images --
# reference_images = { "CounterpartyName": "path/to/ref_image.png", ... }
reference_images = {
    "auth1": "/content/drive/MyDrive/Dataset/Database/auth1/00200002.png"
}

MODEL_PATH = "/content/drive/MyDrive/Dataset/Database/signet.pth"   # file you downloaded from sigver repo links
OUTPUT_LOOKUP = "/content/drive/MyDrive/Dataset/Database/signature_lookup.pkl"

# Preprocessing used by sigver (as in its README):
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((170, 242)),          # resize H x W used in sigver README
    transforms.CenterCrop((150, 220)),      # center crop used at test time
    transforms.ToTensor()                   # to tensor -> automatically divides by 255.0
])

def load_model(model_path):
    # The saved file contains (state_dict, classification_layer, forg_layer)
    saved = torch.load(model_path, map_location="cpu")
    state_dict = saved[0] if isinstance(saved, (list, tuple)) else saved
    model = SigNet()
    model.load_state_dict(state_dict)
    model.eval()
    return model

def get_embedding(model, image_path):
    img = Image.open(image_path).convert("RGB")
    x = transform(img).unsqueeze(0)  # shape 1 x 1 x H x W
    with torch.no_grad():
        feat = model(x)               # output embedding tensor (1 x D)
    return feat.cpu().numpy().squeeze()  # return 1D numpy vector

def create_lookup(model, ref_images, out_file=OUTPUT_LOOKUP):
    lookup = {}
    for name, path in ref_images.items():
        if not os.path.exists(path):
            print(f"[WARN] reference image not found for {name}: {path}")
            continue
        emb = get_embedding(model, path)
        lookup[name] = emb.astype(np.float32)
        print(f"[ENROLL] {name} -> embedding shape {emb.shape}")

    with open(out_file, "wb") as f:
        pickle.dump(lookup, f)
    print(f"[DONE] saved lookup to {out_file}. Contains {len(lookup)} entries.")

if __name__ == "__main__":
    if not os.path.exists(MODEL_PATH):
        raise SystemExit("Model file not found. Download signet.pth and place under models/signet.pth")
    model = load_model(MODEL_PATH)
    create_lookup(model, reference_images)
