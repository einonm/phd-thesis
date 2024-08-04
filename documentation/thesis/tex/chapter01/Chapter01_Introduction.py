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
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
import os
import sys
import pandas as pd
import numpy as np

# #!pip install scipy
from scipy import stats


# #!pip install matplotlib
# %matplotlib inline
import matplotlib.pyplot as plt

# import qvalue
from IPython.display import display, Latex, display_latex

import warnings

warnings.filterwarnings("ignore")

import subprocess

# #!pip install seaborn
import seaborn as sns
import pylab
import scipy.stats as stats
from scipy.stats import chi2, norm

# %matplotlib inline
# #!pip install venn
import venn

import re

# Also generate tables in latex format, with formatting opts
pd.set_option("display.latex.repr", True)
pd.set_option("display.latex.longtable", True)
pd.set_option("display.latex.multirow", True)
pd.set_option("display.latex.multicolumn", True)
pd.set_option("display.max_colwidth", 2000)

# Switch when converting to PDF ('LaTeX') or ODT ('HTML')
# formatting = 'HTML'
formatting = "LaTeX"

if formatting == "HTML":
    print(
        "FORMATTED FOR REVIEW PURPOSES ONLY. SEE CORRESPONDING PDF FOR CORRECT LAYOUT."
    )
# -

if formatting == "LaTeX":
    display(Latex(r"\doublespacing"))
    display(Latex(r"\setlength{\parskip}{5mm}"))
    display(Latex(r"\newpage"))

# +
#gitspec = subprocess.check_output(
#    ["git", "describe", "--all", "--dirty", "--long"]
#).strip()
#print("This chapter was generated from git revision " + str(gitspec, "utf-8"))
# -

# # General Introduction
#
# The world is experiencing an increasing incidence of life-changing neuropsychiatric disorder diagnoses<citet data-cite="james_global_2018"><sup>james</sup></citet> but with few pharmaceutical treatment options available<citet data-cite="citrome_lack_2015,noauthor_despite_nodate"><sup>citrome,healio</sup></citet>, the outlook for sufferers can be daunting. Drug companies and research organisations are investing large sums into therapeutic solutions, but existing methods to equip clinicians with new drug treatment options have to date achieved a very low rate of success<citet data-cite="becker_why_2008"><sup>becker</sup></citet>.
#
# One recent promising direction taken to identify possible therapeutic drugs at a faster and more cost-effective rate is to mine the extensive molecular, target and interaction data available for currently approved drugs to uncover evidence highlighting novel drug repurposing opportunities, which can be used to treat neuropsychiatric and neurodegenerative conditions<citet data-cite="lee_drug_2016,massey_repurposing_2018"><sup>lee,massey</sup></citet>. Using approved drugs for such a task significantly reduces the effort and time required to bring a drug to market for a new indication compared to de novo drug development.<citet data-cite="elder_many_2020"><sup>elder</sup></citet>.
#
# To date, several drugs have been successfully repurposed including thalidomide, repurposed for myeloma<citet data-cite="singhal_antitumor_1999"><sup>singhal</sup></citet> and leprosy<citet data-cite="teo_thalidomide_2002"><sup>teo</sup></citet>, and sildenafil to treat erectile dysfunction<citet data-cite="debusk_efficacy_2004"><sup>debusk</sup></citet>. However, although serendipity and non-genetic data led to these high-profile successes, genetic evidence has been found suggesting that many other opportunities exist for repurposing<citet data-cite="nelson_support_2015"><sup>nelson</sup></citet>.
#
# One technique that is capable of being employed for repurposing efforts is gene set analysis<citet data-cite="mooney_gene_2015"><sup>mooney</sup></citet>, which identifies over-represented sets of genes within a larger pool of genes. Whilst this technique is often used to perform analyses on gene sets representing pathways<citet data-cite="hariharan_mapping_2021"><sup>hariharan</sup></citet>, it also allows sets of genes encoding protein targets of drugs to be compared against a larger group of genes associated with a disease in a competitive manner. Taking a multi-target drug approach to complex diseases, a significant over-representation of a drug's target genes in the larger group of disease genes indicates that it may be a candidate for repurposing and such significantly associated drugs partaking in the competitive analysis can be ranked based on the strength of the drug-disease association, with the inference that drugs found to have the strongest associations with a disease present the most promising novel repurposing candidates.
#
# For this study, disease genome-wide association study (GWAS) summary results and published drug-gene interaction data sets were curated and used as input to gene set enrichment analyses to seek robust genetic evidence that can identify drug repurposing opportunities for several complex neuropsychiatric and neurodegenerative diseases - schizophrenia, major depressive disorder, bipolar disorder, Alzheimer's disease, Parkinson's disease and Huntington's disease. Prior to this activity, this study analysed better understood medical conditions, hypertension and hypercholesterolaemia, to initially validate the input data sets and approaches used.
#
# Gene-disease associations were obtained from disease GWAS summary results data, where single nucleotide polymorphisms (SNPs) were annotated to genes using proximity data alongside evidence provided by functional quantitative trait loci (QTL) data. Drug-gene interactions were collected from existing published sources, quality controlled and combined, with the aim to provide the most comprehensive coverage of both drugs and their gene targets, exceeding in depth any currently available single source.
#
# Managing the complexity and scale of integrating these large genomic data sets along with applying a detailed reproducible analysis is understood to be a difficult challenge. This study also describes and shares the in-silico methods and techniques used to overcome these difficulties.

