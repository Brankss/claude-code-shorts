"""Mappe per What If: TopoJSON Natural Earth, proiezione ortografica e path skia pronti.

Tutto vive su un unico piano in metri centrato sull'origine della storia (x verso est, y verso nord):
la scena a livello strada, la città, il paese, il globo e lo spazio. I path si costruiscono una volta
sola in metri; a ogni frame basta la matrice della camera, così lo zoom continuo costa pochissimo.
"""

import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
import skia

GEO_DIR = Path(__file__).resolve().parent.parent / "assets" / "geo"
R_EARTH = 6_371_000.0


@lru_cache(maxsize=None)
def _topo(name):
    return json.loads((GEO_DIR / name).read_text())


def _arcs(topo):
    """Archi decodificati (delta + quantizzazione) in gradi lon/lat."""
    tr = topo.get("transform")
    out = []
    for arc in topo["arcs"]:
        a = np.asarray(arc, float)
        if tr:
            a = np.cumsum(a, axis=0) * tr["scale"] + tr["translate"]
        out.append(a)
    return out


def _ring(arcs, idx):
    pts = []
    for k, i in enumerate(idx):
        a = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts.append(a if k == 0 else a[1:])
    return np.concatenate(pts)


def features(file, obj):
    """{nome: [anelli lon/lat]} per un oggetto TopoJSON (Polygon e MultiPolygon)."""
    topo = _topo(file)
    arcs = _arcs(topo)
    out = {}
    for g in topo["objects"][obj]["geometries"]:
        polys = g.get("arcs", [])
        if g["type"] == "Polygon":
            polys = [polys]
        elif g["type"] != "MultiPolygon":
            continue
        name = (g.get("properties") or {}).get("name") or g.get("id") or obj
        out.setdefault(name, []).extend(_ring(arcs, r) for p in polys for r in p)
    return out


class Projection:
    """Ortografica centrata sull'origine: vicino al centro è un piano in metri, lontano diventa il globo."""

    def __init__(self, lat0, lon0):
        self.lat0, self.lon0 = lat0, lon0
        self.p0, self.l0 = math.radians(lat0), math.radians(lon0)

    def xy(self, lon, lat):
        """(lon, lat) in gradi -> (x, y) in metri e visibilità (cos c > 0 = emisfero visibile)."""
        lam = np.radians(lon) - self.l0
        phi = np.radians(lat)
        x = R_EARTH * np.cos(phi) * np.sin(lam)
        y = R_EARTH * (math.cos(self.p0) * np.sin(phi) - math.sin(self.p0) * np.cos(phi) * np.cos(lam))
        cosc = math.sin(self.p0) * np.sin(phi) + math.cos(self.p0) * np.cos(phi) * np.cos(lam)
        return x, y, cosc

    def point(self, lat, lon):
        x, y, _ = self.xy(np.array([lon]), np.array([lat]))
        return float(x[0]), float(y[0])

    def path(self, rings):
        """Path skia in metri (y verso nord). I punti dietro il globo finiscono sul bordo."""
        p = skia.Path()
        p.setFillType(skia.PathFillType.kEvenOdd)
        for ring in rings:
            x, y, cosc = self.xy(ring[:, 0], ring[:, 1])
            if (cosc <= 0).all():
                continue
            back = cosc <= 0
            if back.any():
                r = np.hypot(x, y)
                x = np.where(back, x / r * R_EARTH, x)
                y = np.where(back, y / r * R_EARTH, y)
            p.addPoly([skia.Point(float(a), float(b)) for a, b in zip(x, y)], True)
        return p


def distance_km(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dl = np.radians(lon2) - np.radians(lon1)
    c = np.sin(p1) * np.sin(p2) + np.cos(p1) * np.cos(p2) * np.cos(dl)
    return R_EARTH / 1000 * np.arccos(np.clip(c, -1, 1))


class Atlas:
    """Path proiettati per una storia: terre, laghi grandi, paesi, stati USA, e i puntini luminosi che si accendono."""

    def __init__(self, lat0, lon0, seed=7):
        self.proj = Projection(lat0, lon0)
        countries = features("countries-50m.json", "countries")
        self.countries = {k: self.proj.path(v) for k, v in countries.items()}
        self.land = self.proj.path(features("countries-50m.json", "land")["land"])
        self.states = {k: self.proj.path(v) for k, v in features("us-states-10m.json", "states").items()}
        rings = json.loads((GEO_DIR / "lakes-major.json").read_text())["rings"]
        self.lakes = self.proj.path([np.asarray(r, float) for r in rings])
        self.dots = self._dots(seed)

    def _dots(self, seed, per_scale=700):
        """Puntini su terra a densità decrescente con la distanza: a ogni zoom lo schermo ne ha più o meno
        lo stesso numero. Restituisce (punti skia, distanza dall'origine in km) ordinati per distanza."""
        rng = np.random.default_rng(seed)
        pts, dist = [], []
        for r_km in (2, 6, 20, 60, 200, 600, 2000, 6000):
            n = 0
            while n < per_scale:
                rr = r_km * 1000 * np.sqrt(rng.random(per_scale))
                th = rng.random(per_scale) * 2 * np.pi
                x, y = rr * np.cos(th), rr * np.sin(th)
                for a, b in zip(x, y):
                    if (n < per_scale and self.land.contains(float(a), float(b))
                            and not self.lakes.contains(float(a), float(b))):
                        pts.append((a, b))
                        dist.append(math.hypot(a, b) / 1000)
                        n += 1
        order = np.argsort(dist)
        return [skia.Point(float(pts[i][0]), float(pts[i][1])) for i in order], np.asarray(dist)[order]

    def at(self, lat, lon):
        return self.proj.point(lat, lon)
