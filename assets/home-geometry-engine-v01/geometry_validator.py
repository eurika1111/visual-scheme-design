#!/usr/bin/env python3
"""Lightweight home geometry validator.

Coordinate convention:
- origin: lower-left
- X axis: right
- Y axis: up
- unit: millimeters

This is a validator, not a CAD engine. It checks object data produced by AI or
manual editing and reports whether the data is safe enough for concept design.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

from geometry_backend import (
    BACKEND as GEOMETRY_BACKEND,
    EPS,
    Point,
    as_point,
    cross,
    dot,
    distance,
    length,
    point_segment_distance,
    point_segment_param,
    polygon_area,
    polygon_centroid,
    rect_corners,
    segment_intersection,
    segment_to_segment_distance,
    segments_from_polygon,
    sub,
)


def segment_length(seg: dict[str, Any]) -> float:
    return distance(as_point(seg["start"]), as_point(seg["end"]))


def arc_points(geom: dict[str, Any], max_degrees: float = 10.0) -> list[Point]:
    center = as_point(geom["center"])
    radius = float(geom["radius"])
    start_angle = float(geom["start_angle"])
    end_angle = float(geom["end_angle"])
    sweep = end_angle - start_angle
    steps = max(4, int(math.ceil(abs(sweep) / max_degrees)))
    points = []
    for index in range(steps + 1):
        angle = math.radians(start_angle + sweep * index / steps)
        points.append((center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle)))
    return points


def wall_geometry_errors(wall: dict[str, Any], duplicate_tolerance: float) -> list[dict[str, Any]]:
    wall_id = wall.get("id", "<missing>")
    geom = wall.get("geometry", {})
    kind = geom.get("kind")
    if kind == "line":
        if segment_length(geom) <= duplicate_tolerance:
            return [{"type": "zero_length_wall", "object_id": wall_id}]
        return []
    if kind == "arc":
        required = ["center", "radius", "start_angle", "end_angle", "thickness"]
        missing = [key for key in required if key not in geom]
        if missing:
            return [{"type": "arc_wall_incomplete", "object_id": wall_id, "missing": missing}]
        radius = float(geom.get("radius", 0))
        sweep = abs(float(geom.get("end_angle", 0)) - float(geom.get("start_angle", 0)))
        if radius <= duplicate_tolerance:
            return [{"type": "arc_wall_invalid", "object_id": wall_id, "message": "Arc wall radius is too small"}]
        if sweep <= 1:
            return [{"type": "arc_wall_invalid", "object_id": wall_id, "message": "Arc wall sweep is too small"}]
        return []
    return [{"type": "unsupported_wall_geometry", "object_id": wall_id}]


def wall_line_segments(wall: dict[str, Any]) -> list[dict[str, Any]]:
    geom = wall.get("geometry", {})
    if geom.get("kind") == "line":
        return [wall]
    if geom.get("kind") != "arc":
        return []
    try:
        points = arc_points(geom)
    except (KeyError, TypeError, ValueError):
        return []
    segments = []
    for index, (start, end) in enumerate(zip(points, points[1:]), start=1):
        segment = {**wall}
        segment["id"] = f"{wall.get('id', 'ARC')}#S{index:02d}"
        segment["source_wall_id"] = wall.get("id")
        segment["geometry"] = {
            "kind": "line",
            "start": [start[0], start[1]],
            "end": [end[0], end[1]],
            "thickness": geom.get("thickness", 100),
        }
        segments.append(segment)
    return segments


def angle_between(a1: Point, a2: Point, b1: Point, b2: Point) -> float:
    va = sub(a2, a1)
    vb = sub(b2, b1)
    la = length(va)
    lb = length(vb)
    if la < EPS or lb < EPS:
        return 0.0
    value = max(-1.0, min(1.0, abs(dot(va, vb)) / (la * lb)))
    acute = math.degrees(math.acos(value))
    return round(acute, 3)


def is_near_endpoint(p: Point, a: Point, b: Point, tolerance: float) -> bool:
    return distance(p, a) <= tolerance or distance(p, b) <= tolerance


def is_inside_segment_not_endpoint(p: Point, a: Point, b: Point, tolerance: float) -> bool:
    return point_segment_distance(p, a, b) <= tolerance and not is_near_endpoint(p, a, b, tolerance)


def classify_wall_junction(w1: dict[str, Any], w2: dict[str, Any], tolerance: float) -> dict[str, Any] | None:
    a1 = as_point(w1["geometry"]["start"])
    a2 = as_point(w1["geometry"]["end"])
    b1 = as_point(w2["geometry"]["start"])
    b2 = as_point(w2["geometry"]["end"])
    point = segment_intersection(a1, a2, b1, b2)
    angle = angle_between(a1, a2, b1, b2)

    if point:
        a_endpoint = is_near_endpoint(point, a1, a2, tolerance)
        b_endpoint = is_near_endpoint(point, b1, b2, tolerance)
        if not a_endpoint and not b_endpoint:
            kind = "cross_junction"
        elif a_endpoint and b_endpoint:
            kind = "endpoint_junction"
        else:
            kind = "t_junction"
        return {
            "type": kind,
            "members": [w1["id"], w2["id"]],
            "point": [round(point[0], 3), round(point[1], 3)],
            "angle_degrees": angle,
            "status": "valid",
        }

    endpoint_pairs = [
        (a1, b1),
        (a1, b2),
        (a2, b1),
        (a2, b2),
    ]
    nearest = min(endpoint_pairs, key=lambda pair: distance(pair[0], pair[1]))
    nearest_distance = distance(nearest[0], nearest[1])
    if nearest_distance <= EPS:
        return {
            "type": "endpoint_junction",
            "members": [w1["id"], w2["id"]],
            "point": [round(nearest[0][0], 3), round(nearest[0][1], 3)],
            "angle_degrees": angle,
            "status": "valid",
        }
    if nearest_distance <= tolerance:
        mid = ((nearest[0][0] + nearest[1][0]) / 2, (nearest[0][1] + nearest[1][1]) / 2)
        return {
            "type": "near_miss",
            "members": [w1["id"], w2["id"]],
            "point": [round(mid[0], 3), round(mid[1], 3)],
            "distance_mm": round(nearest_distance, 3),
            "angle_degrees": angle,
            "status": "warning",
            "suggestion": "snap_required",
        }

    return None


def are_collinear(a1: Point, a2: Point, b1: Point, b2: Point, tolerance: float) -> bool:
    line_len = distance(a1, a2)
    if line_len < EPS:
        return False
    return (
        point_segment_distance(b1, a1, a2) <= tolerance
        and point_segment_distance(b2, a1, a2) <= tolerance
    )


def projection_range(a: Point, b: Point, p1: Point, p2: Point) -> tuple[float, float]:
    ab = sub(b, a)
    denom = dot(ab, ab)
    if denom < EPS:
        return (0.0, 0.0)
    t1 = dot(sub(p1, a), ab) / denom
    t2 = dot(sub(p2, a), ab) / denom
    return (min(t1, t2), max(t1, t2))


def find_overlapping_walls(walls: list[dict[str, Any]], tolerance: float) -> list[dict[str, Any]]:
    overlaps = []
    for i, w1 in enumerate(walls):
        a1 = as_point(w1["geometry"]["start"])
        a2 = as_point(w1["geometry"]["end"])
        for w2 in walls[i + 1 :]:
            b1 = as_point(w2["geometry"]["start"])
            b2 = as_point(w2["geometry"]["end"])
            if not are_collinear(a1, a2, b1, b2, tolerance):
                continue
            r1 = projection_range(a1, a2, a1, a2)
            r2 = projection_range(a1, a2, b1, b2)
            overlap = min(r1[1], r2[1]) - max(r1[0], r2[0])
            if overlap > 0.05:
                overlaps.append({
                    "members": [w1["id"], w2["id"]],
                    "type": "overlapping_or_duplicate_wall",
                    "status": "error",
                })
    return overlaps


def bind_opening(opening: dict[str, Any], walls: list[dict[str, Any]], tolerance: float) -> dict[str, Any]:
    pos = as_point(opening["position"])
    host_id = opening.get("host_wall_id")
    candidates = []
    for wall in walls:
        a = as_point(wall["geometry"]["start"])
        b = as_point(wall["geometry"]["end"])
        dist = point_segment_distance(pos, a, b)
        if dist <= tolerance:
            candidates.append((wall["id"], dist))

    if host_id:
        matching = [item for item in candidates if item[0] == host_id]
        if matching:
            return {
                "opening_id": opening["id"],
                "host_wall_id": host_id,
                "status": "valid",
                "distance_mm": round(matching[0][1], 3),
            }
        return {
            "opening_id": opening["id"],
            "host_wall_id": host_id,
            "status": "error",
            "message": "Declared host wall does not contain opening position",
            "candidate_hosts": [c[0] for c in candidates],
        }

    if len(candidates) == 1:
        return {
            "opening_id": opening["id"],
            "host_wall_id": candidates[0][0],
            "status": "valid",
            "distance_mm": round(candidates[0][1], 3),
        }
    if not candidates:
        return {
            "opening_id": opening["id"],
            "status": "error",
            "message": "Opening is not close to any wall",
        }
    return {
        "opening_id": opening["id"],
        "status": "warning",
        "message": "Opening is close to more than one wall",
        "candidate_hosts": [c[0] for c in candidates],
    }

def point_almost_equal(a: Point, b: Point, tolerance: float) -> bool:
    return distance(a, b) <= tolerance


def unit_wall_vector(wall: dict[str, Any]) -> Point:
    geom = wall["geometry"]
    a = as_point(geom["start"])
    b = as_point(geom["end"])
    wall_len = distance(a, b)
    if wall_len < EPS:
        return (1.0, 0.0)
    return ((b[0] - a[0]) / wall_len, (b[1] - a[1]) / wall_len)


def rotate_vector(v: Point, degrees: float) -> Point:
    rad = math.radians(degrees)
    c = math.cos(rad)
    s = math.sin(rad)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)


def door_leaf_segments(opening: dict[str, Any], host_wall: dict[str, Any]) -> dict[str, Any] | None:
    if opening.get("type") != "door" or not opening.get("swing"):
        return None

    width = float(opening.get("width", 0))
    if width <= 0:
        return None

    geom = host_wall["geometry"]
    wall_start = as_point(geom["start"])
    wall_end = as_point(geom["end"])
    wall_len = distance(wall_start, wall_end)
    if wall_len < EPS:
        return None

    u = unit_wall_vector(host_wall)
    center_param = max(0.0, min(1.0, point_segment_param(as_point(opening["position"]), wall_start, wall_end)))
    center_dist = center_param * wall_len
    start_dist = max(0.0, center_dist - width / 2)
    end_dist = min(wall_len, center_dist + width / 2)
    p1 = (wall_start[0] + u[0] * start_dist, wall_start[1] + u[1] * start_dist)
    p2 = (wall_start[0] + u[0] * end_dist, wall_start[1] + u[1] * end_dist)

    hinge = p1 if opening.get("swing", {}).get("hinge", "left") == "left" else p2
    closed_end = p2 if hinge == p1 else p1
    closed_vec = sub(closed_end, hinge)
    direction = opening.get("swing", {}).get("direction", "inward")
    sign = 1 if direction == "inward" else -1

    samples = []
    for angle in [15, 30, 45, 60, 75, 90]:
        leaf = rotate_vector(closed_vec, sign * angle)
        endpoint = (hinge[0] + leaf[0], hinge[1] + leaf[1])
        samples.append({"angle": angle, "segment": (hinge, endpoint)})

    return {
        "hinge": hinge,
        "closed_end": closed_end,
        "open_end_90": samples[-1]["segment"][1] if samples else closed_end,
        "samples": samples,
        "assumption": "direction uses left-normal for inward and right-normal for outward relative to host wall order",
    }


def door_swing_collision_checks(
    openings: list[dict[str, Any]],
    walls: list[dict[str, Any]],
    furniture_items: list[dict[str, Any]],
    tolerance: float,
) -> list[dict[str, Any]]:
    wall_by_id = {wall.get("id"): wall for wall in walls}
    reports = []
    for opening in openings:
        if opening.get("type") != "door":
            continue
        host_id = opening.get("host_wall_id")
        host_wall = wall_by_id.get(host_id)
        if host_wall:
            hg = host_wall.get("geometry", {})
            if point_segment_distance(as_point(opening["position"]), as_point(hg["start"]), as_point(hg["end"])) > tolerance:
                reports.append({
                    "door_id": opening.get("id"),
                    "host_wall_id": host_id,
                    "status": "warning",
                    "message": "Door position is not on declared host wall; swing not checked",
                })
                continue
        swing = door_leaf_segments(opening, host_wall) if host_wall else None
        if not swing:
            reports.append({
                "door_id": opening.get("id"),
                "host_wall_id": host_id,
                "status": "warning",
                "message": "Door swing data is incomplete or host wall is unavailable",
            })
            continue

        wall_hits: set[str] = set()
        furniture_hits: set[str] = set()
        for sample in swing["samples"]:
            leaf_start, leaf_end = sample["segment"]
            for wall in walls:
                if wall.get("id") == host_id:
                    continue
                geom = wall.get("geometry", {})
                if geom.get("kind") != "line":
                    continue
                w1 = as_point(geom["start"])
                w2 = as_point(geom["end"])
                hit = segment_intersection(leaf_start, leaf_end, w1, w2)
                if hit and not point_almost_equal(hit, leaf_start, tolerance):
                    wall_hits.add(wall.get("id", "<missing>"))
            for item in furniture_items:
                geom = item.get("geometry", {})
                if geom.get("kind") != "rect":
                    continue
                corners = rect_corners(as_point(geom["center"]), as_point(geom["size"]), float(geom.get("rotation", 0)))
                for e1, e2 in segments_from_polygon(corners):
                    hit = segment_intersection(leaf_start, leaf_end, e1, e2)
                    if hit:
                        furniture_hits.add(item.get("id", "<missing>"))
                        break

        status = "valid" if not wall_hits and not furniture_hits else "warning"
        reports.append({
            "door_id": opening.get("id"),
            "host_wall_id": host_id,
            "status": status,
            "hinge": [round(v, 3) for v in swing["hinge"]],
            "closed_end": [round(v, 3) for v in swing["closed_end"]],
            "open_end_90": [round(v, 3) for v in swing["open_end_90"]],
            "collides_with_walls": sorted(wall_hits),
            "collides_with_furniture": sorted(furniture_hits),
            "assumption": swing["assumption"],
        })
    return reports

def room_boundary_checks(room: dict[str, Any], walls: list[dict[str, Any]], tolerance: float) -> list[dict[str, Any]]:
    warnings, _ = analyze_room_boundaries(room, walls, tolerance)
    return warnings


def edge_wall_coverage(a: Point, b: Point, walls: list[dict[str, Any]], tolerance: float) -> dict[str, Any]:
    edge = sub(b, a)
    edge_len = length(edge)
    if edge_len < EPS:
        return {"coverage": 0.0, "wall_ids": []}

    intervals: list[tuple[float, float]] = []
    wall_ids: list[str] = []
    for wall in walls:
        geom = wall.get("geometry", {})
        if geom.get("kind") != "line":
            continue
        w1 = as_point(geom["start"])
        w2 = as_point(geom["end"])
        if segment_to_segment_distance(a, b, w1, w2) > tolerance:
            continue
        if abs(cross(edge, sub(w1, a))) > tolerance * edge_len:
            continue
        if abs(cross(edge, sub(w2, a))) > tolerance * edge_len:
            continue
        t1 = max(0.0, min(1.0, point_segment_param(w1, a, b)))
        t2 = max(0.0, min(1.0, point_segment_param(w2, a, b)))
        start, end = min(t1, t2), max(t1, t2)
        if end - start <= EPS:
            continue
        intervals.append((start, end))
        wall_ids.append(wall.get("id", "<missing>"))

    if not intervals:
        return {"coverage": 0.0, "wall_ids": []}

    intervals.sort()
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end + EPS:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))

    return {
        "coverage": min(1.0, sum(end - start for start, end in merged)),
        "wall_ids": sorted(set(wall_ids)),
    }


def analyze_room_boundaries(
    room: dict[str, Any],
    walls: list[dict[str, Any]],
    tolerance: float,
    min_coverage: float = 0.8,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    points = [as_point(p) for p in room.get("polygon", [])]
    warnings = []
    edge_reports = []
    if len(points) < 3:
        return ([{"type": "room_invalid_polygon", "room_id": room.get("id"), "message": "Room polygon needs at least 3 points"}], [])

    open_edges = set(room.get("open_edges", []))
    for index, (a, b) in enumerate(segments_from_polygon(points)):
        nearest = None
        nearest_distance = float("inf")
        for wall in walls:
            geom = wall.get("geometry", {})
            if geom.get("kind") != "line":
                continue
            w1 = as_point(geom["start"])
            w2 = as_point(geom["end"])
            dist = segment_to_segment_distance(a, b, w1, w2)
            if dist < nearest_distance:
                nearest_distance = dist
                nearest = wall.get("id")
        coverage_report = edge_wall_coverage(a, b, walls, tolerance)
        is_open_edge = index in open_edges
        edge_reports.append({
            "edge_index": index,
            "nearest_wall_id": nearest,
            "nearest_distance_mm": round(nearest_distance, 3),
            "wall_coverage": round(coverage_report["coverage"], 3),
            "supporting_wall_ids": coverage_report["wall_ids"],
            "open_edge": is_open_edge,
        })
        if nearest_distance > tolerance:
            warnings.append({
                "type": "room_edge_off_wall",
                "room_id": room.get("id"),
                "edge_index": index,
                "nearest_wall_id": nearest,
                "distance_mm": round(nearest_distance, 3),
                "message": "Room boundary edge is not close to any wall",
            })
        elif not is_open_edge and coverage_report["coverage"] < min_coverage:
            warnings.append({
                "type": "room_edge_under_supported",
                "room_id": room.get("id"),
                "edge_index": index,
                "wall_coverage": round(coverage_report["coverage"], 3),
                "supporting_wall_ids": coverage_report["wall_ids"],
                "message": "Room boundary edge is only partially supported by walls",
            })
    return warnings, edge_reports

def validate_rooms(rooms: list[dict[str, Any]], walls: list[dict[str, Any]], tolerance: float) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    errors = []
    warnings = []
    room_reports = []
    for room in rooms:
        room_id = room.get("id", "<missing>")
        points = [as_point(p) for p in room.get("polygon", [])]
        if len(points) < 3:
            errors.append({"type": "room_invalid_polygon", "room_id": room_id, "message": "Room polygon needs at least 3 points"})
            continue

        area_mm2 = polygon_area(points)
        area_sqm = area_mm2 / 1_000_000
        label = room.get("area_label_sqm")
        area_delta = None
        if label is not None:
            area_delta = area_sqm - float(label)
            if abs(area_delta) > 0.5:
                warnings.append({
                    "type": "room_area_mismatch",
                    "room_id": room_id,
                    "computed_area_sqm": round(area_sqm, 3),
                    "area_label_sqm": label,
                    "delta_sqm": round(area_delta, 3),
                    "message": "Computed room area differs from label by more than 0.5 sqm",
                })

        boundary_warnings, boundary_reports = analyze_room_boundaries(room, walls, tolerance)
        warnings.extend(boundary_warnings)
        room_reports.append({
            "room_id": room_id,
            "computed_area_sqm": round(area_sqm, 3),
            "area_label_sqm": label,
            "area_delta_sqm": round(area_delta, 3) if area_delta is not None else None,
            "centroid": [round(v, 3) for v in polygon_centroid(points)],
            "boundary_edges": boundary_reports,
        })
    return errors, warnings, room_reports


def furniture_wall_collisions(furniture: dict[str, Any], walls: list[dict[str, Any]]) -> list[str]:
    geom = furniture["geometry"]
    corners = rect_corners(as_point(geom["center"]), as_point(geom["size"]), float(geom.get("rotation", 0)))
    edges = segments_from_polygon(corners)
    hits: list[str] = []
    for wall in walls:
        a = as_point(wall["geometry"]["start"])
        b = as_point(wall["geometry"]["end"])
        for e1, e2 in edges:
            if segment_intersection(e1, e2, a, b):
                hits.append(wall["id"])
                break
    return sorted(set(hits))

def polygon_edges_intersect(poly_a: list[Point], poly_b: list[Point]) -> bool:
    for a1, a2 in segments_from_polygon(poly_a):
        for b1, b2 in segments_from_polygon(poly_b):
            if segment_intersection(a1, a2, b1, b2):
                return True
    return False


def point_in_polygon(point: Point, polygon: list[Point]) -> bool:
    x, y = point
    inside = False
    j = len(polygon) - 1
    for i, pi in enumerate(polygon):
        xi, yi = pi
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) or EPS) + xi):
            inside = not inside
        j = i
    return inside


def polygons_overlap(poly_a: list[Point], poly_b: list[Point]) -> bool:
    return (
        polygon_edges_intersect(poly_a, poly_b)
        or point_in_polygon(poly_a[0], poly_b)
        or point_in_polygon(poly_b[0], poly_a)
    )


def polygon_distance(poly_a: list[Point], poly_b: list[Point]) -> float:
    if polygons_overlap(poly_a, poly_b):
        return 0.0
    best = float("inf")
    for a1, a2 in segments_from_polygon(poly_a):
        for b1, b2 in segments_from_polygon(poly_b):
            best = min(best, segment_to_segment_distance(a1, a2, b1, b2))
    return best


def furniture_polygon(item: dict[str, Any]) -> list[Point] | None:
    geom = item.get("geometry", {})
    if geom.get("kind") != "rect":
        return None
    return rect_corners(as_point(geom["center"]), as_point(geom["size"]), float(geom.get("rotation", 0)))


def furniture_pair_checks(furniture_items: list[dict[str, Any]], default_clearance: float) -> list[dict[str, Any]]:
    reports = []
    for i, item_a in enumerate(furniture_items):
        poly_a = furniture_polygon(item_a)
        if not poly_a:
            continue
        for item_b in furniture_items[i + 1:]:
            poly_b = furniture_polygon(item_b)
            if not poly_b:
                continue
            dist = polygon_distance(poly_a, poly_b)
            required = max(
                float(item_a.get("clearance_mm", default_clearance)),
                float(item_b.get("clearance_mm", default_clearance)),
            )
            if dist <= EPS:
                status = "collision"
            elif dist < required:
                status = "clearance_warning"
            else:
                status = "valid"
            reports.append({
                "furniture_ids": [item_a.get("id"), item_b.get("id")],
                "status": status,
                "distance_mm": round(dist, 3),
                "required_clearance_mm": round(required, 3),
            })
    return reports


KITCHEN_WORK_CATEGORIES = {
    "base_cabinet",
    "cabinet",
    "countertop",
    "fridge",
    "kitchen_island",
    "sink_cabinet",
    "stove",
}


def kitchen_workflow_checks(furniture_items: list[dict[str, Any]], default_clearance: float) -> list[dict[str, Any]]:
    kitchen_items = [item for item in furniture_items if item.get("category") in KITCHEN_WORK_CATEGORIES]
    reports = []
    for i, item_a in enumerate(kitchen_items):
        poly_a = furniture_polygon(item_a)
        if not poly_a:
            continue
        for item_b in kitchen_items[i + 1:]:
            poly_b = furniture_polygon(item_b)
            if not poly_b:
                continue
            dist = polygon_distance(poly_a, poly_b)
            required = max(
                float(item_a.get("work_clearance_mm", default_clearance)),
                float(item_b.get("work_clearance_mm", default_clearance)),
            )
            if dist <= EPS:
                status = "collision"
            elif dist < required:
                status = "clearance_warning"
            else:
                status = "valid"
            reports.append({
                "furniture_ids": [item_a.get("id"), item_b.get("id")],
                "categories": [item_a.get("category"), item_b.get("category")],
                "status": status,
                "distance_mm": round(dist, 3),
                "required_clearance_mm": round(required, 3),
            })
    return reports


def door_swing_clearance_checks(
    door_swing_checks: list[dict[str, Any]],
    furniture_items: list[dict[str, Any]],
    default_clearance: float,
) -> list[dict[str, Any]]:
    reports = []
    furniture_polys = [(item, furniture_polygon(item)) for item in furniture_items]
    for swing in door_swing_checks:
        if "hinge" not in swing or "open_end_90" not in swing:
            continue
        hinge = as_point(swing["hinge"])
        open_end = as_point(swing["open_end_90"])
        for item, poly in furniture_polys:
            if not poly:
                continue
            dist = min(segment_to_segment_distance(hinge, open_end, a, b) for a, b in segments_from_polygon(poly))
            required = float(item.get("door_clearance_mm", default_clearance))
            if dist < required:
                reports.append({
                    "door_id": swing.get("door_id"),
                    "furniture_id": item.get("id"),
                    "status": "clearance_warning",
                    "distance_mm": round(dist, 3),
                    "required_clearance_mm": round(required, 3),
                })
    return reports
def segment_polygon_distance(a: Point, b: Point, polygon: list[Point]) -> float:
    if any(segment_intersection(a, b, e1, e2) for e1, e2 in segments_from_polygon(polygon)):
        return 0.0
    return min(segment_to_segment_distance(a, b, e1, e2) for e1, e2 in segments_from_polygon(polygon))


def circulation_path_checks(
    paths: list[dict[str, Any]],
    walls: list[dict[str, Any]],
    furniture_items: list[dict[str, Any]],
    default_width: float,
) -> list[dict[str, Any]]:
    reports = []
    furniture_polys = [(item, furniture_polygon(item)) for item in furniture_items]
    for path in paths:
        start = as_point(path["start"])
        end = as_point(path["end"])
        required_width = float(path.get("required_width_mm", default_width))
        min_clearance = required_width / 2
        wall_hits = []
        furniture_hits = []

        for wall in walls:
            geom = wall.get("geometry", {})
            if geom.get("kind") != "line":
                continue
            dist = segment_to_segment_distance(start, end, as_point(geom["start"]), as_point(geom["end"]))
            if dist < min_clearance:
                wall_hits.append({"wall_id": wall.get("id"), "distance_mm": round(dist, 3)})

        for item, poly in furniture_polys:
            if not poly:
                continue
            dist = segment_polygon_distance(start, end, poly)
            if dist < min_clearance:
                furniture_hits.append({"furniture_id": item.get("id"), "distance_mm": round(dist, 3)})

        status = "valid" if not wall_hits and not furniture_hits else "warning"
        reports.append({
            "path_id": path.get("id"),
            "status": status,
            "start": [round(v, 3) for v in start],
            "end": [round(v, 3) for v in end],
            "required_width_mm": round(required_width, 3),
            "collides_or_too_close_walls": wall_hits,
            "collides_or_too_close_furniture": furniture_hits,
        })
    return reports

def recommend_readiness(errors: list[dict[str, Any]], warnings: list[dict[str, Any]], model: dict[str, Any]) -> str:
    if errors:
        return "L0"
    all_walls = model.get("walls", [])
    walls = [wall for wall in all_walls if wall.get("status") != "demolished"]
    openings = model.get("openings", [])
    if len(walls) < 4:
        return "L1"
    if warnings:
        return "L2"
    if openings and model.get("rooms"):
        return "L3"
    return "L2"


def validate(model: dict[str, Any]) -> dict[str, Any]:
    tolerance_cfg = model.get("tolerance", {})
    snap = float(tolerance_cfg.get("snap_mm", 30))
    host_wall = float(tolerance_cfg.get("host_wall_mm", 40))
    duplicate = float(tolerance_cfg.get("duplicate_mm", 10))
    swing_tolerance = float(tolerance_cfg.get("door_swing_mm", 20))
    furniture_clearance = float(tolerance_cfg.get("furniture_clearance_mm", 100))
    door_clearance = float(tolerance_cfg.get("door_clearance_mm", 50))
    circulation_width = float(tolerance_cfg.get("circulation_width_mm", 800))
    kitchen_work_clearance = float(tolerance_cfg.get("kitchen_work_clearance_mm", 900))

    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    all_walls = model.get("walls", [])
    active_walls = [wall for wall in all_walls if wall.get("status") != "demolished"]
    walls: list[dict[str, Any]] = []
    openings = model.get("openings", [])
    furniture_items = model.get("furniture", [])
    rooms = model.get("rooms", [])
    circulation_paths = model.get("circulation_paths", [])

    if model.get("coordinate_system", {}).get("origin") != "lower_left":
        errors.append({
            "type": "coordinate_system_error",
            "message": "coordinate_system.origin must be lower_left",
        })

    wall_ids = set()
    for wall in active_walls:
        wall_id = wall.get("id", "<missing>")
        if wall_id in wall_ids:
            errors.append({"type": "duplicate_id", "object_id": wall_id})
        wall_ids.add(wall_id)
        wall_errors = wall_geometry_errors(wall, duplicate)
        errors.extend(wall_errors)
        if not wall_errors:
            walls.extend(wall_line_segments(wall))

    for item in find_overlapping_walls(walls, duplicate):
        errors.append(item)

    junctions = []
    connected_wall_ids = set()
    for i, w1 in enumerate(walls):
        for w2 in walls[i + 1 :]:
            junction = classify_wall_junction(w1, w2, snap)
            if not junction:
                continue
            junction["id"] = f"J-{len(junctions) + 1:03d}"
            junctions.append(junction)
            if junction["type"] == "near_miss":
                warnings.append({
                    "type": "wall_near_miss",
                    "members": junction["members"],
                    "distance_mm": junction.get("distance_mm"),
                    "message": "Two wall endpoints are close but not actually connected",
                })
            else:
                connected_wall_ids.update(junction["members"])

    for wall in walls:
        if wall.get("id") not in connected_wall_ids and len(walls) > 1:
            warnings.append({
                "type": "isolated_wall",
                "object_id": wall.get("id"),
                "message": "Wall has no detected junctions",
            })

    opening_bindings = [bind_opening(opening, walls, host_wall) for opening in openings]
    for binding in opening_bindings:
        if binding["status"] == "error":
            errors.append({"type": "opening_binding_error", **binding})
        elif binding["status"] == "warning":
            warnings.append({"type": "opening_binding_warning", **binding})

    door_swing_checks = door_swing_collision_checks(openings, walls, furniture_items, swing_tolerance)
    for swing_check in door_swing_checks:
        if swing_check["status"] == "warning":
            if swing_check.get("collides_with_walls"):
                warnings.append({"type": "door_swing_wall_collision", **swing_check})
            if swing_check.get("collides_with_furniture"):
                warnings.append({"type": "door_swing_furniture_collision", **swing_check})
            if not swing_check.get("collides_with_walls") and not swing_check.get("collides_with_furniture"):
                warnings.append({"type": "door_swing_incomplete", **swing_check})

    door_clearance_checks = door_swing_clearance_checks(door_swing_checks, furniture_items, door_clearance)
    for clearance_check in door_clearance_checks:
        warnings.append({"type": "door_swing_clearance_warning", **clearance_check})

    furniture_pair_reports = furniture_pair_checks(furniture_items, furniture_clearance)
    for pair_report in furniture_pair_reports:
        if pair_report["status"] == "collision":
            warnings.append({"type": "furniture_furniture_collision", **pair_report})
        elif pair_report["status"] == "clearance_warning":
            warnings.append({"type": "furniture_clearance_warning", **pair_report})

    kitchen_workflow_reports = kitchen_workflow_checks(furniture_items, kitchen_work_clearance)
    for kitchen_report in kitchen_workflow_reports:
        if kitchen_report["status"] == "collision":
            warnings.append({"type": "kitchen_workflow_collision", **kitchen_report})
        elif kitchen_report["status"] == "clearance_warning":
            warnings.append({"type": "kitchen_workflow_clearance_warning", **kitchen_report})

    circulation_reports = circulation_path_checks(circulation_paths, walls, furniture_items, circulation_width)
    for path_report in circulation_reports:
        if path_report["status"] == "warning":
            warnings.append({"type": "circulation_width_warning", **path_report})

    furniture_checks = []
    for item in furniture_items:
        hits = furniture_wall_collisions(item, walls)
        status = "valid" if not hits else "warning"
        furniture_checks.append({
            "furniture_id": item.get("id"),
            "status": status,
            "collides_with_walls": hits,
        })
        if hits:
            warnings.append({
                "type": "furniture_wall_collision",
                "object_id": item.get("id"),
                "wall_ids": hits,
                "message": "Furniture footprint intersects wall centerline",
            })

    room_errors, room_warnings, room_reports = validate_rooms(rooms, walls, snap)
    errors.extend(room_errors)
    warnings.extend(room_warnings)

    readiness = recommend_readiness(errors, warnings, model)
    return {
        "schema_version": "home_geometry_validation_v1",
        "geometry_backend": GEOMETRY_BACKEND,
        "coordinate_system": model.get("coordinate_system"),
        "readiness": readiness,
        "can_generate_quick_concept": readiness in ["L2", "L3", "L4"],
        "can_generate_deepening": readiness in ["L3", "L4"],
        "summary": {
            "wall_count": len(all_walls),
            "active_wall_count": len(active_walls),
            "wall_segment_count": len(walls),
            "opening_count": len(openings),
            "furniture_count": len(furniture_items),
            "kitchen_object_count": len([item for item in furniture_items if item.get("category") in KITCHEN_WORK_CATEGORIES]),
            "room_count": len(rooms),
            "circulation_path_count": len(circulation_paths),
            "junction_count": len(junctions),
            "error_count": len(errors),
            "warning_count": len(warnings),
        },
        "errors": errors,
        "warnings": warnings,
        "junctions": junctions,
        "opening_bindings": opening_bindings,
        "door_swing_checks": door_swing_checks,
        "door_clearance_checks": door_clearance_checks,
        "furniture_pair_checks": furniture_pair_reports,
        "kitchen_workflow_checks": kitchen_workflow_reports,
        "circulation_checks": circulation_reports,
        "furniture_checks": furniture_checks,
        "room_checks": room_reports,
    }


def main() -> int:
    if len(sys.argv) not in [2, 3]:
        print("Usage: geometry_validator.py <base_object_model.json> [validation_output.json]")
        return 2

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) == 3 else None
    model = json.loads(input_path.read_text(encoding="utf-8-sig"))
    report = validate(model)
    output = json.dumps(report, ensure_ascii=False, indent=2)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)

    return 0 if not report["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())














