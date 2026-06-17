import array


def pack_embedding(values: list[float]) -> bytes:
    vector = array.array("f", values)
    return vector.tobytes()


def unpack_embedding(payload: bytes | None) -> list[float]:
    if not payload:
        return []
    vector = array.array("f")
    vector.frombytes(payload)
    return list(vector)
