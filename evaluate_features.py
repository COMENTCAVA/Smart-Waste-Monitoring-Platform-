# evaluate_features.py

import numpy as np
import pandas as pd
from scipy import stats
from app import create_app
from app.models import Image

def load_data():
    """
    Charge depuis la BDD toutes les images et leurs features+label
    Retourne un DataFrame pandas.
    """
    app = create_app()
    with app.app_context():
        imgs = Image.query.all()
        rows = []
        for img in imgs:
            rows.append({
                'label':          img.label,
                'avg_r':          img.avg_color_r or 0.0,
                'avg_g':          img.avg_color_g or 0.0,
                'avg_b':          img.avg_color_b or 0.0,
                'file_size':      img.file_size or 0,
                'contrast':       img.contrast or 0.0,
                'edges_count':    img.edges_count or 0,
                'dark_ratio':     (sum(img.hist_gray[:50]) / sum(img.hist_gray)
                                   if img.hist_gray and sum(img.hist_gray)>0 else 0.0),
                'std_gray':       (np.sqrt(
                                     (((np.arange(256)-((np.arange(256)*img.hist_gray).sum()/sum(img.hist_gray)))**2)*img.hist_gray).sum()
                                   / sum(img.hist_gray))
                                   if img.hist_gray and sum(img.hist_gray)>0 else 0.0),
                'occupancy_ratio': img.occupancy_ratio or 0.0,
                'hue_ratio':       (sum(img.hist_h[35:85]) / sum(img.hist_h)
                             if img.hist_h and sum(img.hist_h)>0 else 0.0)
            })
    df = pd.DataFrame(rows)
    # Convertir label en binaire 0=Vide, 1=Pleine
    df['y'] = df['label'].apply(lambda v: 1 if v=='Pleine' else 0)
    return df

def cohen_d(x1, x2):
    n1, n2 = len(x1), len(x2)
    s1, s2 = x1.std(ddof=1), x2.std(ddof=1)
    # pooled std
    s = np.sqrt(((n1-1)*s1**2 + (n2-1)*s2**2) / (n1+n2-2))
    return (x1.mean() - x2.mean()) / s if s>0 else 0.0

def analyze(df):
    features = ['avg_r','avg_g','avg_b','file_size',
                'contrast','edges_count','dark_ratio',
                'std_gray','hue_ratio','occupancy_ratio']
    results = []
    y1 = df[df['y']==1]  # Pleine
    y0 = df[df['y']==0]  # Vide

    for feat in features:
        x1 = y1[feat].to_numpy()
        x0 = y0[feat].to_numpy()
        d   = cohen_d(x1, x0)
        r_pb, p = stats.pointbiserialr(df['y'], df[feat])
        results.append({
            'feature':        feat,
            'mean_pleine':    x1.mean(),
            'std_pleine':     x1.std(ddof=1),
            'mean_vide':      x0.mean(),
            'std_vide':       x0.std(ddof=1),
            'cohen_d':        d,
            'pointbiserial':  r_pb,
            'p_value':        p
        })

    res = pd.DataFrame(results)
    res['abs_d'] = res['cohen_d'].abs()
    res = res.sort_values('abs_d', ascending=False)
    pd.set_option('display.float_format', '{:.3f}'.format)
    print("\n### Séparation des classes par feature ###\n")
    print(res[['feature','mean_vide','mean_pleine','cohen_d','pointbiserial','p_value']])
    return res

if __name__ == '__main__':
    df = load_data()
    analyze(df)