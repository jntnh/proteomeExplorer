import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from threading import RLock
from PIL import Image
import io

_lock = RLock()
pixel_limit = 2 * Image.MAX_IMAGE_PIXELS

def stars(p):
    if pd.isna(p):
        return ""
    elif p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    return ""

def valid_figure_size(width, height, dpi, pixel_limit):
    x_pixel = width * dpi
    y_pixel = height * dpi
    total_pixel = x_pixel * y_pixel

    if total_pixel < pixel_limit:
        return True
    else:
        return False

data = pd.read_csv(
    "data/pivot_fc_and_p_fdr.csv", 
    index_col=0, 
    header=[0,1, 2]
)

data = data.drop(columns=[('p-value_FDR', 'sum_significant', 'Unnamed: 11_level_2')])

with st.sidebar:
    st.markdown('*Hallo*')

st.title("Explore TDP-Proteome")
'Mithilfe dieses Tools können verschiedene Filtereinstellungen vorgenommen werden. Anhand dieser Kriterien wird anschließend eine Heatmap erstellt, welche die log2 Fold-Changes in den verschiedenen Geweben/Biomaterialien anzeigt.'

genes = st.multiselect(
    "Filter Proteins",
    options=list(data.index),
    #default=["NEFL"]
)

tissue = st.pills(
    "Protein must be detected in tissue:",
    options=["CSF", "CTX insoluble", "CTX soluble", "SPC insoluble", "SPC soluble"],
    default="CSF",
    selection_mode='multi'
)

notna_threshold = st.number_input("In how many tissue fractions must the protein at least be present?",
                                  min_value=1,
                                  max_value=5)


fdr_threshold = st.slider(
    "Maximum FDR",
    min_value=0.001,
    max_value=0.1,
    value=0.05
)

fc_threshold = st.slider(
    "Minimum absolute Fold Change",
    min_value=0.0,
    max_value=5.0,
    value=0.5
)

only_sig = st.checkbox(
    f"Show only significant proteins (adjusted p-value < {fdr_threshold})",
    value=True
)

only_stars = st.checkbox(
    "Hide detailed p-values (show only significance stars)",
    value=True
)

fc = data["FC"]
pvals = data["p-value_FDR"]

selected = fc.copy()

if genes:
    selected = selected.loc[genes]

if only_sig:

    mask = (
        pvals
        .min(axis=1)
        < fdr_threshold
    )

    selected = selected.loc[mask]

mask_fc = (
    selected.abs()
    .max(axis=1)
    >= fc_threshold
)

selected = selected.loc[mask_fc]

for t in tissue:
    if t == "CSF":
        selected = selected.loc[selected[('CSF', 'CSF')].notna()]
    else:
        selected = selected.loc[selected[(t.split()[0], t.split()[1])].notna()]

selected = selected.dropna(thresh=notna_threshold)

selected = selected.sort_values(
    by=selected.columns[0],
    ascending=False
)

annot = fc.loc[selected.index].copy().astype(object)

for row in fc.loc[selected.index].index:
    for col in fc.columns:

        fc_val = fc.loc[row, col]
        p_val = pvals.loc[row, col]

        if pd.isna(fc_val):
            annot.loc[row, col] = ""
        else:
            if only_stars:
                annot.loc[row, col] = (
                f"{fc_val:.2f}{stars(p_val)}"
            )
            else:
                annot.loc[row, col] = (
                    f"{fc_val:.2f}\n"
                    f"p={p_val:.2g} {stars(p_val)}"
                )

st.markdown('## Heatmap')
with st.expander('Figure settings'):
    dpi = st.number_input('Figure dpi:', 50, 600, 150)
    width = st.number_input('Figure width:', 0, None, 8)
    height_per_item = st.number_input('Figure height per item:', 0.0, None, 0.6)

if len(selected) == 0:
    st.warning('No matches for your filter preferences. Heatmap cannot be generated.', icon="⚠️")

elif not valid_figure_size(width, height_per_item*len(selected), dpi, pixel_limit):
    st.warning('Your Heatmap is too large and cannot be generated. Reduce the number of selected items or adjust figure properties (width, height or dpi)', icon="⚠️")

else:
    with _lock:
        fig, ax = plt.subplots(
            figsize=(width, height_per_item * len(selected),),
            dpi=dpi
        )

        sns.heatmap(
            selected,
            cmap="coolwarm",
            center=0,
            ax=ax,
            annot=annot,
            fmt="",
            annot_kws={"size": 9}, 
            cbar_kws={"shrink": .5},
        )

        plt.ylabel('Gene Name')
        plt.title(f'Heatmap showing log2FC for different tissues')


        try:
            st.pyplot(fig, dpi=dpi)

            download_format = st.menu_button('Download figure as:', ['PDF', 'PNG'])
            if download_format is not None:
                buf = io.BytesIO()
                fig.savefig(buf, format=download_format.lower(), bbox_inches='tight')
                buf.seek(0)

                st.download_button('Download Figure', buf, f'figure.{download_format.lower()}')

        except Image.DecompressionBombError:
            st.error(
                "Die erzeugte Abbildung ist zu groß und kann nicht dargestellt werden.\n\n"
                "Bitte reduzieren Sie die Auflösung oder die Größe der Grafik."
            )

        except Exception as e:
            st.error(f"Fehler beim Erzeugen der Grafik:\n{e}")

        

st.markdown('## DataFrame')

data.loc[selected.index]