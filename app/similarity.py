import math


def dot_product(vector_a, vector_b):
    """
    Calculate the dot product of two vectors.
    """

    if len(vector_a) != len(vector_b):
        raise ValueError("Vectors must have the same dimension.")

    result = 0.0

    for a, b in zip(vector_a, vector_b):
        result += a * b

    return result


def vector_magnitude(vector):
    """
    Calculate the Euclidean norm (length) of a vector.
    """

    squared_sum = 0.0

    for value in vector:
        squared_sum += value ** 2

    return math.sqrt(squared_sum)


def cosine_similarity(vector_a, vector_b):
    """
    Calculate the cosine similarity between two vectors.
    """

    dot = dot_product(vector_a, vector_b)

    magnitude_a = vector_magnitude(vector_a)
    magnitude_b = vector_magnitude(vector_b)

    if magnitude_a == 0 or magnitude_b == 0:
        raise ValueError("Cosine similarity is undefined for zero vectors.")

    return dot / (magnitude_a * magnitude_b)


if __name__ == "__main__":

    print("=" * 50)
    print("DOT PRODUCT TEST")
    print("=" * 50)

    vector1 = [1, 2, 3]
    vector2 = [4, 5, 6]

    print(f"Vector A: {vector1}")
    print(f"Vector B: {vector2}")
    print(f"Dot Product: {dot_product(vector1, vector2)}")

    print("\n" + "=" * 50)
    print("MAGNITUDE TEST")
    print("=" * 50)

    vector = [3, 4]

    print(f"Vector: {vector}")
    print(f"Magnitude: {vector_magnitude(vector)}")

    print("\n" + "=" * 50)
    print("COSINE SIMILARITY TESTS")
    print("=" * 50)

    test_cases = [
        ("Same Direction", [1, 2], [2, 4]),
        ("Perpendicular", [1, 0], [0, 1]),
        ("Opposite Direction", [1, 0], [-1, 0]),
        ("Identical Vectors", [3, 7], [3, 7]),
    ]

    for name, vec_a, vec_b in test_cases:
        similarity = cosine_similarity(vec_a, vec_b)

        print(f"\n{name}")
        print(f"A = {vec_a}")
        print(f"B = {vec_b}")
        print(f"Cosine Similarity = {similarity:.6f}")