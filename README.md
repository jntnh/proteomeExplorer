# ProteomeExplorer

Interactive Streamlit app for exploring TDP-43 proteomics data with interactive filtering and visualization.

## Features

- **Password-protected access** – secure your app with a shared password stored in Streamlit secrets
- **Flexible protein filtering** – select proteins by name, tissue detection, FDR threshold, and fold-change magnitude
- **Interactive heatmap** – visualize log2 fold-changes across tissues with annotated cells (FC ± significance stars)
- **Customizable figures** – adjust DPI, width, and height per item before rendering
- **Export** – download heatmaps as PDF or PNG
- **Data table view** – inspect the raw filtered data

## Requirements

- Python 3.8+
- streamlit
- pandas
- seaborn
- matplotlib
- Pillow

## Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd proteomeExplorer
   ```

2. Install dependencies:
   ```bash
   pip install streamlit pandas seaborn matplotlib Pillow
   ```

3. Create `.streamlit/secrets.toml` (this file is gitignored):
   ```toml
   password = "your-password-here"
   ```
   See `.streamlit/secrets.toml.example` for a template.

## Running the App

```bash
streamlit run proteomeExplorer.py
```

The app will prompt for a password on startup. Once authenticated, you will have access to the full interface.

## Data Format

The app expects a CSV file at the path defined by `DATA_PATH` in `proteomeExplorer.py` (default: `data/pivot_fc_and_p_fdr.csv`).

**Expected CSV structure:**
- **Column header:** 3-level MultiIndex
  - Level 0: `FC` (fold-change) or `p-value_FDR` (adjusted p-value)
  - Level 1: tissue type (e.g., `CSF`, `CTX`, `SPC`)
  - Level 2: fraction (e.g., `CSF`, `insoluble`, `soluble`)
- **Row index:** gene/protein names

Example:
```
                FC                                    p-value_FDR
              CSF  CTX         SPC                  CSF  CTX         SPC
              CSF  insoluble soluble               CSF  insoluble soluble
GENE1         0.5    1.2       -0.3              0.01  0.001      0.05
GENE2         NaN    0.8        0.4              NaN   0.02       0.03
```

## Usage

1. **Authenticate** – enter your password
2. **Filter proteins** – use the "Filter Proteins" multiselect to choose specific genes
3. **Select tissues** – choose which tissue types must be detected (CSF, CTX, SPC)
4. **Set thresholds:**
   - Min tissue fractions: protein must be detected in at least N fractions
   - Maximum FDR: adjusted p-value cutoff for significance
   - Minimum absolute fold-change: magnitude threshold
5. **Toggle display options:**
   - Show only significant proteins (< FDR threshold)
   - Show significance stars instead of full p-values
6. **Adjust figure settings** – customize DPI, width, and height
7. **Download** – export the heatmap as PDF or PNG

## License

MIT
