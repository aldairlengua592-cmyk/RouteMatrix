from __future__ import annotations

import html as html_lib
from dataclasses import dataclass
from datetime import datetime
from math import radians, sin, cos, asin, sqrt
from typing import Iterable
from urllib.parse import quote

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

try:
    import pydeck as pdk
except ImportError:  # Streamlit can still render a simpler map with st.map.
    pdk = None


st.set_page_config(
    page_title="RouteMatrix",
    page_icon="🗺️",
    layout="wide",
)


@dataclass(frozen=True)
class City:
    name: str
    country: str
    lat: float
    lon: float


CITIES: list[City] = [
    City("Piura", "Peru", -5.19, -80.63),
    City("Chiclayo", "Peru", -6.77, -79.84),
    City("Trujillo", "Peru", -8.11, -79.03),
    City("Iquitos", "Peru", -3.74, -73.25),
    City("Lima", "Peru", -12.05, -77.03),
    City("Cusco", "Peru", -13.53, -71.97),
    City("Puerto Maldonado", "Peru", -12.59, -69.19),
    City("Juliaca", "Peru", -15.49, -70.13),
    City("Arequipa", "Peru", -16.40, -71.54),
    City("Ciudad de Mexico", "Mexico", 19.43, -99.13),
    City("Cancun", "Mexico", 21.16, -86.85),
    City("La Habana", "Cuba", 23.13, -82.38),
    City("Belice", "Belice", 17.25, -88.77),
    City("Flores", "Guatemala", 16.93, -89.89),
    City("Ciudad de Guatemala", "Guatemala", 14.64, -90.51),
    City("San Salvador", "El Salvador", 13.69, -89.22),
    City("San Pedro Sula", "Honduras", 15.50, -88.03),
    City("Roatan", "Honduras", 16.32, -86.53),
    City("La Ceiba", "Honduras", 15.77, -86.78),
    City("Tegucigalpa", "Honduras", 14.09, -87.21),
    City("Managua", "Nicaragua", 12.13, -86.28),
    City("Liberia", "Costa Rica", 10.63, -85.44),
    City("San Jose de Costa Rica", "Costa Rica", 9.93, -84.08),
    City("Ciudad de Panama", "Panama", 8.99, -79.52),
    City("Medellin", "Colombia", 6.24, -75.58),
    City("Bogota", "Colombia", 4.71, -74.07),
    City("Cali", "Colombia", 3.45, -76.53),
    City("Quito", "Ecuador", -0.22, -78.51),
    City("Guayaquil", "Ecuador", -2.19, -79.90),
    City("Caracas", "Venezuela", 10.49, -66.88),
    City("Santo Domingo", "Republica Dominicana", 18.48, -69.96),
    City("Punta Cana", "Republica Dominicana", 18.57, -68.37),
    City("San Juan", "Puerto Rico", 18.46, -66.11),
    City("San Andres", "Colombia", 12.58, -81.71),
    City("Cartagena", "Colombia", 10.40, -75.51),
    City("Barranquilla", "Colombia", 10.96, -74.80),
    City("Santa Marta", "Colombia", 11.24, -74.20),
    City("Riohacha", "Colombia", 11.54, -72.91),
    City("Valledupar", "Colombia", 10.47, -73.25),
    City("Monteria", "Colombia", 8.75, -75.88),
    City("Cucuta", "Colombia", 7.89, -72.50),
    City("Bucaramanga", "Colombia", 7.12, -73.12),
    City("Barrancabermeja", "Colombia", 7.06, -73.85),
    City("Yopal", "Colombia", 5.35, -72.40),
    City("Villavicencio", "Colombia", 4.15, -73.64),
    City("Ibague", "Colombia", 4.44, -75.23),
    City("Neiva", "Colombia", 2.93, -75.29),
    City("Florencia", "Colombia", 1.61, -75.61),
    City("Pasto", "Colombia", 1.21, -77.28),
    City("Popayan", "Colombia", 2.44, -76.61),
    City("Pereira", "Colombia", 4.81, -75.69),
    City("Manizales", "Colombia", 5.07, -75.52),
    City("Armenia", "Colombia", 4.53, -75.68),
    City("Leticia", "Colombia", -4.19, -69.94),
    City("Tumaco", "Colombia", 1.80, -78.76),
    City("Madrid", "Espana", 40.42, -3.70),
    City("Barcelona", "Espana", 41.39, 2.16),
    City("Londres", "Reino Unido", 51.51, -0.13),
]

CITY_NAMES = [city.name for city in CITIES]
INDEX = {city.name: i for i, city in enumerate(CITIES)}
N = len(CITIES)


def crear_matriz() -> list[list[int]]:
    return [[0 for _ in range(N)] for _ in range(N)]


def conectar(matrix: list[list[int]], a: str, b: str) -> None:
    matrix[INDEX[a]][INDEX[b]] = 1


def conectar_bi(matrix: list[list[int]], a: str, b: str) -> None:
    conectar(matrix, a, b)
    conectar(matrix, b, a)


