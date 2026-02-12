from insightface.app import FaceAnalysis

print("Downloading model (2-3 minutes)...")
app = FaceAnalysis(name='buffalo_sc', providers=['CPUExecutionProvider'])
app.prepare(ctx_id=-1, det_size=(640, 480))
print("✅ Model downloaded!")