# ## This study in context
#
# Drug discovery and repurposing efforts using genetic data have ballooned since the completion of the Human Genome Project in 2003<citet data-cite="lander_initial_2001"><sup>lander</sup></citet>, when new data sources became available such as Genome Wide Association Studies<citet data-cite="cao_gwas_2014"><sup>cao</sup></citet> and pharmacogenomics <citet data-cite="hoehndorf_linking_2012"><sup>hoehndorf</sup></citet>, associating drug response with genetic variations to inform on potential drugs and drug targets. This was followed by the introduction of gene set enrichment analysis (GSEA) in 2005<citet data-cite="subramanian_gene_2005"><sup>subramanian</sup></citet>, paving the way for the creation and use of many other genomic datasets in drug repurposing. For example, gene set enrichment analysis was used to generate the Connectivity Map<citet data-cite="lamb_connectivity_2006"><sup>lamb</sup></citet> in 2006, efficiently allowing researchers to search gene expression signatures of drug responses. Biological pathway data from the established KEGG pathway<citet data-cite="kanehisa_kegg_2000"><sup>kegg</sup></citet> and GO ontology<citet data-cite="ashburner_gene_2000"><sup>ashburner</sup></citet>datasets further enabled researchers using gene set enrichment analysis to link expression changes due to disease and drugs to biological processes and pathways - highlighting potential opportunities by finding new drugs targeting the same pathways and biological systems as existing treatments. 
#
# To ascertain the breadth of existing methods and studies involving gene set analysis and drugs, in particular gene sets of drug targets, a boolean search of the literature via PubMed<citet data-cite="noauthor_pubmed_nodate"><sup>pubmed</sup></citet> was made with a broad search of titles and abstracts using the boolean search string '((drug) OR (drugs)) AND (("gene set") OR ("gene sets"))' involving the human species where the full text was freely available, published in 2017 or earlier (the start of this study). After manual curation of the 523 articles returned, 272 did not involve any sort of gene set enrichment analysis and were discounted. Of the remaining articles, 20 discussed gene set databases or alternative methods to gene set enrichment analysis and a further 229 articles employed gene set enrichment analysis and pathway databases to associate pathways with either GWAS summary results or differential expression between cell lines. These cell lines typically differed in either disease state or from perturbation by drugs or other molecules, mainly in the field of cancer research. Only 2 articles were found to discuss or apply gene set enrichment analysis techniques to drug target gene sets. 
#
# Of these two articles, the most recent, *A Computational Systems Biology Approach for Identifying Candidate Drugs for Repositioning for Cardiovascular Disease* (Yu & Ramsay)<citet data-cite="yu_computational_2018"><sup>yu</sup></citet> as a supplementary analysis used two drug-target interaction databases to obtain drug targets for drugs of interest, then employed a GSEA to compare drugs associated with a specific target against drugs targeting pathways of interest to obtain a rank of enrichment scores for the drug target, but drug targets as a gene set were not used to partake in a GSEA directly. 
#
# The second article, *Polygenic overlap between schizophrenia risk and antipsychotic response: a genomic medicine approach* (Ruderfer et al.)<citet data-cite="ruderfer_polygenic_2016"><sup>ruderfer</sup></citet>, as part of a many layered analysis uses drug target gene sets gathered from two sources - one a set of experimentally confirmed
#  drug targets (DrugBank), and another of drug targets predicted by ligand similarity (Similarity Ensemble Approach, or SEA), but using larger target gene sets from multiple drugs according to the third level classes of the Anatomical Therapeutic Chemical (ATC) classification system (described in depth later in section \ref{the-anatomical-therapeutic-chemical-atc-classification-system}). Enrichment of schizophrenia risk loci (defined as reaching a genome-wide significance in a schizophrenia GWAS) by these gene sets was investigated, resulting in two ATC gene sets found having a p-value just beyond the chosen significance threshold - "agents against amoebiasis and other protozoal diseases" and "antipsychotics". 
#  
# No publication was found analysing enrichment of target gene sets of individual drugs or using target gene sets from experimental evidence only. This may be due to the lack of a centralised drug-gene interaction database based on experimentally obtained data, with enough targets per drug to be used as gene sets in a gene set enrichment analysis. This implies that this study provides a new avenue to use existing data and methods in a novel way.

