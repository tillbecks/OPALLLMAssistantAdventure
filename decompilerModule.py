from secret_keys import PATH_DECOMPILER;
import subprocess;

def decompile(file_path, safe_location, methods = None):
    print("Decompiling file: " + file_path);
    print("Safe location: " + safe_location);

    command = "java -jar " + PATH_DECOMPILER + " " + file_path 
    if methods != None and methods != "":
        command+= " --methodname " + methods    
    command+= " --outputdir " + safe_location

    print("Command: " + command);

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
        print(e.stderr);
        return e.stderr;

    print(result.stdout);
    return result.stdout;
    


