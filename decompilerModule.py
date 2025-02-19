from secret_keys import PATH_DECOMPILER;
import subprocess;

def decompile_write(file_path, safe_location, methods = None):

    command = "java -jar " + PATH_DECOMPILER + " " + file_path 
    if methods != None and methods != "":
        command+= " --methodname " + methods    
    command+= " --outputdir " + safe_location

    result = None;
    try:
        result = subprocess.run(
            command, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            shell=True);
    except subprocess.CalledProcessError as e:
        return e.stderr;

    return result.stdout;
    
def decompile_no_write(file_path, methods = None):
    command = "java -jar " + PATH_DECOMPILER + " " + file_path 
    if methods != None and methods != "":
        command+= " --methodname " + methods

    result = None;
    try:
        result = subprocess.run(
            command, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            shell=True);
    except subprocess.CalledProcessError as e:
        return e.stderr;

    return result.stdout;


