"""
Converts SwiftData model code into Codable conforming code.
Input: SwiftData struct variables
Output: Codable conforming code (CodingKeys, init from decoder, encode)
"""

# https://www.donnywals.com/making-your-swiftdata-models-codable/
import argparse
import re
from pathlib import Path
from typing import Optional

# consts
enum_template = """
enum CodingKeys: CodingKey {
    case """

init_template = """
required init(from decoder: Decoder) throws {
    let container = try decoder.container(keyedBy: CodingKeys.self)\n"""

encode_template = """
func encode(to encoder: Encoder) throws {
    var container = encoder.container(keyedBy: CodingKeys.self)\n"""


def extract_var_info(lines: str) -> list[tuple[str, str, Optional[str]]]:
    # returns list of (var_name, var_type, is_optional) tuples
    var_info = []
    for line in lines.split("\n"):
        if not line.strip().startswith("var"):
            continue

        match = re.search(r"var (\w+): (\[\w+\]|\w+)(\?)?", line)
        if match:
            var_info.append((match.group(1), match.group(2), match.group(3)))
    return var_info


def create_enum(var_names: list[str]) -> str:
    return f"{enum_template}{', '.join(var_names)}\n}}"


def create_init(var_info: list[tuple[str, str, Optional[str]]]) -> str:
    lines = []
    for var_name, var_type, is_optional in var_info:
        if is_optional is None:
            lines.append(
                f"\tself.{var_name} = try container.decode({var_type}.self, forKey: .{var_name})"
            )
        else:
            lines.append(
                f"\tself.{var_name} = try container.decodeIfPresent({var_type}.self, forKey: .{var_name})"
            )
    return f"{init_template}" + "\n".join(lines) + "\n}"


def create_encode(var_info: list[tuple[str, str, Optional[str]]]) -> str:
    lines = []
    for var_name, _, _ in var_info:
        lines.append(f"\ttry container.encode({var_name}, forKey: .{var_name})")
    return f"{encode_template}" + "\n".join(lines) + "\n}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, help="Input file path")
    args = parser.parse_args()

    raw_input = """
    var id: UUID = UUID()
    var name: String?
    var colors: [Color]
    """

    var_info = extract_var_info(raw_input)
    var_names = [vi[0] for vi in var_info]

    print(create_enum(var_names))
    print()
    print(create_init(var_info))
    print()
    print(create_encode(var_info))
# python swiftdata_models_codable.py | pbcopy
