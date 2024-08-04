# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Gene set analysis results summary
#
# ## Drugs & pathways found
#
# This notebook gives summary analysis data showing:
#
# * which ATC code gene sets (i.e. genes identified from the protein targets of the drugs within that set) are most associated with genes implicated in a disease GWAS by a hybrid mapping of those genes to disease SNPs.
# * which GO pathways are associated with the same.
#
# The following SNP-gene annotation methods are analysed:
# * Positional - SNPs are assigned to genes based on their proximity to the gene (within a 10kb window)
# *
# hybrid, hybrid-both, QTL and positional SNP-gene annotation
#
# The analysis is run for each SNP-gene annotation using the following drug target interaction sets:
#
# * DUGGIE   - a set of ATC coded drugs derived from the 8 different drug-gene interaction sources.
# * STITCH   - the largest drug-gene interaction source contributing to DUGGIE
# * NOSTITCH - the DUGGIE target set, minus all STITCH targets.
#
# *Uncorrected P-values used throughout, except for Mann-Whitney and comparison of DUGGIE and STITCH analysis performance, where Q-values are used*
#
# The analysis attempts to determine which DTI set and annotation method is most effective at identifying known treatment drugs for a disease (and also not falsely identifying other drugs not used to treat).

# +
import os
import sys
import pandas as pd
import numpy as np

import math

sys.path.append("../lib/")

# #!pip install matplotlib
# %matplotlib inline
import matplotlib.pyplot as plt
import seaborn as sns

import statsmodels.api as sm
import scipy.stats as stats

from IPython.display import display, HTML

import subprocess

import results_display as rdisp

from sklearn.metrics import roc_curve, auc
from sklearn.metrics import roc_auc_score
# -

HTML(
    """<script>
code_show=true; 
function code_toggle() {
 if (code_show){
 $('div.input').hide();
 } else {
 $('div.input').show();
 }
 code_show = !code_show
} 
$( document ).ready(code_toggle);
</script>
The raw code for this IPython notebook is by default hidden for easier reading.
To toggle on/off the raw code, click <a href="javascript:code_toggle()">here</a>."""
)

# +
# ** Change these values specific to the pipleine runs of interest **
gwas = "MDD"
run_id = "ch5"

dtis = ["duggie", "stitch"]

annots = [
    "prox",
    "alleqtlbrain",
    "alleqtlbrainhybrid",
    "alleqtlbrainhybridboth",
    "allbrain",
    "allbrainhybrid",
    "allbrainhybridboth",
    "alleqtlblood",
    "alleqtlbloodhybrid",
    "alleqtlbloodhybridboth",
    "alleqtltissues",
    "alleqtltissueshybrid",
    "alleqtltissueshybridboth",
    "alltissues",
    "alltissueshybrid",
    "alltissueshybridboth",
]

# +
pd.set_option("display.max_colwidth", -1)
pd.options.display.max_rows = 1000
pd.set_option('display.precision', 3)

data_path = "../data/"
magma_results_dir = data_path + "magma_analysis/magma_results/"
summary_results_dir = data_path + "summaries/"

N_GENE_THRESH = 4
SIGNIF_THRESH = 0.05
MAGMA_VER = 109
# -

gitspec = subprocess.check_output(
    ["git", "describe", "--all", "--dirty", "--long"]
).strip()
print("This notebook was run on git revision " + str(gitspec, "utf-8"))

# # Analysis of DUGGIE vs STITCH

# +
# All ATC genesets
atc_genesets_df = pd.read_csv(
    data_path + "target-dbs/all_dgi_targets_atc_ensembl.csv",
    header=None,
    sep="\t",
    index_col=0,
)

atc_nostitch_genesets_df = pd.read_csv(
    data_path + "target-dbs/nostitch_dgi_targets_atc_ensembl.csv",
    header=None,
    sep="\t",
    index_col=0,
)

stitch_genesets_df = pd.read_csv(
    data_path + "target-dbs/stitch_dgi_targets_atc_ensembl.csv",
    header=None,
    sep="\t",
    index_col=0,
)

