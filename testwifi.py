import subprocess

def cleanfloat(f):
    try:
        number = float(f)
        return(number)
    except ValueError as e:
        return(0.0)
    
#result = subprocess.run(['wpa_cli', 'scan_results'], stdout=subprocess.PIPE).stdout.decode('ascii').split('\t')
#result = subprocess.run(['wpa_cli', 'scan_results'], stdout=subprocess.PIPE).stdout.decode('ascii').split('\n')
#signalstrength=[string for string in result if "Solipsia24" in string][0].split('\t')[2]
#print(signalstrength)
#signalstrength=result[2]
#print(signalstrength)
#wpa_cli scan_results
#print(result[2])

#link_quality = subprocess.run(["iwconfig", "wlan0"], capture_output=True, text=True).stdout.split("Link Quality=")[1].split("/")[0]
#print(link_quality)

link_quality = subprocess.run(["iwconfig", "wlan0"], capture_output=True, text=True).stdout.split("Link Quality=")[1].split("/")[0]
print(link_quality)
signalstrength=cleanfloat(link_quality)
print(signalstrength)