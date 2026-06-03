"""
데이터 전처리 모듈
담당: 나하림
역할: 공공데이터포털 CSV → graph_data.json 변환

출력 graph_data.json은 M1·M2·M3·M5 공통 토대.
  - nodes   : 도시 거점 (대피소·병원·통신 허브 등)
  - edges   : 도로망 (거리·가중치 포함)
  - grid_mapping: M2 격자 좌표 ↔ 노드 id 매핑
                  (M2 담당자와 형식 합의 후 구현)
"""
import json
import pandas as pd

# [자료구조: 인접 리스트 딕셔너리 (Adjacency List Dictionary)]
# 도시 거점(노드)과 도로망(엣지)을 인접 리스트 형태로 표현
# 예: {"node_001": ["node_002", "node_003"], ...}


def load_raw_data(filepath: str) -> pd.DataFrame:
    """
    공공데이터포털 CSV 로드.
    Args:
        filepath: raw CSV 경로 (예: data/raw/shelter.csv)
    Returns:
        pd.DataFrame
    """
    # TODO: 실제 데이터 경로·컬럼 확정 후 구현
    # 출처: 공공데이터포털 (data.go.kr)
    df = pd.read_csv(filepath, encoding="utf-8")
    return df


def build_graph(df: pd.DataFrame) -> dict:
    """
    [자료구조: 인접 리스트 딕셔너리]
    DataFrame → graph_data 딕셔너리 변환.

    Returns:
        dict: {
            "nodes": [{"id", "name", "type", "lat", "lng", "capacity"}, ...],
            "edges": [{"from", "to", "distance", "weight"}, ...],
            "grid_mapping": {"node_id": {"row": int, "col": int}, ...}
        }
    """
    # TODO: 구현 예정
    graph = {
        "nodes": [],
        "edges": [],
        "grid_mapping": {}   # M2와 형식 합의 후 채울 것
    }
    return graph


def save_graph_data(graph: dict, output_path: str = "data/graph_data.json") -> None:
    """graph_data.json으로 저장."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)
    print(f"[preprocess] graph_data 저장 완료 → {output_path}")


if __name__ == "__main__":
    # TODO: 실제 데이터 경로 지정
    df = load_raw_data("data/raw/sample.csv")
    graph = build_graph(df)
    save_graph_data(graph)
