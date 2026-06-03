"""
Train the ML classifier on the CSIC 2010 dataset.

Usage:
  python train.py --data-dir data/

Place the CSIC 2010 .txt files in the data/ folder before running:
  - normalTrafficTraining.txt
  - normalTrafficTest.txt
  - anomalousTrafficTest.txt
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.preprocessor import load_dataset
from src.classifier import AttackClassifier


def main():
    parser = argparse.ArgumentParser(description="Train the attack detection classifier")
    parser.add_argument("--data-dir", default="data", help="Directory containing CSIC 2010 .txt files")
    parser.add_argument("--model-out", default="models/classifier.joblib", help="Output path for trained model")
    args = parser.parse_args()

    print(f"Loading CSIC 2010 dataset from '{args.data_dir}'...")
    df = load_dataset(args.data_dir)

    print(f"\nDataset loaded: {len(df)} requests total")
    print(df["label"].value_counts().to_string())

    requests = df.to_dict("records")
    labels = df["label"].tolist()

    print("\nTraining Random Forest classifier...")
    clf = AttackClassifier()
    info = clf.train(requests, labels, verbose=True)

    clf.save(args.model_out)
    print(f"\nDone. Classes: {info['classes']}, Samples: {info['n_samples']}")


if __name__ == "__main__":
    main()
