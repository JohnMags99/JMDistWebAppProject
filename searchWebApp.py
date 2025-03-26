from flask import Flask, render_template, request, url_for, flash
from werkzeug.utils import redirect
import paramiko

app = Flask(__name__)
app.config['ENV'] = "Development"
app.config['DEBUG'] = True


@app.route('/')
def searchHome():
    return render_template('search.html')


#Result Landing Page Function
@app.route('/getResult', methods=['POST', 'GET'])
def getResult():
    #Public IPv4 address on EC2 connect console, needs to be reviewed each time instance is stopped and started
    instance_ip="13.51.162.145"
    securityKeyFile="/home/johnm/DistWebAppProj.pem"
    searchTerm=request.form.get('wSearch')
    cmd="source wiki/wiki_env/bin/activate && python3 wiki.py"  #Activating venv before executing wiki.py

    try:
        #Attempt to connect/ssh to the instance
        client=paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key=paramiko.RSAKey.from_private_key_file(securityKeyFile)
        client.connect(hostname=instance_ip, username="johnm", pkey=key)

        #Executing wiki.py
        stdin,stdout,stderr=client.exec_command(cmd+" "+searchTerm)
        stdin.close()
        outerr=stderr.readlines()
        print("ERRORS: ", outerr)
        output=stdout.readlines()

        #TODO Output to HTML instead of console
        wiki_htmlView='''
        
        '''

        #Get result
        print("output: ",output)
        for items in output:
            print(items, end="")

        #Close client connection when finished
        client.close()
        return render_template('results.html', searchTerm=searchTerm, results=output)
    except Exception as e:
        print(e)
        return render_template('results.html', searchTerm=searchTerm, results="Something went wrong, please try again...")



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888)
