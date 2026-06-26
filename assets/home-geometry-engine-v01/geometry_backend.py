#!/usr/bin/env python3
"""Geometry backend for the home geometry engine.

This module hides whether geometry calculations use Shapely or the lightweight
built-in fallback. Business rules should call this module instead of importing
Shapely directly.
"""

from __future__ import annotations

import math

Point = tuple[float, float]
EPS = 1e-9

try:
    from shapely.geometry import LineString as _ShapelyLineString
    from shapely.geometry import Point as _ShapelyPoint
    from shapely.geometry import Polygon as _ShapelyPolygon
except ImportError:  # Shapely is optional.
    _ShapelyLineString = None
    _ShapelyPoint = None
    _ShapelyPolygon = None

BACKEND = "shapely" if _ShapelyLineString else "builtin"


def as_point(value: list[float] | tuple[float, float]) -> Point:
    return (float(value[0]), float(value[1]))


def sub(a: Point, b: Point) -> Point:
    return (a[0] - b[0], a[1] - b[1])


def dot(a: Point, b: Point) -> float:
    return a[0] * b[0] + a[1] * b[1]


def cross(a: Point, b: Point) -> float:
    return a[0] * b[1] - a[1] * b[0]


def length(v: Point) -> float:
    return math.hypot(v[0], v[1])


def distance(a: Point, b: Point) -> float:
    return length(sub(a, b))


def point_segment_distance(p: Point, a: Point, b: Point) -> float:
    if _ShapelyLineString and _ShapelyPoint:
        return float(_ShapelyLineString([a, b]).distance(_ShapelyPoint(p)))
    ab = sub(b, a)
    denom = dot(ab, ab)
    if denom < EPS:
        return distance(p, a)
    t = max(0.0, min(1.0, dot(sub(p, a), ab) / denom))
    closest = (a[0] + ab[0] * t, a[1] + ab[1] * t)
    return distance(p, closest)


def point_segment_param(p: Point, a: Point, b: Point) -> float:
    ab = sub(b, a)
    denom = dot(ab, ab)
    if denom < EPS:
        return 0.0
    return dot(sub(p, a), ab) / denom


def segment_intersection(a1: Point, a2: Point, b1: Point, b2: Point) -> Point | None:
    if _ShapelyLineString:
        inter = _ShapelyLineString([a1, a2]).intersection(_ShapelyLineString([b1, b2]))
        if inter.is_empty:
            return None
        if inter.geom_type == "Point":
            return (float(inter.x), float(inter.y))
        return None
    r = sub(a2, a1)
    s = sub(b2, b1)
    denom = cross(r, s)
    if abs(denom) < EPS:
        return None
    qp = sub(b1, a1)
    t = cross(qp, s) / denom
    u = cross(qp, r) / denom
    if -EPS <= t <= 1.0 + EPS and -EPS <= u <= 1.0 + EPS:
        return (a1[0] + t * r[0], a1[1] + t * r[1])
    return None


def segment_to_segment_distance(a1: Point, a2: Point, b1: Point, b2: Point) -> float:
    if _ShapelyLineString:
        return float(_ShapelyLineString([a1, a2]).distance(_ShapelyLineString([b1, b2])))
    if segment_intersection(a1, a2, b1, b2):
        return 0.0
    return min(
        point_segment_distance(a1, b1, b2),
        point_segment_distance(a2, b1, b2),
        point_segment_distance(b1, a1, a2),
        point_segment_distance(b2, a1, a2),
    )


def polygon_area(points: list[Point]) -> float:
    if len(points) < 3:
        return 0.0
    if _ShapelyPolygon:
        return float(abs(_ShapelyPolygon(points).area))
    total = 0.0
    for a, b in segments_from_polygon(points):
        total += a[0] * b[1] - b[0] * a[1]
    return abs(total) / 2.0


def polygon_centroid(points: list[Point]) -> Point:
    if not points:
        return (0.0, 0.0)
    if _ShapelyPolygon and len(points) >= 3:
        centroid = _ShapelyPolygon(points).centroid
        return (float(centroid.x), float(centroid.y))
    return (sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points))


def segments_from_polygon(points: list[Point]) -> list[tuple[Point, Point]]:
    return list(zip(points, points[1:] + points[:1]))


def rect_corners(center: Point, size: Point, rotation_degrees: float) -> list[Point]:
    cx, cy = center
    w, h = size
    rad = math.radians(rotation_degrees)
    cos_r = math.cos(rad)
    sin_r = math.sin(rad)
    local = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    return [(cx + x * cos_r - y * sin_r, cy + x * sin_r + y * cos_r) for x, y in local]
