#!/usr/bin/env python

from argparse import ArgumentParser, FileType
from dataclasses import dataclass
from typing import BinaryIO

import orjson


def main():
    """Run the extractor"""
    parser = ArgumentParser()
    parser.add_argument(
        "file_list",
        type=FileType("r", encoding="utf-8"),
        help="List of MIBiG JSON files to extract PFAM info from",
    )
    parser.add_argument(
        "output", type=FileType("wb"), help="Output file to write data to"
    )
    args = parser.parse_args()
    file_list: list[str] = args.file_list.read().splitlines()
    run(file_list, args.output)


@dataclass
class ClusterPfams:
    """PFam IDs per record"""

    name: str
    pfam_ids: list[str]


def run(file_list: list[str], output: BinaryIO):
    """Extract the PFAM ids"""
    collection: dict[str, ClusterPfams] = {}
    for filename in file_list:
        with open(filename, "rb") as handle:
            data = orjson.loads(handle.read())
        for record in data["records"]:
            name = record["id"]
            ids: list[str] = []
            for feature in record["features"]:
                if feature["type"] != "PFAM_domain":
                    continue
                ids.extend(
                    filter(
                        lambda x: x.startswith("PF"), feature["qualifiers"]["db_xref"]
                    )
                )
            collection[name] = ClusterPfams(name, ids)
    output.write(orjson.dumps(collection))


if __name__ == "__main__":
    main()
