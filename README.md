Defualt Report
![alt text](image.png)
![alt text](image-1.png)
![alt text](image-2.png)
![alt text](image-3.png)
![alt text](image-4.png)
![alt text](image-5.png)
![alt text](image-6.png)
![alt text](image-7.png)
![alt text](image-8.png)
![alt text](future_climate_hurs.png)
![alt text](future_climate_pr.png)
![alt text](future_climate_tasmax.png)
![alt text](image-9.png)
![alt text](january_tas.png)
![alt text](january_pr.png)
![alt text](imag-10.png)
![alt text](good_days.png)
![alt text](bad_days.png)
![alt text](image-11.png)
![alt text](image-12.png)
# Alpine Ontario Ski Climate Impact Report

A standalone, reproducible Python implementation of the **Alpine Ontario Ski Climate Impact Report** supplied as a Word export.

The project analyzes the supplied NASA NEX-GDDP-CMIP6-derived Parquet dataset for:

- Future climate trends
- January temperature and precipitation trends
- Snowmaking-favorable ("good") days
- Operationally unfavorable ("bad") days
- Ensemble means and 5–95% inter-model ranges

The default settings reproduce the report's stated assumptions: Caledon, Ontario; `ssp585`; 2025–2100.

## Quick start

### 1. Create an environment

Python 3.10+ is recommended.

```bash
python -m venv .venv
```

Activate it:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux**
```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the report

```bash
python -m src.run_report
```

Or:

```bash
python src/run_report.py
```

Generated figures and CSV summaries will be written to `outputs/`.

## Configuration

The default configuration is in `src/config.py`.

Key settings:

- `SCENARIO = "ssp585"`
- `START_YEAR = 2025`
- `END_YEAR = 2100`
- Caledon bounding box from the supplied report
- Good day:
  - `tas <= 265 K` (~ -8.15 °C)
  - `hurs <= 85%`
  - `pr <= 1 mm/day`
- Bad day:
  - `tas >= 283 K` (~ 9.85 °C)
  - `pr >= 5 mm/day`
  - `hurs >= 90%`

The threshold logic follows the exported report's code. In particular, the report's helper combines multiple criteria with logical AND; this project preserves that behavior rather than silently changing the analysis.

## Command-line examples

Use another SSP:

```bash
python -m src.run_report --scenario ssp245
```

Change the period:

```bash
python -m src.run_report --start-year 2030 --end-year 2090
```

Run both:

```bash
python -m src.run_report --scenario ssp370 --start-year 2030 --end-year 2090
```

Choose a different location by editing the latitude/longitude settings in `src/config.py`.

## Outputs

The run creates:

- `outputs/future_climate_tas.png`
- `outputs/future_climate_pr.png`
- `outputs/future_climate_tasmax.png`
- `outputs/january_temperature.png`
- `outputs/january_precipitation.png`
- `outputs/good_days.png`
- `outputs/bad_days.png`
- `outputs/january_summary.csv`
- `outputs/good_bad_summary.csv`
- `outputs/good_bad_by_model_year.csv`

The exact filenames may expand if more variables are enabled.

## Dataset

The repository includes the Parquet dataset supplied with the report:

`data/climate_spatial_means_full.parquet`

The original report describes this as processed NASA NEX-GDDP-CMIP6 data and states that the study uses 2000–2100 climate projections across multiple SSP scenarios and 35 models.

Because the dataset is already included, the project does **not** require Google Cloud credentials or access to the original `nasa-climate-data` bucket.

## Reproducibility notes

The Word export contains notebook code, narrative interpretation, and assumptions but does not contain the original `.ipynb`. This repository therefore reconstructs the executable analysis from the code blocks in that export.

The report itself says to run the notebook with "Run All". The standalone script replaces that notebook workflow with a normal Python entry point.

## Source report

`Climate_Impact_Report.docx` is included in the repository as the source document used to reconstruct the analysis.

## License / data provenance

No license was specified in the supplied report. Add an appropriate license before publishing the repository publicly if required.


## Main notebook report

The primary report is now:

`Alpine_Ontario_Ski_Climate_Impact_Report.ipynb`

Open this file in VS Code and use **Run All**. It contains the written report sections, assumptions, executable analysis cells, figures, tables, interpretations, and appendices.

The original Word export is also included as `Climate_Impact_Report.docx`.