# All GO genesets
go_genesets_df = pd.read_csv(
    "../data/magma_analysis/GO_ALL_PC_20-2000_MAGMA.LH.ensembl.druggable.txt",
    header=None,
    sep="\t",
    index_col=0,
)
# All GO + ATC genesets
genesets_df = pd.concat([atc_genesets_df, go_genesets_df])

nostitch_genesets_df = pd.concat([atc_nostitch_genesets_df, go_genesets_df])

# Ensembl to HGNC translation table
gene_hgnc_df = pd.read_csv(
    "../data/wrangling/NCBI37.3.ensembl.gene.loc",
    sep="\t",
    header=None,
    names=["Ensembl", "1", "chrom", "chromStart", "chromEnd", "HGNC"],
)[["Ensembl", "HGNC", "chrom"]]


duggie_drug_dfs = []
stitch_drug_dfs = []
nostitch_drug_dfs = []

dti_df_sets = [duggie_drug_dfs, stitch_drug_dfs, nostitch_drug_dfs]

for dti in dtis:
    for annot in annots:
        newlist = rdisp.read_results_files(
            gwas, annot, magma_results_dir, run_id, dti, MAGMA_VER
        )
        newlist = newlist[newlist["NGENES"] >= N_GENE_THRESH]
        dti_df_sets[dtis.index(dti)].append(newlist)


# -


# Set up some plotting variables
fig_width = 18
fig_height = 5
fig_height2 = 34


# # DRUG p-value histograms, QQ plots and correlations
#
# These are MAGMA calculated drug gene set p-values, for ATC coded drugs with targets from either DUGGIE, STITCH or DUGGIE without STITCH drugs (NOSTITCH).
#
# **Histograms**
# * For a uniform, flat distribution, there are very little true positives.
# * For a left hand (orange) peak with the rest of the distribution mainly uniform and flat, there are many true positives and the q-value is a good estimate.
# * For a messy distribution or a right hand peak (near 1), there may be issues with the analysis. FDR assumptions may be broken and there are very few true positives.
#
# **QQ plots**
# * A plot following the expected (normal) distribution indicates that there is no evidence against the null hypothesis
# * A plot with a diverging lower tail indicates a higher proportion of low p-values / lower p-values. This indicates that the null hypothesis could be false.
# * A plot with both tails diverging is indeterminate, and may indicate issues with the analysis.
#
# **Scatter plots**
# * More treatment drugs occurring one side of the equivalence line indicates that the relevant analysis (nearest axis) is more effective at identifying them (higher p-values). The opposite effect for non-treatment drugs is also desirable.
#
# **Scatter plots banded by difference in targets between DTI DBs**
#
# **Significantly associated treatment drug ratio / number of non-treatment drugs found significant**
# * Method effectiveness comparison measure. The higher %age of treatment drugs found and the lower the number of non-treatment drugs found to be associated, the better.
#
# **Mann-Whitney U test**
# * Gives the p-value that for this method, the population of p-values of treatment drugs is different from the population of non-treatment drugs.
#
# ## For DUGGIE
#
# ### Histograms of DUGGIE drug p-values

def generate_plot_list(count):
    plot_list = []
    i=1

    # Create just enough plots for the annotation data sets we have
    while (i <= count):
        plot_list.append([i, i+1])
        i = i + 2

    return plot_list


# +
plot_list = generate_plot_list(len(annots))
plt.figure(figsize=(fig_width, fig_height * len(annots))).subplot_mosaic(plot_list)

ax1 = plt.gca()
dti = "duggie_nocyp"

for annot in annots:
    plt.subplot(len(plot_list), len(plot_list[0]), annots.index(annot) + 1, sharex=ax1, sharey=ax1)
    rdisp.plot_density_histogram(
        gwas,
        annot,
        "drug",
        dti_df_sets[dtis.index(dti)][annots.index(annot)],
        "P " + annot + " " + dti,
    )
# -

# ### QQ plots of DUGGIE DRUG p-values

# +
fig = plt.figure(figsize=(fig_width, fig_height * len(annots))).subplot_mosaic(plot_list)

