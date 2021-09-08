# Import packages that are needed
import pandas as pd  # tested with version 0.22.0
import matplotlib as mpl
import matplotlib.pyplot as plt  # tested with version 2.1.2
import seaborn as sns  # tested with version 0.8.1
import matplotlib.gridspec

from .summary_stats import get_merged

mpl.use("Agg")

ALPHA = 0.1  # nominally significant p-value threshold
WILCOXON_STAT = "Wilcoxon rank-sum stat"  # Set up column names
WILCOXON_P_VALUE = "Wilcoxon rank-sum p-value"
# Set the color palette for the bar plot, where significant = red = C2 and Not significant = C0 = blue
PALETTE = {"Bonferoni": "C3", "Nominal": "C0"}
COMBO_FIG_SIZE = (15, 6)  # (25, 10)
BARPLOT_FIG_SIZE = (8, 4.3)  # (15, 8)


def process_data(locations):
    if locations["data"]["resource"]["format"].lower() == "gct":
        measure1 = "before"
        measure2 = "after"
    elif locations["data"]["resource"]["format"].lower() == "csv":
        measure1 = "urine"
        measure2 = "serum"
    summaryStats = pd.read_csv(locations["summary"]["path"], sep=",")
    # Get significant values and measure2/measure1 dataframes
    summaryStats_significant = summaryStats.iloc[
        summaryStats[WILCOXON_P_VALUE]
        .where(summaryStats[WILCOXON_P_VALUE] < ALPHA)
        .dropna()
        .index
    ]
    # Separate measure1 and measure2 samples, sort by t-test statistic, and set the significance of each metabolite
    summaryStats_significant_measure1 = summaryStats_significant[
        summaryStats_significant["Sample Type"].str.match(measure1)
    ]
    summaryStats_significant_measure1 = summaryStats_significant_measure1.sort_values(
        by=WILCOXON_STAT
    )
    summaryStats_significant_measure1["Significance"] = "Nominal"
    summaryStats_significant_measure1.loc[
        summaryStats_significant_measure1[WILCOXON_P_VALUE]
        < (0.05 / len(summaryStats.index)),
        "Significance",
    ] = "Bonferoni"  # These are Bonferroni significant

    summaryStats_significant_measure2 = summaryStats_significant[
        summaryStats_significant["Sample Type"].str.match(measure2)
    ]
    summaryStats_significant_measure2 = summaryStats_significant_measure2.sort_values(
        by=WILCOXON_STAT
    )
    summaryStats_significant_measure2["Significance"] = "Nominal"
    summaryStats_significant_measure2.loc[
        summaryStats_significant_measure2[WILCOXON_P_VALUE]
        < (0.05 / len(summaryStats.index)),
        "Significance",
    ] = "Bonferoni"

    merged, droppable, case, control = get_merged(locations)

    # Remove metabolites that contain at least 1 NA value
    naMolecules = []
    for col in merged:
        if merged.loc[:, col].isna().sum() > 0:
            naMolecules.append(col)
    merged_naRemoved = merged.drop(naMolecules, axis=1)
    csvdropColumns = droppable + [
        "Sample Name",
        "Extraction Protocol",
        "Extraction Method",
        "Spectrum Protocol",
        "Status",
        "Sample Type",
    ]
    dropColumns = []
    for drop in csvdropColumns:
        if drop in merged_naRemoved.columns.values:
            dropColumns.append(drop)

    merged_naRemoved = merged_naRemoved.drop(dropColumns, axis=1)

    # Rename the row index of the dataframe to the sample name
    sampleNames = merged["Sample Name"].values.tolist()
    sampleDict = {}
    for k in range(len(merged_naRemoved.index.values.tolist())):
        sampleDict[merged_naRemoved.index.values.tolist()[k]] = sampleNames[k]
    merged_naRemoved.rename(index=sampleDict, inplace=True)

    measure1_df = merged[merged["Sample Type"] == measure1]
    measure1_significant = measure1_df[summaryStats_significant_measure1["Molecule"]]

    # Remove metabolites that contain at least 1 NA value
    naMolecules = []
    for col in measure1_significant.columns:
        if measure1_significant.loc[:, col].isna().sum() > 0:
            naMolecules.append(col)
    measure1_significant = measure1_significant.drop(naMolecules, axis=1)

    # Rename the row index of the dataframe to the sample name
    sampleNames = measure1_df["Sample Name"].values.tolist()
    sampleDict = {}
    for k in range(len(measure1_significant.index.values.tolist())):
        sampleDict[measure1_significant.index.values.tolist()[k]] = sampleNames[k]
    measure1_significant.rename(index=sampleDict, inplace=True)

    # Separate out the measure2 samples and filter those that are nominally significant (as defined above)
    measure2_df = merged[merged["Sample Type"] == measure2]
    measure2_significant = measure2_df[summaryStats_significant_measure2["Molecule"]]

    # Remove metabolites that contain at least 1 NA value
    naMolecules = []
    for col in measure2_significant.columns:
        if measure2_significant.loc[:, col].isna().sum() > 0:
            naMolecules.append(col)
    measure2_significant = measure2_significant.drop(naMolecules, axis=1)

    # Rename the row index of the dataframe to the sample name
    sampleNames = measure2_df["Sample Name"].values.tolist()
    sampleDict = {}
    for k in range(len(measure2_significant.index.values.tolist())):
        sampleDict[measure2_significant.index.values.tolist()[k]] = sampleNames[k]
    measure2_significant.rename(index=sampleDict, inplace=True)

    return {
        "summ_stats_measure1": summaryStats_significant_measure1,
        "summ_stats_measure2": summaryStats_significant_measure2,
        "heatmap_all_samples": merged_naRemoved,
        "heatmap_measure1_significant": measure1_significant,
        "heatmap_measure2_significant": measure2_significant,
    }


