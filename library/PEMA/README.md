#  1. <a name='PEMA'></a>PEMA

<!-- vscode-markdown-toc -->
- [1. PEMA](#1-pema)
  - [Requriements](#requriements)
    - [Tools](#tools)
    - [Database](#database)
  - [DevOps](#devops)
    - [docker](#docker)
    - [workspace](#workspace)
    - [VM, pema-dev.naavre.net](#vm-pema-devnaavrenet)
      - [VM](#vm)
      - [Composer](#composer)
  - [Test](#test)
    - [test\_18S, gene\_16S](#test_18s-gene_16s)
    - [Res\_gene\_18S-PEMA\_v2.1.4-docker, gene\_18S](#res_gene_18s-pema_v214-docker-gene_18s)
    - [compare, gene\_16S \& gene\_18S](#compare-gene_16s--gene_18s)
  - [Viewer](#viewer)
    - [C:\\MyPrograms\\FastTree\\FastTree.exe" -nt -gtr -out TEMP\_OUT\_FILE CURRENT\_ALIGNMENT\_FASTA](#cmyprogramsfasttreefasttreeexe--nt--gtr--out-temp_out_file-current_alignment_fasta)
    - [C:\\MyPrograms\\FigTree\\FigTree v1.4.4.exe" TEMP\_OUT\_FILE](#cmyprogramsfigtreefigtree-v144exe-temp_out_file)

<!-- vscode-markdown-toc-config
	numbering=false
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

## <a name='Requriements'></a>Requriements

### <a name='Tools'></a>Tools

* [Big Data Script language (BDS)](https://github.com/pcingola/bds)
  * [manual](https://pcingola.github.io/bds/manual/site/syntax_highlight/)
  * [command line parsing](https://pcingola.github.io/bds/manual/site/cmdline/)
* [openjdk-11-jdk](https://openjdk.org/projects/jdk/11/)

* [FastQC, v0.11.8.zip](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.8.zip), [github](https://github.com/s-andrews/FastQC), A quality control tool for high throughput sequence data
* [VSEARCH, 2.9.1, github](https://github.com/torognes/vsearch/releases/download/v2.9.1/vsearch-2.9.1-linux-x86_64.tar.gz), [github](https://github.com/torognes/vsearch), Vectorized search
* [Trimmomatic, 0.38](http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.38.zip), [github](https://github.com/usadellab/Trimmomatic), A flexible read trimming tool for Illumina NGS data
* [obi, v1.2.13, zenodo](https://zenodo.org/record/5745272/files/obi_v1.2.13.tar), [OBITools3, forge](https://forge.metabarcoding.org/obitools/obitools3), [pip](https://pypi.org/project/OBITools3/), A package for the management of analyses and data in DNA metabarcoding
* [SPAdes, 3.14.0, cab.spbu.ru (not found)](http://cab.spbu.ru/files/release3.14.0/SPAdes-3.14.0.tar.gz), [github](https://github.com/ablab/spades), Assembly and analysis of sequencing data
* [PANDAseq, github](http://github.com/neufeld/pandaseq.git),  Align Illumina reads, optionally with PCR primers embedded in the sequence, and reconstruct an overlapping sequence
* [NCBI-blast+, 2.8.1, ftp](https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.8.1/ncbi-blast-2.8.1+-x64-linux.tar.gz), [github](https://github.com/ncbi/blast_plus_docs), Basic Local Alignment Search Tool
* [PaPaRa_nt, 2.5, ftp](https://sco.h-its.org/exelixis/resource/download/software/papara_nt-2.5-static_x86_64.tar.gz), [github](https://github.com/sim82/papara_nt), PArsimony-based Phylogeny-Aware Read alignment program
* [EPA-ng, github](https://github.com/Pbdas/epa.git), Fast, parallel, highly accurate Maximum Likelihood Phylogenetic Placement
* [RAxML-ng, github](https://github.com/amkozlov/raxml-ng.git), A phylogenetic tree inference tool
* [SWARM, github](https://github.com/torognes/swarm.git), A robust and fast clustering method for amplicon-based studies
* [MAFFT, 7.427-1](https://mafft.cbrc.jp/alignment/software/mafft_7.427-1_amd64.deb), [github](https://github.com/GSLBiotech/mafft), Align multiple amino acid or nucleotide sequences
* [cutadapt, pip](https://pypi.org/project/cutadapt/), [github](https://github.com/marcelm/cutadapt/), Finds and removes adapter sequences, primers, poly-A tails and other types of unwanted sequence from your high-throughput sequencing reads
* [ncbi-taxonomist, pip](https://pypi.org/project/ncbi-taxonomist/), [gitlab](https://gitlab.com/janpb/ncbi-taxonomist), handles and manages phylogenetic data from [NCBI's Entrez taxonomy database](https://www.ncbi.nlm.nih.gov/taxonomy)
* [CREST, zenodo](https://zenodo.org/record/5734317/files/crest.tar.gz), [github](https://github.com/crest-lab/crest), (Conformer-Rotamer Ensemble Sampling Tool) is a program for the automated exploration of the low-energy molecular chemical space
* [RPDTools, zenodo](https://zenodo.org/record/5734317/files/rdptools.tar.gz), [github](https://github.com/rdpstaff/RDPTools), Collection of commonly used modules from the RDP-Ribosomal Database Project (Classifier, Clustering, SequenceMatch, ProbeMatch, InitialProcessing, FrameBot, ReadSeq, Xander) and all their dependencies

### <a name='Database'></a>Database

* [SILVA](https://www.arb-silva.de/no_cache/download/archive/current/Exports/)
  * [SILVA 138](https://zenodo.org/record/6419029/files/silva138.tar.gz)
* [MIDORI](http://reference-midori.info/index.html)
* [PR2](https://pr2-database.org/)

## <a name='DevOps'></a>DevOps

### <a name='docker'></a>docker

[local, FASTAPI](http://127.0.0.1/docs)

workspace `C:\DockerShare\ANERIS_DNA\library\PEMA`
dataspace `C:\DockerShare\ANERIS_DNA\Example\PEMA\analysis:/mnt/analysis`

```shell
cd C:\DockerShare\ANERIS_DNA\library\PEMA

docker build . --no-cache -f pema.Dockerfile --build-arg API_REQ_FOLDER=api -t pema-api:dev
docker run -it --rm --name api_pema --publish="80:80" --volume="//c/DockerShare/ANERIS_DNA/Example/PEMA/analysis:/mnt/analysis" pema-api:dev

docker exec -it api_pema bash
```

```shell
docker run -it --name pema --volume="//c/DockerShare/ANERIS_DNA/PEMA/analysis:/mnt/analysis" hariszaf/pema:v.2.1.4
```

### <a name='workspace'></a>workspace

```shell
root@8397d391df3c:/home# ls /home/
GUniFrac  R-3.6.0  cmake-3.21.4  modules  pema_R_packages.tsv  pema_environment.tsv  pema_latest.bds  scripts  tools

root@8397d391df3c:/home# ls /mnt/analysis/
mydata  parameters.tsv  pema_latest.bds
```

### <a name='VMpema-dev.naavre.net'></a>VM, pema-dev.naavre.net

[Github, issure #487](https://github.com/QCDIS/projects_overview/issues/487#issuecomment-3671024251)

#### <a name='VM'></a>VM

```shell
ssh ubuntu@pema-dev.naavre.net

scp ubuntu@pema-dev.naavre.net:/home/ubuntu/pema/docker-compose.yaml C:\DockerShare\ANERIS_DNA\library\PEMA\api\
```

#### <a name='Composer'></a>Composer

## <a name='Test'></a>Test

* parameters.tsv: 
  * `outputFolderName	test_18S`
  * `gene	gene_16S`
* log: `pema_latest.log`
* tmp: `*.chp`
* result: 
  * `7.mainOutput\gene_16S\vsearch\my_taxon_assign\finalTable.tsv`
  * `7.mainOutput\gene_16S\vsearch\all_sequences_grouped.fa`
  * parameters.tsv: `parameters0f.test_18S.tsv`
* pema_analysis_dir.zip: `test_18S\*`

### <a name='test_18Sgene_16S'></a>test_18S, gene_16S

```shell
root@8397d391df3c:/home# ./pema_latest.bds 2>&1 | tee /mnt/analysis/pema_latest.log

Picked up JAVA_TOOL_OPTIONS: -XX:+UseContainerSupport
A new output files was just created!
ERR7125480_1.fastq.gz
ERR7125480_2.fastq.gz
ERR7125483_1.fastq.gz
ERR7125483_2.fastq.gz
ERR7125486_1.fastq.gz
ERR7125486_2.fastq.gz
ERR7125489_1.fastq.gz
ERR7125489_2.fastq.gz
Picked up JAVA_TOOL_OPTIONS: -XX:+UseContainerSupport
...
  inflating: ERR7125489_1_fastqc/fastqc.fo
here is readDirection from sample
ERR7125489_2_fastqc.zip
2
Archive:  /mnt/analysis/test_18S/1.qualityControl/ERR7125489_2_fastqc.zip
   creating: ERR7125489_2_fastqc/
   creating: ERR7125489_2_fastqc/Icons/
   creating: ERR7125489_2_fastqc/Images/
  inflating: ERR7125489_2_fastqc/Icons/fastqc_icon.png
  inflating: ERR7125489_2_fastqc/Icons/warning.png
  inflating: ERR7125489_2_fastqc/Icons/error.png
  inflating: ERR7125489_2_fastqc/Icons/tick.png
  inflating: ERR7125489_2_fastqc/summary.txt
  inflating: ERR7125489_2_fastqc/Images/per_base_quality.png
  inflating: ERR7125489_2_fastqc/Images/per_tile_quality.png
  inflating: ERR7125489_2_fastqc/Images/per_sequence_quality.png
  inflating: ERR7125489_2_fastqc/Images/per_base_sequence_content.png
  inflating: ERR7125489_2_fastqc/Images/per_sequence_gc_content.png
  inflating: ERR7125489_2_fastqc/Images/per_base_n_content.png
  inflating: ERR7125489_2_fastqc/Images/sequence_length_distribution.png
  inflating: ERR7125489_2_fastqc/Images/duplication_levels.png
  inflating: ERR7125489_2_fastqc/Images/adapter_content.png
  inflating: ERR7125489_2_fastqc/fastqc_report.html
  inflating: ERR7125489_2_fastqc/fastqc_data.txt
  inflating: ERR7125489_2_fastqc/fastqc.fo
----------------------------------------------------------
Pema has been completed successfully. Let biology start!
Thanks for using Pema.
```

### <a name='Res_gene_18S-PEMA_v2.1.4-dockergene_18S'></a>Res_gene_18S-PEMA_v2.1.4-docker, gene_18S

* parameters.tsv: 
  * `outputFolderName	Res_gene_18S-PEMA_v2.1.4-docker`
  * `gene	gene_18S`
* log: `Res_gene_18S-PEMA_v2.1.4-docker.log`
* tmp: `*.chp`
* result: 
  * `7.mainOutput\gene_18S\vsearch\my_taxon_assign\finalTable.tsv`
  * `7.mainOutput\gene_18S\vsearch\all_sequences_grouped.fa`
  * parameters.tsv: `parameters0f.Res_gene_18S-PEMA_v2.1.4-docker.tsv`
* pema_analysis_dir.zip: `Res_gene_18S-PEMA_v2.1.4-docker\*`

```shell
root@8397d391df3c:/home# ./pema_latest.bds 2>&1 | tee /mnt/analysis/Res_gene_18S-PEMA_v2.1.4-docker.log

root@8397d391df3c:/home# cp -rf /mnt/analysis/mydata                              /mnt/analysis/Res_gene_18S-PEMA_v2.1.4-docker/
root@8397d391df3c:/home# mv     /mnt/analysis/Res_gene_18S-PEMA_v2.1.4-docker.log /mnt/analysis/Res_gene_18S-PEMA_v2.1.4-docker/

root@8397d391df3c:/home# ls
GUniFrac      modules               pema_latest.bds                      pema_latest.bds.20251205_133048_926  pema_latest.log
R-3.6.0       pema_R_packages.tsv   pema_latest.bds.20251205_132857_377  pema_latest.bds.20251205_141345_284  scripts
cmake-3.21.4  pema_environment.tsv  pema_latest.bds.20251205_133032_618  pema_latest.bds.20251205_141456_171  tools
```

### <a name='comparegene_16Sgene_18S'></a>compare, gene_16S & gene_18S

`finalTable.tsv`: match

## <a name='Viewer'></a>Viewer

AliView, FastTree, FigTree

### <a name='C:MyProgramsFastTreeFastTree.exe-nt-gtr-outTEMP_OUT_FILECURRENT_ALIGNMENT_FASTA'></a>C:\MyPrograms\FastTree\FastTree.exe" -nt -gtr -out TEMP_OUT_FILE CURRENT_ALIGNMENT_FASTA

```shell
C:\MyPrograms\FastTree\FastTree.exe -nt -gtr -out C:\Users\quan.pan\AppData\Local\Temp\aliview-tmp-tempfile-for-new-alignment_6002128974095716153.tmp C:\Users\quan.pan\AppData\Local\Temp\aliview-tmp-current-alignment_7281490812908973559fas

FastTree Version 2.2.0 Double precision
Alignment: C:\Users\quan.pan\AppData\Local\Temp\aliview-tmp-current-alignment_7281490812908973559fas
Nucleotide distances: Jukes-Cantor Joins: balanced Support: SH-like 1000
Search: Normal +NNI +SPR (2 rounds range 10) +ML-NNI opt-each=1
TopHits: 1.00*sqrtN close=default refresh=0.80
ML Model: Generalized Time-Reversible, CAT approximation with 20 rate categories
Non-unique name 'ERR7125483' in the alignment
```

### <a name='C:MyProgramsFigTreeFigTreev1.4.4.exeTEMP_OUT_FILE'></a>C:\MyPrograms\FigTree\FigTree v1.4.4.exe" TEMP_OUT_FILE

require java
* Version 8 Update 471
* Release date: October 21, 2025
* filesize: 38.48 MB

```shell
C:\MyPrograms\FigTree\FigTree v1.4.4.exe C:\Users\quan.pan\AppData\Local\Temp\aliview-tmp-tempfile-for-new-alignment_6002128974095716153.tmp

javax.swing.UIManager$LookAndFeelInfo[Metal javax.swing.plaf.metal.MetalLookAndFeel]
javax.swing.UIManager$LookAndFeelInfo[Nimbus javax.swing.plaf.nimbus.NimbusLookAndFeel]
javax.swing.UIManager$LookAndFeelInfo[CDE/Motif com.sun.java.swing.plaf.motif.MotifLookAndFeel]
javax.swing.UIManager$LookAndFeelInfo[Windows com.sun.java.swing.plaf.windows.WindowsLookAndFeel]
javax.swing.UIManager$LookAndFeelInfo[Windows Classic com.sun.java.swing.plaf.windows.WindowsClassicLookAndFeel]
```