def cargar_rutas_base(matrix: list[list[int]]) -> None:
    for a, b in [
        ("Lima", "Piura"),
        ("Lima", "Chiclayo"),
        ("Lima", "Trujillo"),
        ("Lima", "Iquitos"),
        ("Lima", "Cusco"),
        ("Lima", "Arequipa"),
        ("Cusco", "Puerto Maldonado"),
        ("Lima", "Juliaca"),
        ("Cusco", "Arequipa"),
        ("Arequipa", "Juliaca"),
        ("Lima", "Bogota"),
        ("Lima", "Quito"),
        ("Lima", "Guayaquil"),
        ("Lima", "San Salvador"),
        ("Lima", "Ciudad de Panama"),
        ("Lima", "San Jose de Costa Rica"),
        ("Lima", "Ciudad de Mexico"),
        ("San Salvador", "Ciudad de Mexico"),
        ("San Salvador", "Cancun"),
        ("San Salvador", "Ciudad de Guatemala"),
        ("San Salvador", "Flores"),
        ("San Salvador", "Belice"),
        ("San Salvador", "San Pedro Sula"),
        ("San Salvador", "Roatan"),
        ("San Salvador", "La Ceiba"),
        ("San Salvador", "Tegucigalpa"),
        ("San Salvador", "Managua"),
        ("San Salvador", "Liberia"),
        ("San Salvador", "San Jose de Costa Rica"),
        ("San Salvador", "Ciudad de Panama"),
        ("San Salvador", "Bogota"),
        ("Cancun", "La Habana"),
        ("Cancun", "Belice"),
        ("San Pedro Sula", "Roatan"),
        ("San Pedro Sula", "La Ceiba"),
        ("San Pedro Sula", "Tegucigalpa"),
        ("La Ceiba", "Roatan"),
        ("Ciudad de Panama", "San Jose de Costa Rica"),
        ("Managua", "Liberia"),
        ("Bogota", "Medellin"),
        ("Bogota", "Cali"),
        ("Bogota", "Quito"),
        ("Bogota", "Guayaquil"),
        ("Bogota", "Ciudad de Panama"),
        ("Bogota", "Caracas"),
        ("Bogota", "Santo Domingo"),
        ("Bogota", "Punta Cana"),
        ("Bogota", "San Juan"),
        ("Bogota", "Madrid"),
        ("Bogota", "Barcelona"),
        ("Bogota", "Londres"),
    ]:
        conectar_bi(matrix, a, b)

    for city in [
        "San Andres",
        "Cartagena",
        "Barranquilla",
        "Santa Marta",
        "Riohacha",
        "Valledupar",
        "Monteria",
        "Cucuta",
        "Bucaramanga",
        "Barrancabermeja",
        "Yopal",
        "Villavicencio",
        "Ibague",
        "Neiva",
        "Florencia",
        "Pasto",
        "Popayan",
        "Pereira",
        "Manizales",
        "Armenia",
        "Leticia",
        "Tumaco",
    ]:
        conectar_bi(matrix, "Bogota", city)

    for city in ["San Andres", "Cartagena", "Barranquilla", "Santa Marta", "Monteria"]:
        conectar_bi(matrix, "Medellin", city)

    for city in ["Pereira", "Armenia", "Manizales", "Popayan", "Pasto", "Tumaco"]:
        conectar_bi(matrix, "Cali", city)


def rutas_directas(matrix: list[list[int]], origin: int, dest: int) -> list[list[int]]:
    return [[origin, dest]] if matrix[origin][dest] else []


def rutas_una_escala(
    matrix: list[list[int]], origin: int, dest: int
) -> list[list[int]]:
    routes = []
    for k in range(N):
        if k not in (origin, dest) and matrix[origin][k] and matrix[k][dest]:
            routes.append([origin, k, dest])
    return routes


def rutas_dos_escalas(
    matrix: list[list[int]], origin: int, dest: int
) -> list[list[int]]:
    routes = []
    for k in range(N):
        if k in (origin, dest):
            continue
        for m in range(N):
            if m in (origin, dest, k):
                continue
            if matrix[origin][k] and matrix[k][m] and matrix[m][dest]:
                routes.append([origin, k, m, dest])
    return routes


def rutas_eficientes(
    matrix: list[list[int]], origin: int, dest: int
) -> dict[str, list[list[int]]]:
    direct = rutas_directas(matrix, origin, dest)
    if direct:
        return {"Directas": direct, "1 escala": [], "2 escalas": []}
    one = rutas_una_escala(matrix, origin, dest)
    if one:
        return {"Directas": [], "1 escala": one, "2 escalas": []}
    return {
        "Directas": [],
        "1 escala": [],
        "2 escalas": rutas_dos_escalas(matrix, origin, dest),
    }


def rutas_desde_origen(
    matrix: list[list[int]], origin: int
) -> dict[str, list[list[int]]]:
    groups = {"Directas": [], "1 escala": [], "2 escalas": []}
    for dest in range(N):
        if dest == origin:
            continue
        efficient = rutas_eficientes(matrix, origin, dest)
        for label, routes in efficient.items():
            groups[label].extend(routes)
    return groups


def all_edges(matrix: list[list[int]]) -> list[tuple[int, int]]:
    return [(i, j) for i in range(N) for j in range(N) if matrix[i][j] == 1]


def route_edges(route: list[int]) -> list[tuple[int, int]]:
    return list(zip(route, route[1:]))


def haversine_km(a: int, b: int) -> float:
    lat1, lon1 = CITIES[a].lat, CITIES[a].lon
    lat2, lon2 = CITIES[b].lat, CITIES[b].lon
    r = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    x = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    return 2 * r * asin(sqrt(x))


def route_distance(route: list[int]) -> float:
    return sum(haversine_km(a, b) for a, b in route_edges(route))


def init_state() -> None:
    if "matrix" not in st.session_state:
        st.session_state.matrix = crear_matriz()
        cargar_rutas_base(st.session_state.matrix)
    if "selected_route" not in st.session_state:
        st.session_state.selected_route = None
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "origin" not in st.session_state:
        st.session_state.origin = None
    if "dest" not in st.session_state:
        st.session_state.dest = None
    if "history" not in st.session_state:
        st.session_state.history = []
    if "active_section" not in st.session_state:
        st.session_state.active_section = "Rutas"
    digraph_origin = st.query_params.get("digraph_origin")
    digraph_pick = st.query_params.get("digraph_pick", "")
    if isinstance(digraph_origin, list):
        digraph_origin = digraph_origin[0] if digraph_origin else None
    if isinstance(digraph_pick, list):
        digraph_pick = digraph_pick[0] if digraph_pick else ""
    digraph_selection = f"{digraph_origin}:{digraph_pick}"
    if (
        digraph_origin in CITY_NAMES
        and st.session_state.get("_digraph_origin_consumed") != digraph_selection
    ):
        st.session_state.origin = digraph_origin
        st.session_state.active_section = "Digrafo"
        st.session_state._digraph_origin_consumed = digraph_selection


