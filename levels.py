"""Level layout data. Each level is described declaratively (tile columns/rows)
and turned into actual game objects by Level.build() in game.py.

Tile row 0 is the top of the screen; ground_row is the first row of solid
ground. Columns are 0-indexed tile positions along the level's width.
"""

LEVEL_1 = {
    "name": "1-1 Green Hills",
    "width": 95,
    "ground_row": 14,
    # inclusive (start, end) tile-column ranges with no ground -> pits
    "gaps": [(9, 10), (27, 28), (47, 49), (66, 67)],
    # (col, row, kind) kind is "brick" or "question"
    "blocks": [
        (12, 10, "question"),
        (18, 10, "brick"), (19, 10, "question"), (20, 10, "brick"),
        (31, 9, "question"),
        (39, 10, "brick"), (40, 10, "brick"), (41, 10, "brick"),
        (56, 9, "question"), (57, 9, "question"),
        (71, 9, "brick"),
    ],
    "pipes": [(16, 2), (35, 3), (53, 2), (73, 3)],
    "goombas": [23, 42, 59, 75, 81],
    "coins": [(12, 9), (31, 8), (56, 8), (57, 8), (63, 9), (64, 9), (65, 9)],
    "stairs_up": {"start_col": 84, "steps": 5},
    "flag_col": 93,
}

LEVEL_2 = {
    "name": "1-2 Underground Rush",
    "width": 110,
    "ground_row": 14,
    "gaps": [(6, 7), (20, 22), (40, 41), (58, 60), (80, 82), (95, 96)],
    "blocks": [
        (10, 10, "question"),
        (15, 9, "brick"), (16, 9, "question"), (17, 9, "brick"),
        (28, 10, "question"), (29, 10, "question"),
        (44, 9, "brick"), (45, 9, "brick"), (45, 8, "question"),
        (63, 9, "question"), (64, 9, "brick"), (65, 9, "question"),
        (85, 9, "brick"), (86, 9, "brick"), (87, 9, "brick"),
    ],
    "pipes": [(12, 2), (32, 3), (48, 2), (68, 3), (90, 3)],
    "goombas": [9, 25, 34, 46, 54, 62, 71, 83, 91, 98],
    "coins": [(10, 8), (28, 9), (29, 9), (63, 8), (64, 8), (65, 8), (100, 9), (101, 9)],
    "stairs_up": {"start_col": 99, "steps": 6},
    "flag_col": 108,
}

LEVELS = [LEVEL_1, LEVEL_2]