dti = "duggie_nocyp"
for annot in annots:
    ax2 = plt.subplot(len(plot_list), len(plot_list[0]), annots.index(annot) + 1)
    dti_df_sets[dtis.index(dti)][annots.index(annot)][
        "Z " + annot + " " + dti
    ] = stats.norm.ppf(
        dti_df_sets[dtis.index(dti)][annots.index(annot)]["P " + annot + " " + dti]
    )
    sm.qqplot(
        dti_df_sets[dtis.index(dti)][annots.index(annot)]["Z " + annot + " " + dti],
        line="45",
        ax=ax2,
    )
    plt.ylabel("measured " + annot + " z-score")
    plt.xlabel("expected norm quantiles")
    dummy = plt.title("QQ-plot, " + annot + " annotation drug p-vals")
# -

# ## For STITCH
#
# ### Histograms of STITCH drug p-values

# +
plt.figure(figsize=(fig_width, fig_height * len(annots))).subplot_mosaic(plot_list)
ax1 = plt.gca()

dti = "stitch_nocyp"
for annot in annots:
    plt.subplot(len(plot_list), len(plot_list[0]), annots.index(annot) + 1, sharex=ax1, sharey=ax1)
    rdisp.plot_density_histogram(
        gwas,
        annot,
        "drug",
        dti_df_sets[dtis.index(dti)][annots.index(annot)],
        "P " + annot + " " + dti,
    )
# -

# ### QQ plots of STITCH DRUG p-values

# +
fig = plt.figure(figsize=(fig_width, fig_height * len(annots))).subplot_mosaic(plot_list)

dti = "stitch_nocyp"
for annot in annots:
    ax2 = plt.subplot(len(plot_list), len(plot_list[0]), annots.index(annot) + 1)
    dti_df_sets[dtis.index(dti)][annots.index(annot)][
        "Z " + annot + " " + dti
    ] = stats.norm.ppf(
        dti_df_sets[dtis.index(dti)][annots.index(annot)]["P " + annot + " " + dti]
    )
    sm.qqplot(
        dti_df_sets[dtis.index(dti)][annots.index(annot)]["Z " + annot + " " + dti],
        line="45",
        ax=ax2,
    )
    plt.ylabel("measured " + annot + " z-score")
    plt.xlabel("expected norm quantiles")
    dummy = plt.title("QQ-plot, " + annot + " annotation drug p-vals")
# -

# ### Comparison of DUGGIE and STITCH analysis performance

# #### Scatter plot of STITCH vs DUGGIE results
#
# * Blue dots are drugbank drugs with an ATC code listed for the indication
# * All other drugs are pink
# * Drugs with significant Q values for STITCH only, DUGGIE only, both DUGGIE and STITCH and neither are shown as down triangles, up triangles, diamonds and points respectively.

# +
plt.figure(figsize=(fig_width, fig_height * len(annots))).subplot_mosaic(plot_list)

axlimit = 9

dti1 = "stitch_nocyp"
dti2 = "duggie_nocyp"

for annot in annots:
    plt.subplot(len(plot_list), len(plot_list[0]), annots.index(annot) + 1)
    rdisp.plot_drug_scatter(
        gwas,
        annot + " " + dti1,
        dti_df_sets[dtis.index(dti1)][annots.index(annot)],
        annot + " " + dti2,
        dti_df_sets[dtis.index(dti2)][annots.index(annot)],
        "P",
        axlimit,
    )
# -
# ### DUGGIE vs STITCH p-vals with colour banded difference in gene counts
#
# plots of DUGGIE vs STITCH p-values with the increase in the number of genes DUGGIE has over STITCH highlighted (It is expected the drugs for which the log p-values differ most between STITCH and DUGGIE - i.e. those furthest from the line y=x - to have the greatest difference in the number of genes). Based on the difference range quartiles, the colour groups are split at differences of 4, 11 and 22 genes.
#
# (N.B. This only show drugs present in both sets - additional DUGGIE drugs are not included)

# +
plt.figure(figsize=(fig_width, fig_height * len(annots))).subplot_mosaic(plot_list)

axlimit = 13

dti1 = "stitch_nocyp"
dti2 = "duggie_nocyp"

diffs = []

