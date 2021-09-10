import glob
import json
import os
import re
from typing import Dict
from typing import List
from typing import Union


def load_json(cache_filename: str):

    with open(cache_filename, "r") as f:

        cache = json.load(f)

    return cache


def cache_object_to_json(obj: Union[List, Dict], cache_filename: str):

    with open(cache_filename, "w") as f:

        json.dump(obj, f, indent=4)


def fetch_cached_blocks(cached_files: List):

    cached_blocks = []
    for cache_file in cached_files:

        block_id_of_cache = re.findall("(\d+).json", cache_file)
        cached_blocks.append(int(block_id_of_cache[0]))

    return cached_blocks


def fetch_cached_files(cache_dir: str):

    cached_files = glob.glob(os.path.join(cache_dir, "*.json"))

    return cached_files
