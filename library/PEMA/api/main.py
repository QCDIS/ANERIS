import os
import io
import uuid
from typing import Union, Dict, List
from datetime import datetime

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse

import pathlib
import zipfile

app = FastAPI()


def get_file_info(path: str, filename: str) -> Dict[str, str]:
    """
    Get information about a file
    """
    file_path = os.path.join(path, filename)
    file_info = os.stat(file_path)

    # Get file extension
    file_ext = os.path.splitext(filename)[1]
    if file_ext == '':
        file_ext = 'unknown'

    return {
        "filename": filename,
        "last_modified": datetime.fromtimestamp(file_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
        "extension": file_ext
    }

@app.get("/")
async def get_root():
    return {"API": "PEMA"}

@app.get("/pema/")
async def get_pema():  # -> Dict[str, List[Dict[str, str]]]
    # WORKDIR /home
    
    dir_root = '/home'

    fname_pema_R_pkg = 'pema_R_packages.tsv'
    file_pema_R_pkg  = os.path.join(dir_root, fname_pema_R_pkg)

    files_tree = {}
    for folder in os.listdir(dir_root):
        folder_path = os.path.join(dir_root, folder)

        if os.path.isdir(folder_path):
            files_tree[folder] = [get_file_info(folder_path, f) for f in os.listdir(folder_path)]
        
        if os.path.isfile(folder_path):
            files_tree[folder] = get_file_info(dir_root, folder)

    files_tree[fname_pema_R_pkg]["packages"] = []
    with open(file_pema_R_pkg) as fp:
        # data = (line.strip().split('\t') for line in fp)
        # for row in data:
        for line in fp:
            files_tree[fname_pema_R_pkg]["packages"].append(line)
    
    return files_tree

@app.get("/pema/case/")
async def get_pema_case():  # -> Dict[str, List[Dict[str, str]]]
    # WORKDIR /mnt/
    # RUN mkdir analysis
    # RUN mkdir databases

    dir_root = '/mnt/analysis'
    dir_case = os.path.join(dir_root, "case")
    
    files_tree = {}
    for folder in os.listdir(dir_case):
        folder_path = os.path.join(dir_case, folder)

        if os.path.isdir(folder_path):
            files_tree[folder] = [get_file_info(folder_path, f) for f in os.listdir(folder_path)]

    return files_tree

@app.post("/pema/case/")
async def upload_pema_case(case_zip_file: UploadFile):
    # WORKDIR /mnt/
    # RUN mkdir analysis
    # RUN mkdir databases

    date_time_now = datetime.now().strftime('%Y%m%d_%H%M%S%f')

    dir_root = '/mnt/analysis'
    dir_temp = os.path.join(dir_root, "temp")
    dir_case = os.path.join(dir_root, "case")

    try:
        # Create directory
        dir_upload     = os.path.join(dir_case, date_time_now)
        dir_upload_tmp = dir_temp

        fname_upload_tmp = f"{date_time_now}-{case_zip_file.filename}"
        file_upload_tmp  = os.path.join(dir_upload_tmp, fname_upload_tmp)

        if not os.path.exists(dir_upload):
            os.makedirs(dir_upload)
        if not os.path.exists(dir_upload_tmp):
            os.makedirs(dir_upload_tmp)

        # Save the file with the date and time included in the filename
        with open(file_upload_tmp, "wb+") as fp:
            fp.write(case_zip_file.file.read())
            
            with zipfile.ZipFile(file_upload_tmp,"r") as zip_ref:
                zip_ref.extractall(dir_upload)

                files_tree = {}
                for folder in os.listdir(dir_upload):
                    folder_path = os.path.join(dir_upload, folder)

                    if os.path.isdir(folder_path):
                        files_tree[folder] = [get_file_info(folder_path, f) for f in os.listdir(folder_path)]

        return {
            "case_id": date_time_now,
            "info": f"file '{case_zip_file.filename}' saved at {dir_upload_tmp}, unzip at {dir_upload}",
            "files": files_tree
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/pema/run/")
async def run_pema(case_id: str):
    # WORKDIR /mnt/
    # RUN mkdir analysis
    # RUN mkdir databases
    # 
    # string parameterFilePath = "/mnt/analysis/"
    # globalVars{'path'}              = '/home'
    # globalVars{'dataPath'}          = '/mnt/analysis/mydata' 
    # globalVars{'parameterFilePath'} = '/mnt/analysis/'
    # globalVars{'outputPoint'}       = '/mnt/analysis'
    
    dir_root = '/mnt/analysis/case'
    dir_case = os.path.join(dir_root, case_id)
    
    dir_path              = '/home'    
    # dir_dataPath          = f"{dir_case}/mydata"
    # dir_parameterFilePath = f"{dir_case}/"
    # dir_outputPoint       = f"{dir_case}"

    fname_pema  = "pema_latest.bds"
    fname_param = "parameters.tsv"
    fname_log   = f"PEMA-{case_id}.log"
    
    file_pema  = os.path.join(dir_path, fname_pema)
    file_param = os.path.join(dir_case, fname_param)
    file_log   = os.path.join(dir_case, fname_log)

    try:
        os.system(f'{file_pema} -case_id {case_id} 2>&1 | tee {file_log}')

        rtn_status = "Finished"
        # rtn_log = []
        # with open(file_log) as fp:
        #     for line in fp:
        #         rtn_log.append(line)
        
        return {
            "case_id": case_id,
            "status":  rtn_status,
            "info":    f"case '{case_id}' run successfully",

            "file_param": file_param,
            "file_log":   file_log,
            # "log": rtn_log
        }
        
    except Exception as e:
        rtn_status = "Error"
        return {
            "case_id": case_id,
            "status":  rtn_status,
            "info":    f"case '{case_id}' run failed, {str(e)}",

            "file_param": file_param,
            "file_log":   file_log,
        }

@app.get("/pema/result/")
async def download_pema_result(case_id: str):
    # WORKDIR /mnt/

    dir_root = '/mnt/analysis/case'
    dir_case = os.path.join(dir_root, case_id)
    dir_results = os.path.join(dir_case, 'Result', '7.mainOutput')

    fname_zip = f"PEMA-{case_id}.zip"
    file_zip  = os.path.join(dir_case, fname_zip)

    fname_param = "parameters.tsv"
    file_param = os.path.join(dir_case, fname_param)

    fname_log   = f"PEMA-{case_id}.log"
    file_log   = os.path.join(dir_case, fname_log)

    obj_path_dir_results = pathlib.Path(dir_results)
    # zip_io = io.BytesIO()
    with zipfile.ZipFile(file_zip, mode='w', compression=zipfile.ZIP_DEFLATED) as temp_zip:
        temp_zip.write(file_param, fname_param)
        temp_zip.write(file_log,   fname_log)

        for obj_entry in obj_path_dir_results.rglob("*"):
            print(obj_entry, obj_entry.relative_to(obj_path_dir_results))
            temp_zip.write(obj_entry, obj_entry.relative_to(obj_path_dir_results))

    # zip_io = io.BytesIO()
    # with zipfile.ZipFile(zip_io, mode='w', compression=zipfile.ZIP_DEFLATED) as temp_zip:
    #     for file_result in file_results:
    #         temp_zip.write(file_result, file_zip)

    return FileResponse(
        file_zip,
        media_type="application/x-zip-compressed", 
        headers={"Content-Disposition": f"attachment; filename={fname_zip}"}
    )