for annot in annots:
    plt.subplot(len(plot_list), len(plot_list[0]), annots.index(annot) + 1)
    df = rdisp.plot_drug_genediff_scatter(
        gwas,
        annot + " " + dti1,
        dti_df_sets[dtis.index(dti1)][annots.index(annot)],
        annot + " " + dti2,
        dti_df_sets[dtis.index(dti2)][annots.index(annot)],
        "P",
        axlimit,
    )
    diffs.append(df)
# -

# ### Scatter plot/regression of DUGGIE p-value difference vs geneset size difference with STITCH

# +
# Diff on x-axis, p-val on y
plt.figure(figsize=(fig_width, fig_height * len(annots))).subplot_mosaic(plot_list)

for i in range(0, len(diffs)):
    df = diffs[i]

    # p-diffs = -log(q_duggie) - -log(q_stitch)
    # -ve diff => STITCH better, +ve DUGGIE better
    df["p-diffs"] = df.iloc[:, 11] - df.iloc[:, 10]

    slope, intercept, r_value, p_value, std_err = stats.linregress(
        df["diff"], df["p-diffs"]
    )

    annot_type = df.columns[2].split()[1 - 3]

    df, group_labels, colours = rdisp.group_drugs(df, gwas)

    groups = df.groupby("colour_id")

    plt.subplot(len(plot_list), len(plot_list[0]), i + 1)

    for name, group in groups:
        plt.scatter(
            group["diff"],
            group["p-diffs"],
            label=group_labels[int(name)],
            c=colours[int(name)],
        )

    plt.xlabel("DUGGIE/STITCH drug gene difference")
    plt.ylabel("-log(p value) absolute difference between DUGGIE & STITCH")
    plt.title(annot_type + " q-value difference vs geneset size difference")

    ax2 = plt.gca()
    plt.text(
        0,
        -0.1,
        "r_value = "
        + "{0:.5f}".format(r_value)
        + ", slope = "
        + "{0:.5f}".format(slope)
        + ", err "
        + "{0:.5f}".format(std_err),
        transform=ax2.transAxes,
    )

    legend = ax2.legend([])
    plt.legend()
    dummy = plt.plot(df["diff"], slope * df["diff"] + intercept, i)
# -

# ## Mann-Whitney tests for each of these groups

# ### Annotation/DTI DB performance stats for identifying treatment drugs
#
# * Positives - Number of drugs found to have a significant association with the disease
# * True Positives - Number of significant drugs that are treatment drugs
# * False Positives - Number of significant drugs that are not treatment drugs
# * Negatives - Number of drugs found not to have a significant association with the disease
# * True Negatives - Number of significant drugs that are not treatment drugs
# * False Negatives - Number of significant drugs that are treatment drugs
#
#
# * Sensitivity is the ability to correctly detect a treatment drug (Fewer false negatives is good)
# * Specificity is the ability to correctly  reject a non-treatment drug (Fewer false positives is good)
# * A smaller Mann-Whitney p-value implies the analysis method is better at discerning between treatment and non-treatment drug sets
# * A significant Fisher exact test p-value tells us there is a significant association between the analysis method results and the classification of treatment/non-treatment drugs.
#

# +
#### Comparison of duggie/stitch of shared drugs
#Only looking at drugs present in both databases.

#df1 = rdisp.show_treatment_drug_stats(diffs, 7, SIGNIF_THRESH)
#df2 = rdisp.show_treatment_drug_stats(diffs, 3, SIGNIF_THRESH)
#display(df1.append(df2))
# -

# # Comparison of duggie/stitch for all drugs
# Duggie covers more drugs than stitch.

# +
stats_df = pd.DataFrame()
for dti in dtis:
    for annot in annots:
        df = dti_df_sets[dtis.index(dti)][annots.index(annot)]
        df, group_labels, colours = rdisp.group_drugs(df, gwas)

    stats_df = stats_df.append(
        rdisp.show_treatment_drug_stats(dti_df_sets[dtis.index(dti)], 3, SIGNIF_THRESH)
    )

display(stats_df)
# -

# #### ROC curves and AUC for all analyses

# +
roc_fig_unit = 10
plt.figure(figsize=(roc_fig_unit, roc_fig_unit)).subplot_mosaic([[1]])
lw = 2