# ## Associating  drugs with disease
#
# GWAS studies typically produce a summary of the statistical association of millions of SNPs with a disease or trait, usually expressed in the form of a p-value per SNP. These associations describe the link between SNP allele variations commonly occurring in the population and the particular trait, quantifying the probability that the SNP is associated with the disease. These associations are considered to exist because:
#
# * Studies of heritability have shown that there is a genetic component to many diseases and that a person's genetic makeup influences their susceptibility to a disease that is not due wholly to their environment<citet data-cite="tenesa_heritability_2013"><sup>tenesa</sup></citet>
# * This genetic component of susceptibility to a disease is partly attributable to common variations in single nucleotides in a genome<citet data-cite="noauthor_genetic_nodate"><sup>Norrgard</sup></citet>
# * As the genome by nature includes coding genes that produce proteins, common variation in an individual's genome can influence protein function by non-synonymous variation. SNP variation in non-coding genome regions can affect gene expression along with changes in epigenetic modifications, all within one or more tissue types
# * Furthermore, the protein function and expression changes associated with a disease in turn affect the biological pathways in which the proteins are involved, and these pathways may be considered to be involved in the disease mechanism.
#
# By associating a SNP with a disease, it should also be possible to associate the disease with particular genes, proteins and, using gene set analysis, pathways - although combining SNP associations to give a measurement of the association of a gene with a disease, known as SNP-gene annotation and an important step in gene set analysis, is not always straightforward and this challenge is explored in chapter \ref{using-functional-qtl-gene-annotation-to-better-identify-genes-associated-with-disease}.
#
# Using gene set analysis, sets of genes representing pathways have been used to explore the link of drug targets with disease, based on a one drug-one target model, where significantly associating known pathways with a disease has been used to understand and discover more about the disease mechanisms and provide candidate drugs targeting single genes in a disease associated pathway. However, gene set analysis can also be used to associate drugs targeting multiple disease-associated genes to the disease with the expectation that drugs significantly associated thus with a disease may have a safer, more robust therapeutic effect on it.

