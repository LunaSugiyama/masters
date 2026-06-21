from typing import List, Tuple, Optional

# ----------------------------
# Step 1: Batcher Sorter (handles None as -1)
# ----------------------------

def compare_and_swap(packets: List[Tuple[int, Optional[int]]], i: int, j: int, ascending: bool):
    key_i = -1 if packets[i][1] is None else packets[i][1]
    key_j = -1 if packets[j][1] is None else packets[j][1]

    if (ascending and key_i > key_j) or (not ascending and key_i < key_j):
        packets[i], packets[j] = packets[j], packets[i]

def bitonic_merge(packets: List[Tuple[int, Optional[int]]], low: int, cnt: int, ascending: bool):
    if cnt > 1:
        k = cnt // 2
        for i in range(low, low + k):
            compare_and_swap(packets, i, i + k, ascending)
        bitonic_merge(packets, low, k, ascending)
        bitonic_merge(packets, low + k, k, ascending)

def bitonic_sort(packets: List[Tuple[int, Optional[int]]], low: int, cnt: int, ascending: bool):
    if cnt > 1:
        k = cnt // 2
        bitonic_sort(packets, low, k, True)
        bitonic_sort(packets, low + k, k, False)
        bitonic_merge(packets, low, cnt, ascending)

def batcher_sort(packets: List[Tuple[int, Optional[int]]]) -> List[Tuple[int, Optional[int]]]:
    bitonic_sort(packets, 0, len(packets), True)
    return packets

# ----------------------------
# Step 2: Banyan Network
# ----------------------------

def int_to_bitstring(n: int, width: int) -> str:
    return format(n, f'0{width}b')

def banyan_network(packets: List[Tuple[int, Optional[int]]]) -> List[Optional[int]]:
    """
    ルーティングを行い、出力ポートごとに data_id を返す。
    宛先が None の場合はそのポートは None。
    """
    n = len(packets)
    width = (n - 1).bit_length()

    # 宛先をビット列に変換し、パケットを (data_id, bitstring) として扱う
    bit_packets: List[Optional[Tuple[int, str]]] = [
        (data, int_to_bitstring(dest, width)) if dest is not None else None
        for data, dest in packets
    ]

    def banyan_stage(stage_packets: List[Optional[Tuple[int, str]]], bit_index: int) -> List[Optional[Tuple[int, str]]]:
        result = [None] * len(stage_packets)
        for i in range(0, len(stage_packets), 2):
            upper = stage_packets[i]
            lower = stage_packets[i+1]

            if upper is None and lower is None:
                continue

            if upper is not None and upper[1][bit_index] == '0':
                result[i] = upper
            elif upper is not None and upper[1][bit_index] == '1':
                result[i+1] = upper

            if lower is not None:
                if lower[1][bit_index] == '0':
                    if result[i] is None:
                        result[i] = lower
                    else:
                        result[i+1] = lower
                else:
                    if result[i+1] is None:
                        result[i+1] = lower
                    else:
                        result[i] = lower
        return result

    stage_result = bit_packets[:]
    print("=== Stage 0:", stage_result)
    for stage in range(width):
        stage_result = banyan_stage(stage_result, stage)
        print(f"=== Stage {stage + 1}:", stage_result)

    # 最終出力: ビット列を整数に戻して data_id を配置
    output: List[Optional[int]] = [None] * n
    for pkt in stage_result:
        if pkt is not None:
            data, bits = pkt
            dest = int(bits, 2)
            output[dest] = data
    return output

# ----------------------------
# テストデータと実行
# ----------------------------

def main():
    inputs: List[Tuple[int, Optional[int]]] = [
        (0, None),
        (1, 6),
        (2, 2),
        (3, 7),
        (4, 1),
        (5, 0),
        (6, 5),
        (7, 4)
    ]

    print("=== 入力パケット ===")
    for p in inputs:
        print(p)

    sorted_packets = batcher_sort(inputs.copy())
    print("\n=== Batcher ソート後 ===")
    for p in sorted_packets:
        print(p)

    final_output = banyan_network(sorted_packets)
    print("\n=== Banyan 出力 ===")
    for i, p in enumerate(final_output):
        print(f"出力ポート {i}: {p}")

if __name__ == "__main__":
    main()
