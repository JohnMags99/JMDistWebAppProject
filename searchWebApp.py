from flask import Flask, render_template, request, url_for, flash
from sqlalchemy.util import counter
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
        #print result to the console (
        lines=[]
        print("output: ")
        for items in output:
            print(items, end="")
            lines.append(items.split('\n'))

        wiki_htmlView='''
            <!DOCTYPE html> 
            <html lang="en"> 
            <head> 
                <meta charset="UTF-8"> 
                <title>Results for '''+searchTerm+'''</title> 
                <!--Bootstrap Framework CDN-->
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet"
                    integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
                    integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz"
                        crossorigin="anonymous"></script>
            </head> 
            <body>
                <div class="container text-center">
                    <div class="row">
                        <div class="col-8">
                            <h1>wiki.py</h1>
                        </div>
                        <div class="col-4">
                            <a href="/" class="btn btn-primary">Back to Search</a>
                        </div>
                    </div> 
        '''
        # count if lines break more than once
        lineBreak = 0
        for line in lines:
            if not line[0].startswith("Oops"):
                #if the first line is the title/url/content line
                if line[0].startswith("title"):
                    lineBreak=0
                    wiki_htmlView+='''</div><div class="card">
                                        <div class="card-body container">
                                            <div class="row">
                                                <div class="col-10">
                                                    <h1 class="card-title">'''
                    # Split first line into title, url and content for title of card
                    title1 = line[0].split("title:", 1)
                    title2 = title1[1].split("URL:", 1)
                    title3 = title2[1].split("Content:", 1)
                    wiki_htmlView+=title2[0]+'</h1>'+\
                                    '</div>'+\
                                    '<div class=col><a href="'+title3[0]+'">Wiki Source</a></div></div>'+\
                                    '<br><h5 class="card-subtitle mb-2 text-muted">'+title3[1]+'</h5><br>'

                #if next line is subtitle, e.g., "==sub==
                elif line[0].startswith("=="):
                    lineBreak=0
                    subTitle=line[0].split("=")
                    wiki_htmlView+='<br><br><h6 class="card-subtitle mb-2">'+subTitle[2]+'</h6>'

                #if line break
                elif line[0] == '':
                    lineBreak+=1
                    if not lineBreak > 1:
                        wiki_htmlView+='<br>'

                #if standard text
                else:
                    lineBreak=0
                    wiki_htmlView+='<p>'+\
                                    line[0]+\
                                    '</p>'

        wiki_htmlView+=''' 
                        </div>                
                    </div>
                </div>
            </body> 
            </html> 
        '''
        #Close client connection when finished
        client.close()
        return wiki_htmlView
    except Exception as e:
        print(e)
        return render_template('results.html', searchTerm=searchTerm, results="Something went wrong, please try again...S")



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888)