for dti in ["duggie_nocyp", "stitch_nocyp"]:
    for annot in annots:
        df = dti_df_sets[dtis.index(dti)][annots.index(annot)]
        ## Replace any inf Z-score (from p-val of 1)
        df.replace(np.inf, 0, inplace=True)
        if df["colour_id"].any():
            fpr, tpr, thresholds = roc_curve(
                (df["colour_id"] != 0), 1 - df.iloc[:, [4]]
            )
            roc_auc = auc(fpr, tpr)
            plt.plot(
                fpr, tpr, lw=lw, label=dti + " " + annot + " (area = %0.2f)" % roc_auc
            )

plt.plot([0, 1], [0, 1], color="navy", lw=lw, linestyle="--")
plt.xlim([0.0, 1.01])
plt.ylim([0.0, 1.05])
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("Receiver operating characteristics")
plt.legend()
plt.show()
# -

# #### what are the treatment drugs stitch finds over duggie?

for annot in annots:
    stitch_treatment_df = dti_df_sets[dtis.index("stitch_nocyp")][annots.index(annot)]
    stitch_treatment_df = stitch_treatment_df[stitch_treatment_df["colour_id"] != 0]
    stitch_treatment_df = stitch_treatment_df[
        stitch_treatment_df["Q " + annot + " stitch_nocyp"] < SIGNIF_THRESH
    ]

    duggie_treatment_df = dti_df_sets[dtis.index("duggie_nocyp")][annots.index(annot)]
    duggie_treatment_df = duggie_treatment_df[duggie_treatment_df["colour_id"] != 0]
    duggie_treatment_df = duggie_treatment_df[
        duggie_treatment_df["Q "+ annot + " duggie_nocyp"] < SIGNIF_THRESH
    ]

    d_set = set(duggie_treatment_df["ATC_CODE"])
    s_set = set(stitch_treatment_df["ATC_CODE"])

    stitch_over_duggie = s_set - s_set.intersection(d_set)
    print(annot + " annotation:")
    display(stitch_over_duggie)

# # Analysis of annotation methods
# ## GENE p-value histograms and correlations
#
# A MAGMA gene analysis produces a table of results which looks like this (from the hybrid gene results set):

# +
annot_dfs = []

for annot in annots:
    annot_dfs.append(rdisp.get_annot_results(gwas, annot, magma_results_dir, run_id))
# -

# ZSTAT is used in a subsequent gene set analysis, which MAGMA calculates from PERMP_MULTI.
#
# Note - PERMP_MULTI often contains values of zero. Where a log is taken of these, the value is set in this script to 1e-05 in order to obtain a result from the linear regression.
#
# ### MAGMA calculated P_MULTI values from gene analysis
#
# pi0est - the estimated proportion of true null hypotheses
#
# The orange bars show pvalues < 0.05. The orange part below the red dotted line are the false discoveries. The orange portion above the dotted line represents the true discoveries (significant results).
#
# Each true discovery represents a gene being associated with the disease.
#
# ## Histograms of GENE p-values

# +
plt.figure(figsize=(fig_width, fig_height * len(annots))).subplot_mosaic(plot_list)
ax1 = plt.gca()

for annot in annots:
    annot_index = annots.index(annot)
    plt.subplot(len(plot_list), len(plot_list[0]), annot_index + 1, sharex=ax1, sharey=ax1)
    rdisp.plot_density_histogram(gwas, annot, "gene", annot_dfs[annot_index], "P_MULTI")
# -

# ## QQ-plots of GENE p-values

# +
plt.figure(figsize=(fig_width, fig_height * len(annots))).subplot_mosaic(plot_list)

for annot in annots:
    annot_index = annots.index(annot)
    ax2 = plt.subplot(len(plot_list), len(plot_list[0]), annot_index + 1)
    annot_dfs[annot_index]["Z"] = stats.norm.ppf(annot_dfs[annot_index]["P_MULTI"])
    sm.qqplot(annot_dfs[annot_index]["Z"], line="45", ax=ax2)
    plt.ylabel("measured prox z-score")
    plt.xlabel("expected norm quantiles")
    plt.title("QQ-plot, " + annot + " annotation gene p-vals")
# -

# ## Scatter plots of GENE p-values