def css() -> None:
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #0f3d2e, #166534);
            border: 1px solid rgba(74, 222, 128, .35);
            padding: 14px;
            border-radius: 12px;
        }
        .hero {
            background:
                linear-gradient(135deg, rgba(15,61,46,.94), rgba(22,101,52,.72)),
                radial-gradient(circle at 20% 10%, rgba(74,222,128,.30), transparent 35%);
            border: 1px solid rgba(74,222,128,.3);
            border-radius: 18px;
            padding: 24px;
            color: white;
            margin-bottom: 18px;
        }
        .hero h1 { margin: 0; font-size: 34px; }
        .hero p { margin: 8px 0 0 0; color: rgba(255,255,255,.86); }
        .route-card {
            border: 1px solid rgba(148,163,184,.35);
            border-radius: 12px;
            padding: 14px;
            background: rgba(15,23,42,.05);
            margin-bottom: 10px;
        }
        .digraph-shell {
            border: 1px solid rgba(148,163,184,.35);
            border-radius: 14px;
            background: #08111f;
            overflow: hidden;
            margin: 12px 0 18px 0;
        }
        .digraph-title {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: flex-start;
            padding: 16px 18px;
            border-bottom: 1px solid rgba(148,163,184,.25);
            color: #f8fafc;
        }
        .digraph-title h3 { margin: 0; font-size: 18px; }
        .digraph-title p { margin: 4px 0 0 0; color: #cbd5e1; font-size: 13px; }
        .digraph-title span {
            white-space: nowrap;
            color: #bbf7d0;
            background: rgba(34,197,94,.14);
            border: 1px solid rgba(74,222,128,.35);
            border-radius: 999px;
            padding: 5px 10px;
            font-size: 12px;
            font-weight: 700;
        }
        .digraph-scroll {
            overflow: auto;
            max-height: 720px;
            padding: 12px;
        }
        .digraph-scroll svg {
            min-width: 1040px;
            width: 100%;
            height: auto;
            display: block;
        }
        .graph-bg { fill: #0b1424; }
        .graph-grid {
            stroke: rgba(148,163,184,.12);
            stroke-width: 1;
        }
        .graph-frame {
            fill: none;
            stroke: rgba(74,222,128,.35);
            stroke-width: 2;
        }
        .group-label {
            fill: #bbf7d0;
            font-size: 14px;
            font-weight: 800;
            text-anchor: middle;
            letter-spacing: .02em;
        }
        .node circle {
            fill: #0f172a;
            stroke: #34d399;
            stroke-width: 2;
        }
        .node.start circle { fill: #451a03; stroke: #f59e0b; }
        .node.end circle { fill: #4c0519; stroke: #fb7185; }
        .node.mid circle { fill: #2e1065; stroke: #a78bfa; }
        .node.peru circle { fill: #052e1a; stroke: #34d399; }
        .node.centroamerica-y-caribe circle { fill: #064e3b; stroke: #4ade80; }
        .node.colombia circle { fill: #134e4a; stroke: #2dd4bf; }
        .node.sudamerica circle { fill: #365314; stroke: #a3e635; }
        .node.europa circle { fill: #14532d; stroke: #86efac; }
        .node-label-bg {
            fill: rgba(8,17,31,.86);
            stroke: rgba(148,163,184,.24);
            stroke-width: 1;
        }
        .node text {
            fill: #f8fafc;
            font-size: 11px;
            font-weight: 700;
            dominant-baseline: middle;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def header() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>RouteMatrix</h1>
            <p>Analisis de rutas aereas mediante relacion binaria, matriz de conectividad y mapa.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def node_dataframe(
    nodes: Iterable[int], route: list[int] | None = None
) -> pd.DataFrame:
    route = route or []
    rows = []
    for idx in nodes:
        city = CITIES[idx]
        if route and idx == route[0]:
            kind = "Origen"
            color = [245, 158, 11, 225]
            radius = 65000
        elif route and idx == route[-1]:
            kind = "Destino"
            color = [251, 113, 133, 225]
            radius = 65000
        elif route and idx in route:
            kind = "Escala"
            color = [167, 139, 250, 225]
            radius = 54000
        else:
            kind = "Ciudad"
            color = [52, 211, 153, 170]
            radius = 36000
        rows.append(
            {
                "city": city.name,
                "country": city.country,
                "lat": city.lat,
                "lon": city.lon,
                "kind": kind,
                "color": color,
                "radius": radius,
            }
        )
    return pd.DataFrame(rows)


def edge_dataframe(
    edges: Iterable[tuple[int, int]],
    route_edges_set: set[tuple[int, int]] | None = None,
) -> pd.DataFrame:
    route_edges_set = route_edges_set or set()
    rows = []
    for a, b in edges:
        start = CITIES[a]
        end = CITIES[b]
        selected = (a, b) in route_edges_set
        rows.append(
            {
                "from": start.name,
                "to": end.name,
                "from_lon": start.lon,
                "from_lat": start.lat,
                "to_lon": end.lon,
                "to_lat": end.lat,
                "color": [245, 158, 11, 215] if selected else [52, 211, 153, 60],
                "width": 4 if selected else 1,
            }
        )
    return pd.DataFrame(rows)


def city_group(idx: int) -> str:
    city = CITIES[idx].name
    if city in {
        "Piura",
        "Chiclayo",
        "Trujillo",
        "Iquitos",
        "Lima",
        "Cusco",
        "Puerto Maldonado",
        "Juliaca",
        "Arequipa",
    }:
        return "Peru"
    if city in {
        "Ciudad de Mexico",
        "Cancun",
        "La Habana",
        "Belice",
        "Flores",
        "Ciudad de Guatemala",
        "San Salvador",
        "San Pedro Sula",
        "Roatan",
        "La Ceiba",
        "Tegucigalpa",
        "Managua",
        "Liberia",
        "San Jose de Costa Rica",
        "Ciudad de Panama",
        "Santo Domingo",
        "Punta Cana",
        "San Juan",
    }:
        return "Centroamerica y Caribe"
    if CITIES[idx].country == "Colombia":
        return "Colombia"
    if city in {"Madrid", "Barcelona", "Londres"}:
        return "Europa"
    return "Sudamerica"


def geo_digraph_layout(nodes: list[int]) -> tuple[dict[int, tuple[int, int]], int, int]:
    width = 1450
    height = 760
    padding = 70
    min_lat = min(CITIES[idx].lat for idx in nodes)
    max_lat = max(CITIES[idx].lat for idx in nodes)
    min_lon = min(CITIES[idx].lon for idx in nodes)
    max_lon = max(CITIES[idx].lon for idx in nodes)
    lat_span = max(max_lat - min_lat, 1)
    lon_span = max(max_lon - min_lon, 1)

    usable_width = width - padding * 2
    usable_height = height - padding * 2
    scale = min(usable_width / lon_span, usable_height / lat_span)
    graph_width = lon_span * scale
    graph_height = lat_span * scale
    x_offset = (width - graph_width) / 2
    y_offset = (height - graph_height) / 2

    positions = {}
    for idx in nodes:
        city = CITIES[idx]
        x = x_offset + (city.lon - min_lon) * scale
        y = y_offset + (max_lat - city.lat) * scale
        positions[idx] = (round(x), round(y))
    return positions, width, height


def svg_edge_path(
    start: tuple[int, int],
    end: tuple[int, int],
    offset: int = 0,
) -> str:
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) < 8:
        c1 = (x1 + offset, y1 + dy * 0.35)
        c2 = (x2 + offset, y2 - dy * 0.35)
    else:
        c1 = (x1 + dx * 0.45, y1 + offset)
        c2 = (x2 - dx * 0.45, y2 + offset)
    return f"M {x1} {y1} C {c1[0]} {c1[1]}, {c2[0]} {c2[1]}, {x2} {y2}"


def shorten_label(label: str, limit: int = 20) -> str:
    return label if len(label) <= limit else label[: limit - 1] + "..."


def css_slug(text: str) -> str:
    normalized = (
        text.lower()
        .replace(" ", "-")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
    return "".join(ch for ch in normalized if ch.isalnum() or ch == "-")


def visible_digraph_edges(
    edges: list[tuple[int, int]],
    route: list[int] | None,
) -> list[tuple[int, int, bool]]:
    if route:
        return [(a, b, False) for a, b in edges]

    edge_set = set(edges)
    handled = set()
    display_edges = []
    for a, b in edges:
        if (a, b) in handled:
            continue
        if (b, a) in edge_set:
            handled.add((a, b))
            handled.add((b, a))
            display_edges.append((a, b, True))
        else:
            handled.add((a, b))
            display_edges.append((a, b, False))
    return display_edges


def digraph_svg(
    matrix: list[list[int]],
    route: list[int] | None = None,
) -> tuple[str, int, int, list[int], list[tuple[int, int]]]:
    if route:
        nodes = list(dict.fromkeys(route))
        edges = route_edges(route)
        positions, width, height = geo_digraph_layout(nodes)
        selected_edges = set(edges)
        title = "Ruta seleccionada en proporcion geografica"
    else:
        nodes = list(range(N))
        edges = all_edges(matrix)
        positions, width, height = geo_digraph_layout(nodes)
        selected_edges = set()
        title = "Digrafo completo en proporcion geografica"

    node_set = set(nodes)
    visible_edges = [(a, b) for a, b in edges if a in node_set and b in node_set]
    grid_lines = []
    for x in range(100, width, 125):
        grid_lines.append(
            f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" class="graph-grid" />'
        )
    for y in range(80, height, 100):
        grid_lines.append(
            f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" class="graph-grid" />'
        )

    pair_seen: dict[tuple[int, int], int] = {}
    edge_markup = []
    display_edges = visible_digraph_edges(visible_edges, route)
    for a, b, bidirectional in display_edges:
        key = tuple(sorted((a, b)))
        pair_seen[key] = pair_seen.get(key, 0) + 1
        offset = 10 if bidirectional else 18 if pair_seen[key] % 2 else -18
        selected = (a, b) in selected_edges
        stroke = "#f59e0b" if selected else "#34d399"
        opacity = "0.96" if selected else "0.17"
        width_px = "3.2" if selected else "1.4"
        marker_start = 'marker-start="url(#arrow-soft)" ' if bidirectional else ""
        marker_end = (
            'marker-end="url(#arrow-selected)"'
            if selected
            else 'marker-end="url(#arrow-soft)"'
        )
        edge_markup.append(
            f'<path d="{svg_edge_path(positions[a], positions[b], offset)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{width_px}" '
            f'stroke-opacity="{opacity}" {marker_start}{marker_end} />'
        )

    degree_by_node = {
        idx: sum(1 for target in range(N) if matrix[idx][target])
        + sum(1 for source in range(N) if matrix[source][idx])
        for idx in nodes
    }
    key_nodes = {
        "Lima",
        "Bogota",
        "San Salvador",
        "Cali",
        "Medellin",
        "Ciudad de Panama",
    }
    node_markup = []
    for idx in nodes:
        x, y = positions[idx]
        city = html_lib.escape(CITIES[idx].name)
        country = html_lib.escape(CITIES[idx].country)
        label_text = shorten_label(CITIES[idx].name, 17)
        label = html_lib.escape(label_text)
        is_start = bool(route and idx == route[0])
        is_end = bool(route and idx == route[-1])
        role = (
            "start"
            if is_start
            else "end" if is_end else "mid" if route else css_slug(city_group(idx))
        )
        radius = 11 if not route else 14
        if degree_by_node[idx] >= 10:
            radius = 16
        elif degree_by_node[idx] >= 5:
            radius = 13
        label_width = max(68, len(label_text) * 7 + 16)
        label_class = (
            "hub-label"
            if CITIES[idx].name in key_nodes or degree_by_node[idx] >= 10
            else "detail-label"
        )
        label_markup = (
            f'<g class="label-pack {label_class}">'
            f'<rect x="{x + 20}" y="{y - 12}" width="{label_width}" height="24" '
            f'rx="6" class="node-label-bg" />'
            f'<text x="{x + 28}" y="{y + 1}">{label}</text>'
            "</g>"
        )
        origin_url = f"?digraph_origin={quote(CITIES[idx].name)}"
        node_markup.append(
            f'<a href="{origin_url}" target="_parent" class="node-link" data-city="{city}">'
            f'<g class="node {role}" data-city="{city}">'
            f"<title>{city} - {country}</title>"
            f'<circle cx="{x}" cy="{y}" r="{radius}" />'
            f"{label_markup}"
            "</g>"
            "</a>"
        )

    svg = f"""
    <style>
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: "Segoe UI", system-ui, sans-serif;
        background: transparent;
      }}
      .digraph-shell {{
        border: 1px solid rgba(148,163,184,.35);
        border-radius: 14px;
        background: #08111f;
        overflow: hidden;
        color: #f8fafc;
      }}
      .digraph-title {{
        display: flex;
        justify-content: space-between;
        gap: 16px;
        align-items: flex-start;
        padding: 14px 16px;
        border-bottom: 1px solid rgba(148,163,184,.25);
      }}
      .digraph-title h3 {{ margin: 0; font-size: 18px; }}
      .digraph-title p {{ margin: 4px 0 0 0; color: #cbd5e1; font-size: 13px; }}
      .digraph-title span {{
        white-space: nowrap;
        color: #bbf7d0;
        background: rgba(34,197,94,.14);
        border: 1px solid rgba(74,222,128,.35);
        border-radius: 999px;
        padding: 5px 10px;
        font-size: 12px;
        font-weight: 700;
      }}
      .digraph-tools {{
        display: flex;
        gap: 8px;
        align-items: center;
        padding: 10px 12px;
        border-bottom: 1px solid rgba(148,163,184,.18);
        background: rgba(15,23,42,.72);
      }}
      .digraph-tools button {{
        height: 32px;
        min-width: 36px;
        border: 1px solid rgba(74,222,128,.35);
        border-radius: 8px;
        background: #0f3d2e;
        color: #dcfce7;
        font-weight: 800;
        cursor: pointer;
      }}
      .digraph-tools button:hover {{ background: #166534; }}
      .digraph-tools small {{ color: #94a3b8; margin-left: 6px; }}
      .digraph-viewport {{
        height: 620px;
        overflow: hidden;
        cursor: grab;
        touch-action: none;
      }}
      .digraph-viewport.dragging {{ cursor: grabbing; }}
      svg {{ width: 100%; height: 100%; display: block; }}
      .graph-bg {{ fill: #0b1424; }}
      .graph-grid {{ stroke: rgba(148,163,184,.12); stroke-width: 1; }}
      .graph-frame {{
        fill: none;
        stroke: rgba(74,222,128,.35);
        stroke-width: 2;
      }}
      .node circle {{ fill: #0f172a; stroke: #34d399; stroke-width: 2; }}
      .node-link {{ cursor: pointer; }}
      .node-link:hover .node circle {{
        stroke: #f59e0b;
        stroke-width: 3;
      }}
      .node.start circle {{ fill: #451a03; stroke: #f59e0b; }}
      .node.end circle {{ fill: #4c0519; stroke: #fb7185; }}
      .node.mid circle {{ fill: #2e1065; stroke: #a78bfa; }}
      .node.peru circle {{ fill: #052e1a; stroke: #34d399; }}
      .node.centroamerica-y-caribe circle {{ fill: #064e3b; stroke: #4ade80; }}
      .node.colombia circle {{ fill: #134e4a; stroke: #2dd4bf; }}
      .node.sudamerica circle {{ fill: #365314; stroke: #a3e635; }}
      .node.europa circle {{ fill: #14532d; stroke: #86efac; }}
      .label-pack {{
        opacity: 0;
        transition: opacity .14s ease;
        pointer-events: none;
      }}
      svg.labels-mid .hub-label,
      svg.labels-on .label-pack {{ opacity: 1; }}
      .node-label-bg {{
        fill: rgba(8,17,31,.9);
        stroke: rgba(148,163,184,.28);
        stroke-width: 1;
      }}
      .node text {{
        fill: #f8fafc;
        font-size: 11px;
        font-weight: 700;
        dominant-baseline: middle;
      }}
    </style>
    <div class="digraph-shell">
      <div class="digraph-title">
        <div>
          <h3>{html_lib.escape(title)}</h3>
          <p>Arrastra para mover, usa la rueda para acercar. Los nombres aparecen al hacer zoom.</p>
        </div>
        <span>{len(nodes)} nodos | {len(visible_edges)} aristas</span>
      </div>
      <div class="digraph-tools">
        <button type="button" id="zoom-in">+</button>
        <button type="button" id="zoom-out">-</button>
        <button type="button" id="zoom-reset">Centrar</button>
        <small id="zoom-label">Zoom 100%</small>
      </div>
      <div class="digraph-viewport" id="digraph-viewport">
        <svg id="digraph-svg" viewBox="0 0 {width} {height}" role="img" aria-label="{html_lib.escape(title)}">
          <defs>
            <marker id="arrow-soft" viewBox="0 0 10 10" refX="9" refY="5"
              markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#34d399" fill-opacity=".62" />
            </marker>
            <marker id="arrow-selected" viewBox="0 0 10 10" refX="9" refY="5"
              markerWidth="8" markerHeight="8" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#f59e0b" />
            </marker>
          </defs>
          <rect width="{width}" height="{height}" rx="18" class="graph-bg" />
          <rect x="20" y="20" width="{width - 40}" height="{height - 40}" rx="16" class="graph-frame" />
          {''.join(grid_lines)}
          {''.join(edge_markup)}
          {''.join(node_markup)}
        </svg>
      </div>
    </div>
    <script>
      const svg = document.getElementById("digraph-svg");
      const viewport = document.getElementById("digraph-viewport");
      const label = document.getElementById("zoom-label");
      const base = {{ x: 0, y: 0, w: {width}, h: {height} }};
      let box = {{ ...base }};
      let dragging = false;
      let didDrag = false;
      let last = {{ x: 0, y: 0 }};

      function applyBox() {{
        svg.setAttribute("viewBox", `${{box.x}} ${{box.y}} ${{box.w}} ${{box.h}}`);
        const zoom = base.w / box.w;
        svg.classList.toggle("labels-mid", zoom >= 1.45);
        svg.classList.toggle("labels-on", zoom >= 2.15);
        label.textContent = `Zoom ${{Math.round(zoom * 100)}}%`;
      }}

      function clientToSvg(event) {{
        const rect = svg.getBoundingClientRect();
        return {{
          x: box.x + ((event.clientX - rect.left) / rect.width) * box.w,
          y: box.y + ((event.clientY - rect.top) / rect.height) * box.h
        }};
      }}

      function zoomAt(factor, anchor) {{
        const nextW = Math.max(base.w / 5, Math.min(base.w, box.w * factor));
        const nextH = nextW * (base.h / base.w);
        box.x = anchor.x - ((anchor.x - box.x) / box.w) * nextW;
        box.y = anchor.y - ((anchor.y - box.y) / box.h) * nextH;
        box.w = nextW;
        box.h = nextH;
        applyBox();
      }}

      viewport.addEventListener("wheel", (event) => {{
        event.preventDefault();
        zoomAt(event.deltaY < 0 ? 0.86 : 1.16, clientToSvg(event));
      }}, {{ passive: false }});

      viewport.addEventListener("pointerdown", (event) => {{
        dragging = true;
        didDrag = false;
        last = {{ x: event.clientX, y: event.clientY }};
        viewport.classList.add("dragging");
        viewport.setPointerCapture(event.pointerId);
      }});

      viewport.addEventListener("pointermove", (event) => {{
        if (!dragging) return;
        const rect = svg.getBoundingClientRect();
        if (Math.abs(event.clientX - last.x) > 2 || Math.abs(event.clientY - last.y) > 2) {{
          didDrag = true;
        }}
        box.x -= ((event.clientX - last.x) / rect.width) * box.w;
        box.y -= ((event.clientY - last.y) / rect.height) * box.h;
        last = {{ x: event.clientX, y: event.clientY }};
        applyBox();
      }});

      viewport.addEventListener("click", (event) => {{
        const link = event.target.closest("a.node-link");
        if (!link) return;
        event.preventDefault();
        if (didDrag) {{
          return;
        }}
        const target = new URL(window.parent.location.href);
        target.searchParams.set("digraph_origin", link.dataset.city);
        target.searchParams.set("digraph_pick", Date.now().toString());
        window.parent.location.href = target.toString();
      }});

      function stopDrag() {{
        dragging = false;
        viewport.classList.remove("dragging");
      }}
      viewport.addEventListener("pointerup", stopDrag);
      viewport.addEventListener("pointerleave", stopDrag);

      document.getElementById("zoom-in").addEventListener("click", () => {{
        zoomAt(0.78, {{ x: box.x + box.w / 2, y: box.y + box.h / 2 }});
      }});
      document.getElementById("zoom-out").addEventListener("click", () => {{
        zoomAt(1.24, {{ x: box.x + box.w / 2, y: box.y + box.h / 2 }});
      }});
      document.getElementById("zoom-reset").addEventListener("click", () => {{
        box = {{ ...base }};
        applyBox();
      }});
      applyBox();
    </script>
    """
    return svg, width, height, nodes, visible_edges


def draw_digraph(matrix: list[list[int]], route: list[int] | None = None) -> None:
    route_available = route is not None
    mode_options = ["Digrafo completo"]
    if route_available:
        mode_options.insert(0, "Ruta seleccionada")

    selected_mode = st.radio(
        "Vista del digrafo",
        mode_options,
        horizontal=True,
        label_visibility="collapsed",
    )
    selected_route = route if selected_mode == "Ruta seleccionada" else None
    svg, _width, _height, nodes, edges = digraph_svg(matrix, selected_route)

    st.subheader("Digrafo de ciudades")
    st.caption(
        "Vista separada del mapa: conserva las proporciones geograficas y muestra solo nodos y conexiones."
    )
    components.html(svg, height=760, scrolling=False)

    out_degrees = []
    node_set = set(nodes)
    for idx in nodes:
        out_degrees.append(
            {
                "Nodo": idx,
                "Ciudad": CITIES[idx].name,
                "Grupo": city_group(idx),
                "Salidas visibles": sum(1 for a, _b in edges if a == idx),
                "Entradas visibles": sum(1 for _a, b in edges if b == idx),
                "Grado total": sum(1 for j in range(N) if matrix[idx][j])
                + sum(1 for i in range(N) if matrix[i][idx]),
            }
        )

    st.markdown("### Resumen de nodos")
    st.dataframe(
        pd.DataFrame(out_degrees).sort_values(
            ["Salidas visibles", "Entradas visibles"], ascending=False
        ),
        use_container_width=True,
        hide_index=True,
    )


def view_state_for(nodes: list[int]) -> dict[str, float]:
    if not nodes:
        return {"latitude": 7.0, "longitude": -75.0, "zoom": 2.5}
    lats = [CITIES[i].lat for i in nodes]
    lons = [CITIES[i].lon for i in nodes]
    span = max(max(lats) - min(lats), max(lons) - min(lons))
    zoom = 4.7 if span < 10 else 3.4 if span < 35 else 2.2
    return {
        "latitude": sum(lats) / len(lats),
        "longitude": sum(lons) / len(lons),
        "zoom": zoom,
    }


def draw_interactive_map(
    matrix: list[list[int]],
    route: list[int] | None = None,
) -> None:
    route = route or None
    if route:
        nodes = list(dict.fromkeys(route))
        edges = route_edges(route)
        route_edge_set = set(route_edges(route))
        title = "Mapa de la ruta seleccionada"
    else:
        nodes = list(range(N))
        edges = all_edges(matrix)
        route_edge_set = set()
        title = "Mapa del digrafo completo"

    st.subheader(title)
    st.caption(
        "Arrastra para mover, usa la rueda para zoom y pasa el cursor sobre los nodos para ver detalles."
    )

    nodes_df = node_dataframe(nodes, route)
    edges_df = edge_dataframe(edges, route_edge_set)
    view = view_state_for(nodes)

    if pdk is None:
        st.map(
            nodes_df.rename(columns={"lat": "latitude", "lon": "longitude"}),
            latitude="latitude",
            longitude="longitude",
        )
        st.info(
            "Instala pydeck para ver arcos de rutas sobre el mapa: pip install pydeck"
        )
        return

    layers = [
        pdk.Layer(
            "ArcLayer",
            edges_df,
            get_source_position=["from_lon", "from_lat"],
            get_target_position=["to_lon", "to_lat"],
            get_source_color="color",
            get_target_color="color",
            get_width="width",
            auto_highlight=True,
            pickable=True,
        ),
        pdk.Layer(
            "ScatterplotLayer",
            nodes_df,
            get_position=["lon", "lat"],
            get_fill_color="color",
            get_radius="radius",
            radius_min_pixels=5,
            radius_max_pixels=18,
            pickable=True,
        ),
        pdk.Layer(
            "TextLayer",
            nodes_df if route else nodes_df.iloc[[]],
            get_position=["lon", "lat"],
            get_text="city",
            get_size=13,
            get_color=[255, 255, 255],
            get_alignment_baseline="'bottom'",
            get_pixel_offset=[0, -18],
        ),
    ]

    st.pydeck_chart(
        pdk.Deck(
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            initial_view_state=pdk.ViewState(
                latitude=view["latitude"],
                longitude=view["longitude"],
                zoom=view["zoom"],
                pitch=25,
            ),
            layers=layers,
            tooltip={
                "html": "<b>{city}</b><br/>{country}<br/>{kind}",
                "style": {"backgroundColor": "#0f172a", "color": "white"},
            },
        ),
        use_container_width=True,
    )


def show_route_cards(groups: dict[str, list[list[int]]]) -> None:
    all_routes = [route for routes in groups.values() for route in routes]
    if not all_routes:
        st.info("No se encontraron rutas disponibles hasta 2 escalas.")
        return

    route_options = {
        f"{' -> '.join(CITY_NAMES[i] for i in route)} - {len(route) - 1} tramo(s)": route
        for route in all_routes
    }
    selected_label = st.selectbox(
        "Ruta que se mostrara en el mapa",
        list(route_options.keys()),
        index=0,
    )
    st.session_state.selected_route = route_options[selected_label]

    for label, routes in groups.items():
        if not routes:
            continue
        st.markdown(f"### {label}")
        for idx, route in enumerate(routes):
            text = " -> ".join(CITY_NAMES[i] for i in route)
            distance = route_distance(route)
            with st.container(border=True):
                if route == st.session_state.selected_route:
                    st.success("Mostrandose en el mapa")
                st.markdown(f"**{text}**")
                st.caption(
                    f"{len(route) - 1} tramo(s) | {max(0, len(route) - 2)} escala(s) | {distance:,.0f} km"
                )


def show_matrix(matrix: list[list[int]]) -> None:
    df = pd.DataFrame(matrix, index=CITY_NAMES, columns=CITY_NAMES)
    st.dataframe(df, use_container_width=True)


def show_city_catalog() -> None:
    data = [
        {
            "Ciudad": city.name,
            "Pais": city.country,
            "Latitud": city.lat,
            "Longitud": city.lon,
            "Nodo": i,
        }
        for i, city in enumerate(CITIES)
    ]
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)


def show_about() -> None:
    st.subheader("Sobre nosotros")
    st.markdown("""
        **Universidad Peruana de Ciencias Aplicadas**  
        **Curso:** Matematica Discreta (1AMA0708) - NRC 13224  
        **Proyecto:** RouteMatrix - Analisis de rutas aereas mediante relaciones binarias y matrices de conectividad
        """)

    st.write(
        "RouteMatrix representa una red de vuelos como una relacion binaria sobre un conjunto de ciudades. "
        "A partir de esa relacion se construye la matriz de conectividad M, se analizan rutas directas "
        "y rutas con escalas, y se visualizan los recorridos sobre un mapa con coordenadas reales."
    )

    st.markdown("### Integrantes")
    team = [
        ("Astudillo Oliva, Matheo Fabian Anthony", "u202517618"),
        ("Cordova Salcedo, Juan Pablo", "u20241i934"),
        ("Fernandez Jara, Jean Pier Carlos", "u20251f122"),
        ("Lengua Nieto, Cesar Aldair", "u20251f085"),
        ("Pereira Mamani, Juan Andree", "u20251f947"),
    ]

    cols = st.columns(2)
    for i, (name, code) in enumerate(team):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{name}**")
                st.caption(code)

    info1, info2 = st.columns(2)
    with info1:
        st.markdown("### Profesor")
        st.info("Juan Manuel Mattos Quevedo")
    with info2:
        st.markdown("### Fecha")
        st.info("Lima, 19 de abril de 2026")

    st.markdown("### Fundamento matematico")
    st.write(
        "La aplicacion conserva el criterio del proyecto original: M[i, j] = 1 indica que existe una ruta "
        "directa desde la ciudad i hacia la ciudad j. Las rutas con una escala se interpretan mediante "
        "composicion de relaciones, equivalente al analisis de M2; las rutas con dos escalas corresponden "
        "al analisis de M3, evitando repetir ciudades en un mismo recorrido."
    )


def optional_city_selectbox(
    label: str, value: str | None, empty_label: str
) -> str | None:
    options = [""] + CITY_NAMES
    index = options.index(value) if value in CITY_NAMES else 0
    selected = st.sidebar.selectbox(
        label,
        options,
        index=index,
        format_func=lambda city: empty_label if city == "" else city,
    )
    return selected or None


def sidebar(matrix: list[list[int]]) -> None:
    st.sidebar.title("RouteMatrix")
    st.sidebar.caption("Relacion binaria R y matriz M")

    st.session_state.origin = optional_city_selectbox(
        "Ciudad de origen",
        st.session_state.origin,
        "Selecciona origen",
    )
    st.session_state.dest = optional_city_selectbox(
        "Ciudad de destino",
        st.session_state.dest,
        "Selecciona destino",
    )

    if st.sidebar.button("Buscar rutas eficientes", use_container_width=True):
        origin = st.session_state.origin
        dest = st.session_state.dest
        if not origin:
            st.sidebar.warning("Selecciona una ciudad de origen.")
        elif dest and origin == dest:
            st.sidebar.warning("Origen y destino deben ser diferentes.")
        elif not dest:
            groups = rutas_desde_origen(matrix, INDEX[origin])
            st.session_state.last_result = groups
            st.session_state.selected_route = None
            st.rerun()
        else:
            groups = rutas_eficientes(matrix, INDEX[origin], INDEX[dest])
            st.session_state.last_result = groups
            st.session_state.selected_route = None
            st.rerun()

    if st.sidebar.button("Mostrar mapa completo", use_container_width=True):
        st.session_state.selected_route = None
        st.session_state.last_result = None
        st.rerun()

    st.sidebar.divider()
    st.sidebar.subheader("Agregar ruta dirigida")
    new_origin = st.sidebar.selectbox(
        "Nuevo origen", CITY_NAMES, index=None, key="new_origin"
    )
    new_dest = st.sidebar.selectbox(
        "Nuevo destino", CITY_NAMES, index=None, key="new_dest"
    )
    if st.sidebar.button("Agregar a M", use_container_width=True):
        if not new_origin or not new_dest:
            st.sidebar.warning("Completa origen y destino.")
        elif new_origin == new_dest:
            st.sidebar.warning("No se permite una ruta reflexiva.")
        elif matrix[INDEX[new_origin]][INDEX[new_dest]]:
            st.sidebar.info("La ruta ya existe.")
        else:
            matrix[INDEX[new_origin]][INDEX[new_dest]] = 1
            st.sidebar.success(f"Ruta agregada: {new_origin} -> {new_dest}")
            st.session_state.history.append(
                {
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "ruta": f"{new_origin} -> {new_dest}",
                }
            )


def main() -> None:
    css()
    init_state()
    matrix = st.session_state.matrix
    sidebar(matrix)
    header()

    edges = all_edges(matrix)
    c1, c2, c3 = st.columns(3)
    c1.metric("Ciudades", N)
    c2.metric("Rutas directas", len(edges))
    c3.metric("Matriz", f"{N} x {N}")

    sections = [
        "Digrafo",
        "Rutas",
        "Mapa",
        "Matriz M",
        "Ciudades",
        "Sobre nosotros",
    ]
    if st.session_state.active_section not in sections:
        st.session_state.active_section = sections[0]

    active = st.radio(
        "Seccion",
        sections,
        horizontal=True,
        label_visibility="collapsed",
        key="active_section",
    )

    if active == "Digrafo":
        draw_digraph(matrix, st.session_state.selected_route)

    if active == "Rutas":
        result = st.session_state.last_result
        if result:
            show_route_cards(result)
        else:
            st.info("Busca una ruta eficiente desde el panel izquierdo.")

    elif active == "Mapa":
        draw_interactive_map(matrix, st.session_state.selected_route)
        if st.session_state.selected_route:
            st.success(
                "Ruta seleccionada: "
                + " -> ".join(CITY_NAMES[i] for i in st.session_state.selected_route)
            )
        else:
            st.caption("Mostrando el digrafo completo sobre el mapa.")

    elif active == "Matriz M":
        st.subheader("Matriz de conectividad")
        st.caption(
            "M[i, j] = 1 si existe una ruta directa desde la ciudad i hacia la ciudad j."
        )
        show_matrix(matrix)

    elif active == "Ciudades":
        st.subheader("Catalogo de ciudades")
        show_city_catalog()

    elif active == "Sobre nosotros":
        show_about()
        if st.session_state.history:
            st.markdown("### Rutas agregadas en esta sesion")
            st.dataframe(
                pd.DataFrame(st.session_state.history),
                use_container_width=True,
                hide_index=True,
            )


if __name__ == "__main__":
    main()
