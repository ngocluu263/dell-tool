import subprocess

result_text = subprocess.Popen("sudo lshw -class network -short",
                               stdout=subprocess.PIPE, shell=True).communicate()[0]
print result_text
