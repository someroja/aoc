from collections import deque
from collections.abc import Callable
from typing import Final, NamedTuple

type Grid[T] = list[list[T]]

type Transform[T] = Callable[[str], T]


def to_int(value: str) -> int:
    return int(value)


class Tile[T](NamedTuple):
    i: int
    j: int
    value: T


class Region[T](NamedTuple):
    tiles: list[Tile[T]]


type Position = tuple[int, int]


type MatchPredicate[T] = Callable[[Tile[T], Tile[T]], bool]


def match_always[T](_a: Tile[T], _b: Tile[T]) -> bool:
    return True


def match_value[T](a: Tile[T], b: Tile[T]) -> bool:
    return a.value == b.value


type Direction = tuple[int, int]

UP: Final[Direction] = (-1, 0)
DOWN: Final[Direction] = (1, 0)
LEFT: Final[Direction] = (0, -1)
RIGHT: Final[Direction] = (0, 1)


def create_grid[T](
    puzzle_input: str, transform: Transform[T] = lambda tile: tile
) -> Grid[T]:
    return [
        [transform(tile) for tile in list(row)] for row in puzzle_input.splitlines()
    ]


def shape(grid: Grid) -> tuple[int, int]:
    return len(grid), len(grid[0])


def get_neighbours[T](
    tile: Tile[T], grid: Grid[T], predicate: MatchPredicate[T] = match_always
) -> list[Tile[T]]:
    neighbours = []
    row_count, col_count = shape(grid)
    for di, dj in [UP, RIGHT, DOWN, LEFT]:
        neighbour_i, neighbour_j = tile.i + di, tile.j + dj
        is_outside_bounds = (
            neighbour_i < 0
            or neighbour_i >= row_count
            or neighbour_j < 0
            or neighbour_j >= col_count
        )
        if is_outside_bounds:
            continue
        neighbour = Tile(neighbour_i, neighbour_j, grid[neighbour_i][neighbour_j])
        if predicate(tile, neighbour):
            neighbours.append(neighbour)
    return neighbours


def get_region[T](
    tile: Tile[T], grid: Grid[T], predicate: MatchPredicate[T] = match_value
) -> Region[T]:
    tiles = set()
    stack = deque([tile])
    while stack:
        current = stack.pop()
        if current not in tiles:
            tiles.add(current)
            stack.extend(
                neighbour
                for neighbour in get_neighbours(current, grid, predicate)
                if neighbour not in tiles
            )
    return Region(list(tiles))


def get_all_regions[T](
    grid: Grid[T], predicate: MatchPredicate[T] = match_value
) -> list[Region[T]]:
    regions = []
    visited_tiles = set()
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            tile = Tile(i, j, grid[i][j])
            if tile in visited_tiles:
                continue
            region = get_region(tile, grid, predicate)
            regions.append(region)
            visited_tiles.update(region.tiles)
    return regions


def get_perimeter(region: Region) -> int:
    coordinates = {(tile.i, tile.j) for tile in region.tiles}
    perimeter = 0
    for tile in region.tiles:
        for di, dj in [UP, RIGHT, DOWN, LEFT]:
            is_edge = (tile.i + di, tile.j + dj) not in coordinates
            if is_edge:
                perimeter += 1
    return perimeter


def get_tiles[T](
    grid: Grid[T], predicate: Callable[[Tile[T]], bool] = lambda tile: True
) -> list[Tile[T]]:
    tiles = []
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            tile = Tile(i, j, grid[i][j])
            if predicate(tile):
                tiles.append(tile)
    return tiles


def turn_right(direction: Direction) -> Direction:
    i, j = direction
    return (j, -i)


def turn_left(direction: Direction) -> Direction:
    i, j = direction
    return (-j, i)


def can_see(
    viewpoint: Position,
    target: Position,
    direction: Direction,
) -> bool:
    vertical_delta = target[0] - viewpoint[0]
    if direction[0] == 0 and vertical_delta != 0:
        # should not move vertically
        return False
    horizontal_delta = target[1] - viewpoint[1]
    if direction[1] == 0 and horizontal_delta != 0:
        # should not move horizontally
        return False
    return vertical_delta * direction[1] == horizontal_delta * direction[0]
