# NYC Taxi EDA — Yellow Taxi, May 2026

Exploratory data analysis pipeline for one month of NYC TLC Yellow Taxi
trip records: cleaning, univariate/bivariate visualization, outlier
detection, and five quantified business answers, packaged into a
stakeholder-facing PDF report.

## 1. Project Structure

```
nyc-taxi-eda-05-2026/
│
├── data/
│   ├── raw/                          # raw parquet goes here (not committed)
│   └── processed/                    # cleaned data + cleaning_summary.json
│
├── src/
│   ├── data_cleaning.py              # load, clean, flag/cap outliers, log every decision
│   ├── business_analysis.py          # the 5 required business answers + charts
│   ├── visualization.py              # univariate + bivariate chart functions
│   └── utils.py                      # shared helpers (load, derive features, save_fig)
│
├── images/                           # every chart the pipeline produces (.png)
│
├── reports/
│   └── final_report.pdf              # stakeholder report (generated)
│
├── main.py                           # runs the univariate + bivariate EDA suite
├── generate_report.py                # assembles reports/final_report.pdf
├── pyproject.toml
└── README.md
```

## 2. Dataset

- **Source:** [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- **File used:** Yellow Taxi, **May 2026** (`yellow_tripdata_2026-05.parquet`)
- Download the file from the TLC site and place it at:
  ```
  data/raw/yellow_tripdata_2026-05.parquet
  ```
  `data_cleaning.py` validates that this file exists and checks its size
  before doing anything else — if it's missing, the pipeline stops there
  with a clear error rather than failing partway through.

## 3. Environment Setup

This project uses a virtual environment with pinned dependencies declared
in `pyproject.toml`.

### Option A — venv + pip

```powershell
# from the project root
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
# source .venv/bin/activate     # macOS/Linux

python -m pip install --upgrade pip
python -m pip install -e .
```

### Option B — uv

```bash
uv venv
uv sync
```

### Dependencies (pinned in `pyproject.toml`)

```toml
[project]
name = "nyc-taxi-eda-05-2026"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pandas==2.2.3",
    "pyarrow==17.0.0",
    "matplotlib==3.9.2",
    "seaborn==0.13.2",
    "scipy==1.14.1",
    "reportlab==4.2.5",
]
```

> Versions above are a known-good starting point. After installing, run
> `pip freeze > requirements-lock.txt` and use *those* exact versions in
> `pyproject.toml` if you want your environment to be perfectly
> reproducible for grading — pinned means "the versions you actually ran,"
> not just any numbers.

**Verify the environment is ready:**
```powershell
python -c "import pandas, pyarrow, matplotlib, seaborn, scipy, reportlab; print('OK')"
```
If this fails with `ModuleNotFoundError`, the active `python`/`pip` isn't
your venv's — run `python -m pip install <package>` (not bare `pip`) to
guarantee installs go into the currently activated environment.

## 4. How to Run `main.py` End to End

The pipeline has four sequential stages. Each stage reads the output of
the one before it, so **run them in this order**:

```powershell
# 1. Clean the raw data
#    Reads:  data/raw/yellow_tripdata_2026-05.parquet
#    Writes: data/processed/cleaned_taxi_data.parquet
#            data/processed/cleaning_summary.json
python -m src.data_cleaning

# 2. Run the full univariate + bivariate EDA suite
#    Reads:  data/processed/cleaned_taxi_data.parquet
#    Writes: images/*.png  (histograms, KDEs, count plots, box/violin
#            plots, correlation heatmap, hourly demand heatmap, etc.)
python main.py

# 3. Answer the 5 required business questions
#    Reads:  data/processed/cleaned_taxi_data.parquet
#    Writes: business_analysis_summary.json
#            images/business_*.png
python -m src.business_analysis

# 4. Assemble the final stakeholder report
#    Reads:  data/processed/cleaning_summary.json
#            business_analysis_summary.json
#            images/*.png
#    Writes: reports/final_report.pdf
python generate_report.py
```

Console output at each step reports row counts before/after every filter,
percent missing per column with the imputation decision and justification,
and outlier counts with what was done about them (capped vs. kept-and-
flagged) — nothing is dropped silently.

### One-shot (all four stages)

```powershell
python -m src.data_cleaning; python main.py; python -m src.business_analysis; python generate_report.py
```
```bash
# macOS/Linux
python -m src.data_cleaning && python main.py && python -m src.business_analysis && python generate_report.py
```

### Expected outputs after a full run

| Path | What it is |
|---|---|
| `data/processed/cleaned_taxi_data.parquet` | Cleaned, outlier-flagged trip data |
| `data/processed/cleaning_summary.json` | Machine-readable log of every cleaning/outlier decision |
| `images/*.png` | Full univariate + bivariate chart set |
| `business_analysis_summary.json` | The 5 required business answers as structured numbers |
| `images/business_*.png` | Charts for each business answer |
| `reports/final_report.pdf` | Final non-technical stakeholder report |

## 5. Troubleshooting

- **`ModuleNotFoundError: No module named 'src'`** — run commands from the
  project root (where `main.py` lives), not from inside `src/`.
- **`FileNotFoundError: ... cleaning_summary.json`** — stage 1
  (`src.data_cleaning`) hasn't been run yet, or was run before this
  version of the script existed. Re-run it.
- **`No module named pip` inside the venv** — the venv was created without
  pip bundled; run `python -m ensurepip --upgrade`, or recreate the venv.
- Installs going to the wrong Python — always invoke installs as
  `python -m pip install ...` rather than a bare `pip install ...`, to
  guarantee they target the currently active environment.