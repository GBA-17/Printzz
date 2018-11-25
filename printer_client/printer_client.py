import json
import requests
import subprocess
import time
import urllib

url = 'http://printzz.herokuapp.com/'
refresh_time = 2
print_time = 30

def poll_server():    

    # Check if There is a File Ready to Print
    params = {'printer_id': 'e19e5d74-6ed2-41b6-ad21-ed1c8e7be7e1'}
    settings = (requests.get(url+'get_doc_settings', params=params)).json()
    
    # Return to Loop if No File Exists
    if (settings['status'] == False):
        return

    # File Exists, So Download the Actual File
    doc_url = url + 'get_doc?printer_id=' + params['printer_id']
    doc = (urllib.request.urlopen(doc_url)).read()
    print ("Received " + settings['data']['doc_name'] + " from " +\
            settings['data']['username'])

    # Write the File to Disk
    extension = settings['data']['ext']
    f = open("print." + extension, "wb")
    f.write(doc)
    f.close

    # TODO Check If .docx can be printed directly, or need to convert

    # Generate Print Command Based on Provided Options
    print_cmd = "lp print." + extension + " -n "
    print_cmd += str(settings['data']['settings']['copies']) + " "  # Number of Copies
    if (settings['data']['settings']['double_sided'] == 1):         # Double-Sided, Long Edge
        print_cmd += "-o sides=two-sided-long-edge "
    elif (settings['data']['settings']['double_sided'] == 2):       # Double-Sided, Short Edge
        print_cmd += "-o sides=two-sided-short-edge "
    if (settings['data']['settings']['color'] == False):            # Color Printing
        print_cmd += "-oColorModel=KGray"
    
    # Issue Print Command to the System
    subprocess.call(print_cmd, shell=True)
    print (print_cmd)

    # Perform Cleanup
    subprocess.call('rm -f print.*', shell=True)
    pop_res = (requests.get(url+'pop_doc', params=params)).json()

    # Check for Successful Pop
    if pop_res['status'] == False:
        print ("ERROR: " + pop_res['error'])
        exit()
    return
    
def main():
    # Delete Any Existing Print Files
    subprocess.call('rm -f print.*', shell=True)

    # Continuously Poll the Server, Printing Any Files Found
    while (True):
        poll_server()
        time.sleep(refresh_time)


if __name__ == "__main__":
    main()