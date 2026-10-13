import json
from threading import Lock
from PIL import Image
import torch
from torch import nn
from torchvision import models, transforms
from .config import get_settings

class PlantPredictor:
    """Loads project-generated ResNet18 weights only when valid artifacts exist."""
    def __init__(self):
        self._model = None
        self._classes: list[str] = []
        self._lock = Lock()
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)), transforms.ToTensor(),
            transforms.Normalize([.485, .456, .406], [.229, .224, .225]),
        ])

    @property
    def ready(self) -> bool:
        return self._model is not None

    def load(self) -> bool:
        settings = get_settings()
        model_path, class_path = settings.resolved_model_path, settings.resolved_class_names_path
        if not model_path.is_file() or not class_path.is_file():
            return False
        try:
            classes = json.loads(class_path.read_text(encoding="utf-8"))
            if not isinstance(classes, list) or not classes:
                return False
            payload = torch.load(model_path, map_location=self._device, weights_only=True)
            state = payload["state_dict"] if isinstance(payload, dict) and "state_dict" in payload else payload
            model = models.resnet18(weights=None)
            model.fc = nn.Linear(model.fc.in_features, len(classes))
            model.load_state_dict(state)
            model.eval().to(self._device)
            self._model, self._classes = model, [str(x) for x in classes]
            return True
        except (OSError, ValueError, RuntimeError, KeyError, TypeError, json.JSONDecodeError):
            self._model, self._classes = None, []
            return False

    def predict(self, image: Image.Image, top_k: int = 3) -> list[dict]:
        if not self.ready:
            raise RuntimeError("No trained model is configured. Train with ml/train.py and set MODEL_PATH.")
        tensor = self.transform(image.convert("RGB")).unsqueeze(0).to(self._device)
        with self._lock, torch.inference_mode():
            probabilities = torch.softmax(self._model(tensor), dim=1)[0]
            values, indices = torch.topk(probabilities, k=min(top_k, len(self._classes)))
        return [{"class_name": self._classes[int(i)], "confidence": float(v)} for v, i in zip(values.cpu(), indices.cpu())]
