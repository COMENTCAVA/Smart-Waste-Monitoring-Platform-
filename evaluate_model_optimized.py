#!/usr/bin/env python3
# evaluate_model_optimized.py

import random
import numpy as np
import pandas as pd

# Charge les données en DataFrame (avec y=0/1, avg_r,g,b, file_size, contrast, edges_count, dark_ratio, std_gray)
from evaluate_features import load_data

def classify_batch(df: pd.DataFrame,
                   B: float, S: float, C: float,
                   E: float, D: float, SG: float) -> float:
    """
    Calcule l'accuracy (en %) pour un ensemble de seuils donné,
    sur le DataFrame préchargé `df`.
    """
    gray = (df['avg_r'] + df['avg_g'] + df['avg_b']) / 3.0
    cond1 = (df['file_size']   > S) & (gray         < B)
    cond2 = (df['contrast']    > C)
    cond3 = (df['edges_count'] > E)
    cond4 = (df['dark_ratio']  > D)
    cond5 = (df['std_gray']    > SG)
    votes = cond1.astype(int) + cond2.astype(int) + cond3.astype(int) \
          + cond4.astype(int) + cond5.astype(int)
    pred = (votes >= 3).astype(int)      # 1 = Pleine, 0 = Vide
    return (pred == df['y']).mean() * 100  # % de bonnes prédictions

def main():
    print("🔄 Chargement des données…")
    df = load_data()
    print(f"📊 {len(df)} images chargées.")

    N_TRIALS = 100_000
    best = {'acc': 0.0}

    print(f"🚀 Lancement de la recherche aléatoire ({N_TRIALS:,} essais)…")
    for i in range(1, N_TRIALS+1):
        B  = random.uniform(0,   255)
        S  = random.uniform(50e3, 500e3)
        C  = random.uniform(0,   200)
        E  = random.uniform(100, 50e3)
        D  = random.uniform(0.1, 0.7)
        SG = random.uniform(0,  300)
        acc = classify_batch(df, B, S, C, E, D, SG)
        if acc > best['acc']:
            best.update(acc=acc, B=B, S=S, C=C, E=E, D=D, SG=SG)
        if i % 10_000 == 0:
            print(f"  • Essais {i:,}/{N_TRIALS:,} — meilleur acc: {best['acc']:.2f}%")

    print("\n✅ Recherche terminée.")
    print("Meilleurs seuils trouvés :")
    print(f"  Brightness  = {best['B']:.1f}")
    print(f"  File size   = {best['S']:.0f}")
    print(f"  Contrast    = {best['C']:.1f}")
    print(f"  Edges count = {best['E']:.0f}")
    print(f"  Dark ratio  = {best['D']:.3f}")
    print(f"  Std gray    = {best['SG']:.1f}")
    print(f"  → Accuracy  = {best['acc']:.2f}%")

if __name__ == '__main__':
    main()