# ## A gene set enrichment analysis pipeline
#
# A gene set analysis as employed in this study performs a competitive test of each drug against a disease to ascertain if the set of gene targets for the drug are more strongly associated with the disease than the set of genes that are not targets of that drug. The Multi-marker Analysis of GenoMic Annotation (MAGMA)<citet data-cite="leeuw_magma_2015"><sup>magma</sup></citet> software is an established tool that implements this gene set enrichment analysis whilst attempting to correct for known confounding effects, following a disease-gene analysis where trait-associated SNPs are firstly annotated to genes in order to take part in the enrichment analysis, both of which are shown in figure \ref{fig:summary-analysis}, a summary of the main parts of a gene set analysis pipeline.
#
# This pipeline takes as main inputs drug-target gene interactions and p-value associations of single nucleotide polymorphisms (SNPs) with a disease. The pipeline produces results of p-value associations between each drug's set of gene targets and the disease, that can be ranked in ascending p-value order with the lowest p-values being of the most interest.
#
# The pipeline has two main analysis steps - a gene analysis, where the disease-SNP association p-values are mapped to disease-gene association p-vales and a gene-set analysis step where the target gene set of each drug is competitively analysed against the set of disease associated genes to obtain the final drug-gene p-value. Both of these steps are implemented by the MAGMA tool. The steps and data inputs of the pipeline analysis are shown in Figure \ref{fig:summary-analysis}, described in more detail below.
#
# As a secondary input, the gene set analysis part of the pipeline requires a translation from the SNPs associated with the disease to genes along with the association p-values. This study will use several such annotation methods - positional, QTL functional and hybrids of these two to generate separate gene annotations which can be run in parallel as part of an analysis to aid in comparing their relative merits. The selection of these annotation methods is explored in Chapter \ref{using-functional-qtl-gene-annotation-to-better-identify-genes-associated-with-disease}, but prior to this activity the default MAGMA positional annotation will be used as a reference in order to compare other features of the pipeline.

if formatting == "LaTeX":
    display(Latex(r"\begin{figure}[htpb]"))
    display(Latex(r"\centering"))
    display(
        Latex(
            r"\caption{Summary of the main parts of a drug-disease association study. "
            r"\normalfont{Green parallelograms represent data sets, blue rectangles analysis steps.}}"
        )
    )
    display(Latex(r"\includegraphics{../../img/summary-analysis-ud}"))
    display(Latex(r"\label{fig:summary-analysis}"))
    display(Latex(r"\end{figure}"))

# <img src="../../img/summary-analysis-ud.png">

