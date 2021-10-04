import os
from typing import Dict, Optional, Tuple, Union

PathLike = Union[str, os.PathLike]


REFERENCES: Dict[str, PathLike] = {
    "ENEL-SP @1": "compared_images/2021_03_DISTRIBUICAO_ENEL SP_RD 49672924.jpg",
    "ENEL-SP @2": "compared_images/2020_11_DISTRIBUICAO_ELETROPAULO_1139 TODO DIA Copiuva.jpg",
    "ELEKTRO @1": "compared_images/2021_04_DISTRIBUICAO_ELEKTRO_RD 12520411.jpg",
    "ELEKTRO @2": "compared_images/2021_08_DISTRIBUICAO_ELEKTRO_S214 MAXXI Mogi Guacu.jpg"
}


class ModelMatchNotFoundError(Exception):
    pass


def calculate_similarity(reference_image_file: PathLike, image_file: PathLike) -> int:
    hash0 = imagehash.average_hash(Image.open(reference_image_file))
    hash1 = imagehash.average_hash(Image.open(image_file))

    return hash0 - hash1


def find_best_match(
    references: Dict[str, PathLike],
    image_file: str,
    *,
    cutoff: Optional[int] = None
) -> Tuple[str, int]:
    best_model = None
    best_score = float('inf')

    for model, reference in references.items():
        score = calculate_similarity(reference, image_file)
        if score < best_score:
            best_model = model
            best_score = score

    if cutoff and best_score > cutoff:
        raise ModelMatchNotFoundError("Best match does not meet the cutoff")

    return best_model, best_score


def has_model(file: str) -> bool:
    try:
        find_best_match(REFERENCES, file, cutoff=10)
        return True
    except ModelMatchNotFoundError:
        return False
