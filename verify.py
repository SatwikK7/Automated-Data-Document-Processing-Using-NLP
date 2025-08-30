# verify.py

from sigver.featurelearning.models import SigNet

MODEL_PATH = "/content/drive/MyDrive/Dataset/Database/signet.pth"
LOOKUP_PATH = "/content/drive/MyDrive/Dataset/Database/signature_lookup.pkl"


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

def verify(test_image_path, claimed_name, threshold=0.6):
    if not os.path.exists(MODEL_PATH):
        raise SystemExit("Model weights not found. Place signet.pth under models/")

    if not os.path.exists(LOOKUP_PATH):
        raise SystemExit("Lookup file not found. Run enrollment.py first.")

    model = load_model(MODEL_PATH)

    with open(LOOKUP_PATH, "rb") as f:
        lookup = pickle.load(f)

    if claimed_name not in lookup:
        print(f"[ERROR] {claimed_name} not found in lookup.")
        return False

    ref_emb = lookup[claimed_name]
    test_emb = get_embedding(model, test_image_path)

    # Euclidean distance
    dist = np.linalg.norm(test_emb - ref_emb)
    print(f"[INFO] distance = {dist:.4f}")

    # You can use cosine as an alternative
    # cos_sim = np.dot(test_emb, ref_emb) / (np.linalg.norm(test_emb)*np.linalg.norm(ref_emb))

    # threshold: start with 0.6 (example). Must be calibrated on validation data.
    if dist < threshold:
        print(f"✅ ACCEPTED: {claimed_name} (distance {dist:.4f} < {threshold})")
        return True
    else:
        print(f"❌ REJECTED: {claimed_name} (distance {dist:.4f} >= {threshold})")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python verify.py <test_signature.png> <ClaimedCounterpartyName> [threshold]")
        sys.exit(1)
    test_img = sys.argv[1]
    claimed = sys.argv[2]
    thresh = float(sys.argv[3]) if len(sys.argv) >= 4 else 0.6
    verify(test_img, claimed, threshold=thresh)