# ## Gene annotation
#
# Gene annotation is the mapping of SNPs to genes, a precursor to the disease-gene analysis step. The MAGMA tool by default provides a simple position-based method and dataset to do this, assigning a SNP to a gene if the SNPs location is inside, or in close proximity to the gene according to a configurable window around the gene. The window is measured as an extension to the transcript start and stop points of the gene, and can have different upstream and downstream values. A symmetrical value of 10 kilobases for this window was used, which has previously shown lower p-values compared to using no such window<citet data-cite="leeuw_magma_2015"><sup>leeuw</sup></citet>. As a set of input SNPs for the positional annotation, those SNPs used in the disease GWAS were chosen to minimise the loss of SNP association data during the gene analysis.
#
# The simplest strategy for annotation is a positional or proximity based method, as carried out by MAGMA, where a SNP is assigned to a gene if it is located within the gene or within a window around the gene. However, this approach does not take into account any further known biological evidence and has been often found to assign SNPs to genes that differ from other sources of evidence<citet data-cite="smemo_obesity-associated_2014"><sup>smemeo</sup></citet> such as Quantitative Trait Loci (QTL) expression measurements that can, in many cases, implicate the greatest effect on a gene close but not adjacent to the SNP being considered<citet data-cite="stacey_progem_2019"><sup>stacey</sup></citet>.
#
# In an attempt to improve the biological basis for SNP annotation, QTL data can be used. A QTL is a region of DNA whose variation correlates with the variation of a quantitative trait such as an mRNA expression level (eQTL)<citet data-cite="nica_expression_2013"><sup>nica</sup></citet> or CpG methylation of a DNA region (mQTL)<citet data-cite="smith_methylation_2014"><sup>smith</sup></citet>. These DNA loci are identified by a direct association test between SNPs and a quantitative measurement of the phenotype (e.g. methylation or gene expression) from tens or hundreds of individuals, and provide more direct biological evidence than associating SNPs positionally. As these measured traits can vary by tissue, QTL analyses are usually performed specific to a tissue type and this provides an opportunity to select a subset of the most relevant tissue types if enough aetiology is known of the disease being investigated - reducing the multiple testing required and preserving statistical power.
#
# However, in the case of such functional gene annotations, where the assignment of SNPs to genes is based on the SNP's function, a large number of SNPs involved in a GWAS are non-coding but functionally relevant and assignment of these compared to assignment of coding SNPs to genes is less straightforward leading to lower coverage of the genome by functional annotations. Hence as QTL data may not include results to identify SNPs for all known genes, a hybrid approach can be used where genes not annotated by any QTL derived SNPs are annotated using positionally derived SNP lists - this increases the coverage of available genes, giving more opportunity to find novel associations. The resultant gene annotation data set can be used as a basis to assign the degree of association with a disease for each gene, given a set of associations of SNPs with the disease such as is produced by a GWAS. 

# ## Disease-gene analysis
#
# The annotation step output is used to enable the gene analysis step to translate the set of disease-SNP association p-values generated from a GWAS into a set of disease-gene association p-values. The MAGMA tool, implementing a SNP-mean with SNP-top multiple model (or multi=snp-wise) was employed for this. For each gene, this model takes the list of SNPs annotated to it along with the SNP-disease association p-values and calculates both the mean p-value (which the MAGMA documentation<citet data-cite="noauthor_magma_nodate"><sup>magmadoc</sup></citet> refers to as the snp-wise=mean model), and the top 1 p-value (referred to as snp-wise=top). The two resultant p-values, one from each model, are combined to give a joint p-value that represents the gene's association with the disease. MAGMA converts the joint p-value to a Z-score using a probit transformation, after undergoing a permutation-based procedure to correct for multiple testing. The set of such Z-scores for all annotated genes are used as input to a gene set analysis.
#
# The mean model on its own measures the mean SNP association but tends to skew towards associations in areas of higher Linkage Disequilibrium (LD) within a gene, while the top model on its own only considers the most significant SNP and is very sensitive to genes with few SNP associations. By aggregating these scores into a single p-value, both of these unwanted effects are blunted. Alongside the gene p-values, a MAGMA gene analysis also calculates correlations between all pairs of genes which are used to account for LD in any subsequent gene set analyses. Linkage disequilibrium is the non-random association of allele loci along a genome. Loci are in LD when the frequency of association of the alleles is not equal to that expected if they were random - this can occur due to genetic linkage, mutation, genetic drift and population structure.
#
# A MAGMA gene analysis uses as a default setting an adaptive permutation method to correct output p-values for multiple testing, where the number of permutations calculated is dependent on the gene association p-value. This adaptive method, used to minimise compute resource use, stops once a predefined number of permutations, 10 by default, are calculated with a test statistic more extreme than that found for the observed data giving the dependence on the p-value, as lower p-values would on average require more permutations to meet the criteria. The number of permutations matching the criteria is checked periodically by MAGMA after a set number of permutation calculations - 1,000, 5,000, 10,000, 50,000 etc.
#
# Whilst testing the automated pipeline as part of this study, the adaptive method was found to give a huge variation in output p-values over multiple runs with the same input data, partly due to the inherent randomness of permutation calculations but this also would be exacerbated by the permutation stopping mechanism adding to the variation - even for the same gene, stopping after 1,000 permutations may give a widely different result compared to stopping after 50,000 permutations. Instead a fixed number of permutations was found to be more reliable at an acceptable level of compute resource use - a value of 20,000 permutations was chosen as the most pragmatic to ensure reliability of the results, taking of the order of 12 hours to run on the available compute infrastructure. See Appendix \ref{appendix-magma-permutation-issues} for further details.