# +
scatter_plot_list = generate_plot_list(1 + len(annots) * (len(annots) - 1) / 2)
fig = plt.figure(figsize=(fig_width, fig_height2 * len(annots))).subplot_mosaic(scatter_plot_list)
axlimit = 50
plot_index = 1

for annot1 in annots:
    for annot2 in annots:
        annot_index1 = annots.index(annot1)
        annot_index2 = annots.index(annot2)
        # We only want to compare each pair once
        if annot_index2 > annot_index1:
            plt.subplot(len(scatter_plot_list), len(scatter_plot_list[0]), plot_index)
            plot_index = plot_index + 1
            rdisp.plot_gene_scatter(
                gwas, annot1, annot_dfs[annot_index1], annot2, annot_dfs[annot_index2], "P_MULTI", axlimit
            )

# +
ATC_LEVELS = rdisp.get_atc_levels(data_path)

for dti in dtis:
    for annot in annots:
        rdisp.summarise_drug_results(
            gwas,
            annot,
            ATC_LEVELS,
            magma_results_dir,
            summary_results_dir,
            dti,
            run_id,
            MAGMA_VER,
            N_GENE_THRESH,
            SIGNIF_THRESH,
        )

for annot in annots:
    rdisp.summarise_gopath_results(
        gwas,
        annot,
        ATC_LEVELS,
        magma_results_dir,
        summary_results_dir,
        run_id,
        MAGMA_VER,
        N_GENE_THRESH,
        SIGNIF_THRESH,
    )
# -

# ## DUGGIE drug results
# ### Significant Q-values
#
# Only up to the first 100 table entries are listed for each drugset, and the first 10 for tables expanded with geneset members. Only the first 50 geneset members are displayed in any table.

for annot in annots:
    annot_index = annots.index(annot)
    print("")
    print("Significant " + annot + " Q-values, DUGGIE")
    rdisp.display_tables(
        gwas,
        run_id,
        annot,
        "duggie_nocyp_qvals.tsv",
        "Q " + annot + " duggie_nocyp",
        annot_dfs[annot_index],
        summary_results_dir,
        genesets_df,
        gene_hgnc_df,
    )

# ## Results with STITCH only - ATC drugs

# ### Significant Q-values
#
# Only up to the first 100 table entries are listed for each drugset, and the first 10 for tables expanded with geneset members. Only the first 50 geneset members are displayed in any table.

for annot in annots:
    annot_index = annots.index(annot)
    print("")
    print("Significant " + annot + " Q-values, STITCH")
    rdisp.display_tables(
        gwas,
        run_id,
        annot,
        "-stitch_nocyp_qvals.tsv",
        "Q " + annot + " stitch_nocyp",
        annot_dfs[annot_index],
        summary_results_dir,
        stitch_genesets_df,
        gene_hgnc_df,
    )

# ## GO path results

# +
plt.figure(figsize=(fig_width, fig_height * len(annots))).subplot_mosaic(plot_list)
ax1 = plt.gca()
dti = "duggie_nocyp"

for annot in annots:
    newlist = rdisp.read_results_files(
        gwas, annot, magma_results_dir, run_id, "gopaths", MAGMA_VER
    )
    newlist = newlist[newlist["NGENES"] >= N_GENE_THRESH]
    plt.subplot(
        len(plot_list), len(plot_list[0]), annots.index(annot) + 1, sharey=ax1
    )
    rdisp.plot_density_histogram(
        gwas,
        annot,
        "go path",
        dti_df_sets[dtis.index(dti)][annots.index(annot)],
        "P " + annot + " " + dti,
    )
# -

# ### Significant Q-values
#
# Only up to the first 100 table entries are listed for each drugset, and the first 10 for tables expanded with geneset members. Only the first 50 geneset members are displayed in any table.

for annot in annots:
    annot_index = annots.index(annot)
    print("")
    print("Significant " + annot + " GO paths, DUGGIE")
    rdisp.display_tables(
        gwas,
        run_id,
        annot,
        "go_qvals.tsv",
        "Q " + annot + " gopaths",
        annot_dfs[annot_index],
        summary_results_dir,
        genesets_df,
        gene_hgnc_df,
    )
