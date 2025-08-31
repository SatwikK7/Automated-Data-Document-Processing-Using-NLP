# enrollment.py
import torch
import numpy as np
import pickle
import pandas as pd
from PIL import Image
from torchvision import transforms
import os

from sigver.featurelearning.models import SigNet

MODEL_PATH = "models/signet.pth"   # pretrained SigNet weights
OUTPUT_LOOKUP = "signature_lookup.pkl"

# input file: can be Excel (.xlsx) or CSV (.csv)
INPUT_FILE = "reference_signatures.xlsx"   # or .csv

# Preprocessing same as before
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((170, 242)),
    transforms.CenterCrop((150, 220)),
    transforms.ToTensor()
])

def load_model(model_path):
    saved = torch.load(model_path, map_location="cpu")
    state_dict = saved[0] if isinstance(saved, (list, tuple)) else saved
    model = SigNet()
    model.load_state_dict(state_dict)
    model.eval()
    return model

def get_embedding(model, image_path):
    img = Image.open(image_path).convert("RGB")
    x = transform(img).unsqueeze(0)
    with torch.no_grad():
        feat = model(x)
    return feat.cpu().numpy().squeeze()

def create_lookup_from_file(model, input_file, out_file=OUTPUT_LOOKUP):
    # Read Excel or CSV into DataFrame
    if input_file.endswith(".xlsx"):
        df = pd.read_excel(input_file)
    elif input_file.endswith(".csv"):
        df = pd.read_csv(input_file)
    else:
        raise ValueError("Input file must be .xlsx or .csv")

    lookup = {}
    for _, row in df.iterrows():
        name = str(row["Counterparty"]).strip()
        path = str(row["ImagePath"]).strip()
        if not os.path.exists(path):
            print(f"[WARN] File not found for {name}: {path}")
            continue

        emb = get_embedding(model, path)
        lookup[name] = emb.astype(np.float32)
        print(f"[ENROLL] {name} -> embedding shape {emb.shape}")

    with open(out_file, "wb") as f:
        pickle.dump(lookup, f)
    print(f"[DONE] saved lookup to {out_file}. Entries: {len(lookup)}")

if __name__ == "__main__":
    if not os.path.exists(MODEL_PATH):
        raise SystemExit("Model file not found. Download signet.pth under models/")
    model = load_model(MODEL_PATH)
    create_lookup_from_file(model, INPUT_FILE)