# ## Competitive gene set analysis
#
# The MAGMA tool is once again used to execute the final step in the pipeline, a competitive gene set analysis implemented as a linear regression of a gene data matrix, where each gene is marked either as a member of the test set or outside this set and number of SNPs, Z-score, gene size and gene-gene correlations (calculated as part of the previous gene analysis and used to account for linkage disequilibrium) included as standard covariates. The calculated gene-set p-value is the result of a test that the mean association of genes in the gene set is greater that that of genes not in the gene set, conditioned broadly on the standard covariates listed.
#
# For this study, the gene sets involved in the gene set analysis are the larger set of genes with Z-scores of their association with a disease, as output from the gene analysis, and a smaller set of genes representing the targets of an approved drug.
#
# The result of this step is a list of drugs, each represented in the analysis by its set of gene targets, against the corresponding association p-value of the drug with the disease. For the drugs of interest - those with the lowest p-values which are deemed significant by having a p-value lower than 0.05, an arbitrary but common choice often attributed to R.A. Fisher in his 1925 work *Statistical methods for research workers*<citet data-cite="fisher_statistical_1963"><sup>fisher1925</sup></citet>, although ideally the p-value would be much lower. The target list of such significant drugs can be further investigated to allow discussion of possible mechanisms of action for the association.

# ## Drug-target gene interactions
#
# A drug-target gene interaction database provides the collection of gene sets needed to perform a gene set enrichment analysis against the set of genes tested for association with a disease. There are many freely available sources of drug-target interactions, with the observation that each may define a drug target and provide evidence for inclusion differently. In order to gain the broadest, most complete set of interactions, data from these individual sources were combined, and in combining them a compatible definition of a drug target determined along with consistent schemes for identifying drugs, such as Anatomical Therapeutic Chemical (ATC) codes<citet data-cite="noauthor_anatomical_2017"><sup>atc</sup></citet>, and targets, such as Entrez gene IDs<citet data-cite="brown_gene_2015"><sup>brown</sup></citet> or UniProt protein IDs<citet data-cite="uniprot_consortium_uniprot_2018"><sup>uniprot</sup></citet>.
#
# To compile the most comprehensive set of drug gene interactions available, a search of the literature was conducted for existing published drug-gene interaction databases. A drug target definition was also sought that is both consistent with the definitions used to compile the constituent drug-gene interaction data sets, and with the idea of a drug target based on ligand binding supported by experimental evidence, as was aimed at in this study.
#
# Participating drugs were identified by at least an ATC code, a method of grouping drugs which provides both a useful ontology whilst allowing only approved drugs to take part in the analysis.
#
# The supporting evidence used to identify each drug-gene interaction was also recorded to enable the automatic presentation of this evidence when a repurposing opportunity is identified later, allowing the drug-gene relationship to be studied and verified further.
#
# The drug-target database created lists for each drug its interacting set of genes and for each drug-gene pair, supporting evidence for the relationship.