def create_bar_plots(
    x,
    y,
    title,
    figsize=BARPLOT_FIG_SIZE,
    hue=None,
    palette=PALETTE,
    save_path=None,
    font_scale=1,
    ax=None,
):

    plt.figure(figsize=figsize)
    sns.set(font_scale=font_scale)
    sns.barplot(y=y, x=x, hue=hue, palette=PALETTE, dodge=False, ax=ax)
    plt.legend(loc="upper right")
    plt.title(title)


def create_plot(
    cluster_data,
    barplot_data,
    super_title,
    heatmap_title,
    barplot_title,
    gridspec_dict,
    fig_size,
    save_path,
    combo_plot=False,
    font_scale=1,
):

    sns.set(font_scale=font_scale)
    plot = sns.clustermap(cluster_data, figsize=fig_size)
    if super_title:
        plot.fig.suptitle(super_title)
    plot.ax_heatmap.set_title(heatmap_title, pad=45)
    plot.ax_heatmap.xaxis.set_ticklabels(
        ticklabels=plot.ax_heatmap.xaxis.get_ticklabels(), rotation=90
    )

    if combo_plot:
        plot.gs.update(
            left=gridspec_dict["clustermap_left"],
            right=gridspec_dict["clustermap_right"],
        )
        gs2 = matplotlib.gridspec.GridSpec(
            1,
            1,
            left=gridspec_dict["barplot_left"],
            right=gridspec_dict["barplot_right"],
        )
        ax2 = plot.fig.add_subplot(gs2[0])
        x = barplot_data["Molecule"].values
        y = barplot_data[WILCOXON_STAT].values
        hue = barplot_data["Significance"].values
        create_bar_plots(
            y, x, hue=hue, title=barplot_title, font_scale=font_scale, ax=ax2
        )
        ax2.set_title(barplot_title)
        ax2.set_xlabel(WILCOXON_STAT)
        ax2.set_ylabel("Molecule")
        ax2.legend(title="Significance")

    plot.savefig(save_path, dpi=300)
    return save_path.rsplit("/", 1)[1]


def graphics(locations):
    plot_data = process_data(locations)
    summ_stats_measure1 = plot_data.get("summ_stats_measure1")
    summ_stats_measure2 = plot_data.get("summ_stats_measure2")
    heatmap_all_samples = plot_data.get("heatmap_all_samples")
    heatmap_measure1_significant = plot_data.get("heatmap_measure1_significant")
    heatmap_measure2_significant = plot_data.get("heatmap_measure2_significant")

    plot_attrs = {
        "title": {
            "cluster all": "Clustermap - All Samples",
            "cluster measure2": "Clustermap - measure2 Samples",
            "cluster measure1": "Clustermap - measure1 Samples",
            "barplot measure2": "Nominally Significant Metabolites (p < 0.1) - measure2",
            "barplot measure1": "Nominally Significant Metabolites (p < 0.1) - measure1",
            "super measure2": "Nominally Significant Metabolites and measure2 Clustermap",
            "super measure1": "Nominally Significant Metabolites and measure1 Clustermap",
        },
        "filepath": {
            "cluster all": "/tmp/heatmap_all.png",
            "combo measure1": "/tmp/measure1_heatmap_stat_sig_metabolites.png",
            "combo measure2": "/tmp/measure2_heatmap_stat_sig_metabolites.png",
        },
    }

    save_path = plot_attrs["filepath"]["cluster all"]
    title = plot_attrs["title"]["cluster all"]

    created_files = []

    heatmap_all_plotname = create_plot(
        heatmap_all_samples,
        None,
        super_title=None,
        heatmap_title=title,
        barplot_title=None,
        gridspec_dict=None,
        fig_size=BARPLOT_FIG_SIZE,
        save_path=save_path,
    )
    created_files.append(heatmap_all_plotname)

    positions = {
        "barplot_left": 0.0,
        "barplot_right": 0.45,
        "clustermap_left": 0.50,
        "clustermap_right": 1.0,
    }

    save_path = plot_attrs["filepath"]["combo measure2"]
    super_title = plot_attrs["title"]["super measure2"]
    cluster_title = plot_attrs["title"]["cluster measure2"]
    barplot_title = plot_attrs["title"]["barplot measure2"]
    combo_measure2 = create_plot(
        heatmap_measure2_significant,
        summ_stats_measure2,
        super_title=super_title,
        heatmap_title=cluster_title,
        barplot_title=barplot_title,
        gridspec_dict=positions,
        fig_size=COMBO_FIG_SIZE,
        save_path=save_path,
        combo_plot=True,
    )
    created_files.append(combo_measure2)

    save_path = plot_attrs["filepath"]["combo measure1"]
    super_title = plot_attrs["title"]["super measure1"]
    cluster_title = plot_attrs["title"]["cluster measure1"]
    barplot_title = plot_attrs["title"]["barplot measure1"]
    combo_measure1 = create_plot(
        heatmap_measure1_significant,
        summ_stats_measure1,
        super_title=super_title,
        heatmap_title=cluster_title,
        barplot_title=barplot_title,
        gridspec_dict=positions,
        fig_size=COMBO_FIG_SIZE,
        save_path=save_path,
        combo_plot=True,
    )
    created_files.append(combo_measure1)

    return created_files
