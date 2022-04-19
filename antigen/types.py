from ast import AST
from dataclasses import dataclass


@dataclass
class Mutation:
    node: AST