# ## Quality control and results comparison
#
# Each run of the gene set enrichment analysis pipeline results in a set of association p-values of drugs with a disease, and the merits of one set of results over another often needs to be determined, where the results are obtained from pipeline executions usually differing in a single input parameter or one aspect of input data.
#
# The principal measure of success is the number of drugs found to have a significant association with the disease. Secondary is the number of significant drugs found that are used to treat the disease in a clinical setting - referred to as treatment drugs, where the treatment drugs for a disease are obtained from DrugBank's<citet data-cite="law_drugbank_2014"><sup>law</sup></citet> list of drugs used to treat the disease indication. There are some drawbacks to this as the analysis is not capable of differentiating between drugs that have a therapeutic effect on a phenotype, drugs that have a therapeutic effect on a phenotype but are not used to treat the disease due to, for example, side effects and drugs that exacerbate or cause a phenotype - despite each of these drug groups may have a significant association with the disease.
#
# Several other statistical tools are employed to quantify the difference between gene set analysis results. The first of these is a simple p-value histogram, which can inform if there is evidence to reject the null hypothesis, false discovery rate and power of the analysis. Quantile-Quantile plots are used to compare the p-value distribution with the normal distribution, informing if there are any unexpected deviations and if the null hypothesis holds. Histograms and Q-Q plots of p-values are generated for both gene analysis and gene set enrichment analysis results.
#
# Also utilised are correlation plots comparing two sets of negative logs of storey q-value<citet data-cite="storey_direct_2002"><sup>storey</sup></citet> results of drugs with disease. Results from two analyses using e.g. different drug-gene interactions or annotation methods are compared. Where drugs are plotted far away from a central equivalence line, these have a large difference in association with the disease between the two results sets. A consistent trend of such drugs on a plot may indicate one analysis consistently improving association p-values over the other, without needing a p-value threshold.
#
# With a set of treatment drugs defined the drugs analysed can be split into two groups - treatment drugs and non-treatment drugs, allowing a confusion matrix to be constructed and an exact Fisher p-value obtained indicating the association between the treatment drug classification and the analysis run's ability to detect a treatment drug. A Mann-Whitney U test for an analysis run comparing the sets of p-value results obtained for treatment and non-treatment drugs indicates the ability of the analysis to separate the two drug groups.
#
# Finally Receiver-Operator Characteristic (ROC) curves are plotted for each analysis and the corresponding Area Under the Curve (AUC) values calculated. These give a measure of the ability of the analysis to correctly classify a drug as treatment or non-treatment.

# ## Aim of this study
#
# The principal aim of this study was to develop and utilise a novel approach that can identify novel drug repurposing opportunities for neuropsychiatric and neurodegenerative diseases by curating and utilising the most up to date genomic, functional, disease and drug-gene interaction datasets, conducting gene set analyses using a well-established method implemented by the MAGMA tool and automating a pipeline to execute it. Such a pipeline can significantly associate suitable drugs with a disease and further rank these significantly associated drugs. 
#
# To engineer the most effective pipeline, secondary aims were pursued of:
#
# * curating a drug gene interaction database with the greatest coverage of drugs, target genes and their interactions possible (Chapter \ref{curation-of-a-drug-target-interaction-database}); and
# * ascertaining the advantages of using functional QTL annotation and the best methods of incorporating such data in the analysis (Chapter \ref{using-functional-qtl-gene-annotation-to-better-identify-genes-associated-with-disease}).
#
# The study validated the pipeline effectiveness by running and analysing results from diseases having known genetic architecture, comprehensive GWAS summary results and a large selection of effective drug treatments available - hyptertension and hypercholesterolemia were selected as fitting this criteria (Chapters \ref{appraisal-of-the-pipeline-performance-with-hypertension-and-hypercholesterolemia} and \ref{using-functional-qtl-gene-annotation-to-better-identify-genes-associated-with-disease}).
#
# Finally, the study aimed to use the curated datasets and validated, highly automated pipeline to identify novel approved drug repurposing opportunities for schizophrenia, major depressive disorder, bipolar disorder, Alzheimer's disease, Parkinson's disease and Huntington's disease (Chapter \ref{application-of-the-analysis-pipeline-to-neuropsychiatric-and-neurodegenerative-diseases}).

