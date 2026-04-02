<!-- vscode-markdown-toc -->
- [PEMA](#pema)
  - [Requriements](#requriements)
  - [DevOps](#devops)
    - [Bugs](#bugs)
      - [taxAssignments.bds](#taxassignmentsbds)
        - [exec, CREST/LCAClassifier](#exec-crestlcaclassifier)
        - [output file](#output-file)
        - [Error: Line 86](#error-line-86)
        - [Fix](#fix)
        - [LCAClassifier, version 20211129](#lcaclassifier-version-20211129)
          - [Error: "No query sequence could be assigned!", no file will be generated](#error-no-query-sequence-could-be-assigned-no-file-will-be-generated)
          - [output files](#output-files)
    - [PEMA workspace](#pema-workspace)
    - [local](#local)
      - [pema\_org: hariszaf/pema:v.2.1.4](#pema_org-hariszafpemav214)
      - [pema\_api: docker for  `ANERIS` project](#pema_api-docker-for--aneris-project)
    - [UvA](#uva)
      - [VM](#vm)
        - [Docker Composer](#docker-composer)
      - [requests](#requests)
        - [upload zip return case\_id](#upload-zip-return-case_id)
        - [run case\_id](#run-case_id)
        - [get case\_id result](#get-case_id-result)
      - [curl](#curl)
        - [upload zip return case\_id](#upload-zip-return-case_id-1)
        - [run case\_id](#run-case_id-1)
        - [get case\_id result](#get-case_id-result-1)
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

# <a name='PEMA'></a>PEMA

## <a name='Requriements'></a>Requriements

## <a name='DevOps'></a>DevOps

### <a name='Bugs'></a>Bugs

#### <a name='taxAssignments.bds'></a>taxAssignments.bds

##### exec, CREST/LCAClassifier

```
task $globalVars{'path'}/tools/CREST/LCAClassifier/bin/classify \
    -v \
    -c $globalVars{'path'}/tools/CREST/LCAClassifier/parts/etc/lcaclassifier.conf \
    -d silva132 \
    -t allTab_$params{'taxonomyFolderName'}.tsv \
    -o $params{'taxonomyFolderName'} \
    mysilvamod132_$params{'taxonomyFolderName'}.xml \
    &> "$globalVars{'outputFilePath'}/DevOps-taxAssignment.crestAssign-$params{'gene'}.$params{'referenceDb'}-CREST.log"

wait      
```

##### output file

```python
    parser.add_option("-t", "--otuin",
                      dest="otus",
                      type="str",
                      default=None,
                      help=("OTU-table in tab- or comma-separated format, " 
                           "specifying the distribution across datasets "
                           "for the sequences classified."))
    if not hasattr(lca.tree.root, "assignments"):
        sys.stderr.write("\nNo query sequence could be assigned!\n")
        return
```

##### Error: Line 86

```
sys mv $params{'taxonomyFolderName'}/allTab_$params{'taxonomyFolderName'}.tsv $params{'taxonomyFolderName'}/finalTable.tsv
```

##### Fix

`WaitException` doesn't work, "no viable alternative at input"

* https://pcingola.github.io/bds/manual/site/wait/#catching-wait-exceptions
* https://github.com/pcingola/bds/blob/main/test/unit/task/task_33.bds

```
try {
   task {
      sys mv $params{'taxonomyFolderName'}/allTab_$params{'taxonomyFolderName'}.tsv $params{'taxonomyFolderName'}/finalTable.tsv
      sys sed -i 's/classification/Classification/g' $params{'taxonomyFolderName'}/finalTable.tsv
   }

   wait
} catch( WaitException e) {
   println "No query sequence could be assigned!"
   # return 'ok'
} finally {
   println "sys mv finished"
}
```

##### LCAClassifier, version 20211129

`/home/tools/CREST/LCAClassifier/src/LCAClassifier/classify.py`

###### Error: "No query sequence could be assigned!", no file will be generated

[Line, 812](https://github.com/lanzen/CREST/blob/master/LCAClassifier/src/LCAClassifier/classify.py#L812)

```python
    if not hasattr(lca.tree.root, "assignments"):
        sys.stderr.write("\nNo query sequence could be assigned!\n")
        return
```

###### output files

```python
    # Remove empty nodes
    lca.tree.pruneUnassigned(lca.tree.root)
    
    #Write result overviews
    assignmentsCount = open(os.path.join(stub,"All_Assignments.tsv"), 'w')
    totalCount = open(os.path.join(stub,"All_Cumulative.tsv"), 'w')
    rFile = open(os.path.join(stub,"Richness.tsv"),"w")
    chaoFile = open(os.path.join(stub,"Chao1.tsv"),"w")
    raFile = open(os.path.join(stub,"Relative_Abundance.tsv"),"w")

    # ...

    #Add taxonomy to OTU table (new in v3: always do also if not supplied)
    if options.otus:
        otusOut = open(os.path.join(stub,os.path.basename(options.otus)),"w")        
    else:
        otusOut = open(os.path.join(stub,os.path.basename("otus.csv")),"w")
        sep="\t"
    lca.writeOTUsWithAssignments(otusOut, sep=sep)
    otusOut.close()
```

### <a name='PEMAworkspace'></a>PEMA workspace

```shell
root@8397d391df3c:/home# ls /home/
GUniFrac  R-3.6.0  cmake-3.21.4  modules  pema_R_packages.tsv  pema_environment.tsv  pema_latest.bds  scripts  tools

root@8397d391df3c:/home# ls /mnt/analysis/
mydata  parameters.tsv  pema_latest.bds
```

### <a name='local'></a>local

[local, FASTAPI](http://127.0.0.1/docs)

workspace `C:\DockerShare\ANERIS\library\PEMA`
dataspace `C:\DockerShare\ANERIS\example\PEMA\analysis:/mnt/analysis`

#### <a name='pema_org:hariszafpema:v.2.1.4'></a>pema_org: hariszaf/pema:v.2.1.4

```shell
docker run -it --name pema_org --volume="//c/DockerShare/ANERIS/example/DNA/PEMA-ORG/analysis:/mnt/analysis" hariszaf/pema:v.2.1.4

docker exec -it pema_org bash
```

#### <a name='pema_api:dockerforANERISproject'></a>pema_api: docker for  `ANERIS` project

```shell
cd C:\DockerShare\ANERIS\library\PEMA

docker system prune -f
docker rmi pema-api:dev
docker build . --no-cache -f pema.Dockerfile --progress plain --build-arg API_REQ_FOLDER=api -t pema-api:dev
```

```shell
docker system prune -f
docker run -it --rm --name pema_api --publish="80:80" --volume="//c/DockerShare/ANERIS/example/DNA/PEMA-API/analysis:/mnt/analysis" pema-api:dev

docker exec -it pema_api bash
```

```shell
# 1. create folder PEMA-docker
# C:\DockerShare\ANERIS\example\PEMA-Runner\analysis\PEMA-docker
# C:\DockerShare\ANERIS\example\PEMA-Runner\analysis\PEMA-docker\modules

# 2. copy file to PEMA-docker which is mounted to docker
# copy
#   From: C:\DockerShare\ANERIS\library\PEMA\api\modules\taxAssignment.bds
#   To:   C:\DockerShare\ANERIS\example\PEMA-Runner\analysis\PEMA-docker\modules\taxAssignment.bds

# 3. then `cp`
cp /mnt/analysis/PEMA-docker/pema_latest.bds           /home/pema_latest.bds
cp /mnt/analysis/PEMA-docker/modules/taxAssignment.bds /home/modules/taxAssignment.bds

# 4. change to exec
chmod -R +777 /home/pema_latest.bds
chmod -R +777 /home/modules/*.bds
```

### <a name='UvA'></a>UvA

[Github, issure #487](https://github.com/QCDIS/projects_overview/issues/487#issuecomment-3671024251)

#### <a name='VM'></a>VM

```shell
ssh ubuntu@pema-dev.naavre.net

# /mnt/pema:/mnt/analysis
sudo mkdir /mnt/pema
sudo chmod 777 /mnt/pema
scp -r C:\DockerShare\ANERIS\example\PEMA-Runner\analysis\case ubuntu@pema-dev.naavre.net:/mnt/pema/

scp -r C:\DockerShare\ANERIS\library\PEMA\* ubuntu@pema-dev.naavre.net:/home/ubuntu/pema/
scp C:\DockerShare\ANERIS\library\PEMA\docker-compose.yaml ubuntu@pema-dev.naavre.net:/home/ubuntu/pema/

scp ubuntu@pema-dev.naavre.net:/home/ubuntu/pema/docker-compose.yaml C:\DockerShare\ANERIS\library\PEMA\
```

##### Docker Composer

```shell
docker system prune -f

cd C:\DockerShare\ANERIS\
docker compose up
# docker compose up -d

docker compose ps

docker exec -it pema-pema-1 bash
cd /home/ubuntu/pema/

docker compose down
```

#### <a name='requests'></a>requests

```python
dir_pema = os.path.join(dir_data, "PEMA-Runner")
if not os.path.exists(dir_pema):
    os.makedirs(dir_pema)

# Get pema
# url = "https://pema-dev.naavre.net"
url = "https://pema-dev.naavre.net/pema/case/"

obj_response = requests.get(url)
print(obj_response.status_code)
# print(obj_response.text)

dict_response = obj_response.json()
for key, val in dict_response.items():
    print("\n", key, "\n")
    for val_sub in val:
        print(val_sub, "\n")

```

##### upload zip return case_id

```python
# Upload mydata and param
# output: case_id = "20260115_105210330663"
# -----
# dir_data = "/home/jovyan/Virtual Labs/Open Lab/Git public/tutorial/data"
dir_pema = os.path.join(dir_data, "PEMA-Runner")
if not os.path.exists(dir_pema):
    os.makedirs(dir_pema)

# start
# .....
fname_zip = "test.zip"
# fname_zip = "Template-mydata_param.zip"
file_zip  = os.path.join(dir_pema, fname_zip)

url = "https://pema-dev.naavre.net/pema/case/"

with open(file_zip, 'rb') as f:
    print(f)
    
    files = {'mydata_param': (fname_zip, f)}
    print(files)

    r = requests.post(url, files=files)
    print(r.status_code)
    print(r.text)
    r.json()
```

##### run case_id

```python
# run pema
# -----
case_id = "20260115_105210330663"

# start
# .....
url = f"https://pema-dev.naavre.net/pema/run/?case_id={case_id}"

r = requests.post(url)
print(r.status_code)
print(r.text)
# r.json()
```

##### get case_id result

```python
# get pema result
# -----
case_id = "20260115_105210330663"
case_name = f"PEMA-{case_id}"

# dir_data = "/home/jovyan/Virtual Labs/Open Lab/Git public/tutorial/data"
dir_pema = os.path.join(dir_data, "PEMA-Runner", case_name)
if not os.path.exists(dir_pema):
    os.makedirs(dir_pema)

# start
# .....
fname_zip = f"{case_name}.zip"
file_zip  = os.path.join(dir_pema, fname_zip)

url = f"https://pema-dev.naavre.net/pema/result/?case_id={case_id}"

r = requests.get(url, stream=True)
print(r.status_code)
# print(r.text)
# r.json()

if r.status_code == 200:
    chunk_size = 128
    with open(file_zip, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)
    
    if not os.path.isfile(file_zip):
        raise FileNotFoundError(str(file_seq_zip) + " is missing")
    else:
        print(file_zip)
        
        with zipfile.ZipFile(file_zip, 'r') as zip_ref:
            zip_ref.extractall(dir_pema)
else:
    print(r.text)
```

#### <a name='curl'></a>curl

If 504 Gateway Time-out, try to restart docker compose

```shell
curl https://pema-dev.naavre.net/pema/      | python -m json.tool
curl https://pema-dev.naavre.net/pema/case/ | python -m json.tool
```

##### upload zip return case_id

```shell
curl -X 'POST' \
  'https://pema-dev.naavre.net/pema/case/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'case_zip_file=@/home/jovyan/Virtual Labs/Open Lab/Git public/tutorial/Template-mydata_param.zip;type=application/x-zip-compressed'
```

```html
<html>
<head><title>413 Request Entity Too Large</title></head>
<body>
<center><h1>413 Request Entity Too Large</h1></center>
<hr><center>nginx/1.24.0 (Ubuntu)</center>
</body>
</html>
```

##### run case_id

pema is still running after 504, until pema finishes

```shell
curl -X 'POST' \
  'https://pema-dev.naavre.net/pema/run/?case_id=20260115_105210330663' \
  -H 'accept: application/json' \
  -d ''
```

```html
<html>
<head><title>504 Gateway Time-out</title></head>
<body>
<center><h1>504 Gateway Time-out</h1></center>
<hr><center>nginx/1.24.0 (Ubuntu)</center>
</body>
</html>
```

##### get case_id result

```shell
curl -X 'GET' \
  'https://pema-dev.naavre.net/pema/result/?case_id=20260115_105210330663' \
  -H 'accept: application/json' \
  --output "/home/jovyan/Virtual Labs/Open Lab/Git public/tutorial/20260115_105210330663-pema.zip"
```

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
