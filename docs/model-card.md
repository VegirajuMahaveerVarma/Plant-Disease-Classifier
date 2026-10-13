# Model card — initial template

## Intended use
Educational classification of leaf images among classes represented during training.

## Not intended for
Definitive diagnosis, pesticide prescription, crop-loss estimation, or automated agricultural decisions.

## Model
ResNet18 transfer learning. No trained weights are committed. Train with `ml/train.py` to create a checkpoint.

## Data
A user-supplied PlantVillage-compatible ImageFolder dataset. Document revision, provenance, class distribution, and usage terms before release.

## Evaluation
No performance figures are claimed. Training records measured validation and held-out test accuracy. Random image splits can overstate field performance, especially if related images appear in multiple splits.

## Limitations
Dataset bias, limited cultivar coverage, image-quality sensitivity, uncertain field performance, and lack of external validation by agricultural specialists.