# ## In-silico development
#
# This study was conducted entirely in-silico. 

# A common challenge with many scientific studies is that of reproducibility of methods and results, often referred to as the 'replication crisis'<citet data-cite="noauthor_replication_2024"><sup>replication</sup></citet>, and prevalent in psychology and medicine. One aspect of this is the unavailability of data and code, alongside code that cannot be run or produces results at odds with those claimed. To overcome such issues, all input data used was freely available and referenced, and all code used to run analyses scripted and automated as far as possible.
#
# The majority of the analysis code used for this study was developed as a set of Jupyter notebooks<citet data-cite="kluyver_jupyter_2016"><sup>jupyter</sup></citet>, stored as plain python files with a '.py' extension that can be opened and run in a jupyter environment according to the README.md found in the unzipped \hyperref[supp:sf5]{Supplementary File 5}: SF5-code_archive.zip, which includes all chapters of this thesis. With the relevant data in place (\hyperref[supp:sf6]{Supplementary File 6}: SF6-appendix-B_archive.zip and \hyperref[supp:sf7]{Supplementary File 7}: SF7-results-data_archive.tar.gz) and software dependencies installed, the analyses can be repeated and this thesis generated as a pdf using a script (generate_thesis.sh), with the vast majority of graphs, charts and tables appearing in the thesis able to be reproduced, investigated and tested - allowing the review and identification of bugs and issues with the aim of providing a more robust and accurate analysis. All scripts and notebook versions were recorded and stored by the Git<citet data-cite="noauthor_git_nodate"><sup>git</sup></citet> version control system, with the aim of allowing any part of the analysis pipeline to be repeated given identical data inputs. Appendix \ref{appendix-pipeline-scripts-and-notebooks} show diagrams for the main workflows for generating drug-gene interaction databases and drug-disease association results.

# Data manipulation and analyses were carried out in Linux<citet data-cite="noauthor_linux_nodate"><sup>linux</sup></citet> environments, with big data computation taking place on Red-Hat Linux<citet data-cite="noauthor_red_nodate"><sup>rh</sup></citet> clustered High Performance Computing hardware running the SLURM<citet data-cite="noauthor_slurm_nodate"><sup>slurm</sup></citet> workload manager and data wrangling activities performed on a personal laptop running the Fedora Workstation Linux distribution<citet data-cite="noauthor_get_nodate"><sup>fedora</sup></citet>. Orchestration of computations was achieved using bash<citet data-cite="noauthor_gnuorg_nodate"><sup>bash</sup></citet> shell scripts with data manipulation and analysis activities coded in the Python<citet data-cite="noauthor_welcome_nodate"><sup>py</sup></citet> language within the Jupyter Notebook environment. Notable Python libraries used for the analysis were Numpy<citet data-cite="van_der_walt_numpy_2011"><sup>numpy</sup></citet>, SciPy<citet data-cite="virtanen_scipy_2020"><sup>scipy</sup></citet>, Seaborn<citet data-cite="michael_waskom_mwaskomseaborn_2020"><sup>seaborn</sup></citet> and Pandas<citet data-cite="mckinney_data_2010"><sup>pandas</sup></citet>. Some network analyses were undertaken using the Neo4j<citet data-cite="noauthor_neo4j_nodate"><sup>neo4j</sup></citet> graph database. MAGMA version 1.09 was used for all main neuropsychiatric analyses, whilst MAGMA version 1.08b was used for some earlier hyptertension and hypercholesterolaemia analyses.

# The Genome Reference Consortium<citet data-cite="noauthor_genome_nodate"><sup>grchb37</sup></citet> Human Genome Build 37 coordinates, GRChb37 was used throughout, with the necessary conversions performed.

if formatting == "LaTeX":
    display(Latex(r"\newpage"))
