from __future__ import annotations

import argparse
from pathlib import Path

from . import config
from .analysis import run


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Alpine Ontario Ski Climate Impact Report."
    )
    parser.add_argument("--scenario", default=config.SCENARIO)
    parser.add_argument("--start-year", type=int, default=config.START_YEAR)
    parser.add_argument("--end-year", type=int, default=config.END_YEAR)
    parser.add_argument(
        "--data",
        type=Path,
        default=config.DATA_FILE,
        help="Path to the climate_spatial_means_full.parquet dataset.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=config.OUTPUT_DIR,
    )
    args = parser.parse_args()

    run(
        data_file=args.data,
        output_dir=args.output_dir,
        scenario=args.scenario,
        start_year=args.start_year,
        end_year=args.end_year,
    )


if __name__ == "__main__":
    main()
