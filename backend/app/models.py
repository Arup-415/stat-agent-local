from pydantic import BaseModel
from typing import List


class TwoSampleRequest(BaseModel):
    group1: List[float]
    group2: List[float]


class MultiGroupRequest(BaseModel):
    groups: List[List[float]]


class ChiSquareRequest(BaseModel):
    table: List[List[int]]