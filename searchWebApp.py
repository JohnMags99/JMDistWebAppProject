from flask import Flask, render_template, request
import paramiko, zlib, mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.config['ENV'] = "Development"
app.config['DEBUG'] = True




db = 'CACHEDSEARCHES'
instance_ip = '13.53.193.43'
wiki_mysql_ip = '192.168.56.5'  # IP must be changed if instance is stopped and restarted
build_table = 'wiki_build'
cache_table = 'wiki_cache'



@app.route('/')
def searchHome():
    return render_template('search.html')



# Result Landing Page Function
@app.route('/getResult', methods=['POST'])
def getResult():
    search_term = request.form.get('wSearch')
    query = f"SELECT content_compress FROM {cache_table} WHERE search_term='" + search_term + "';"
    content = send_query(query, search_term, "", 1)

    if content:  # If content is not None (content was found)
        html_processed = process_output("in", content)
        return html_processed
    else:  # If content is not found, call wiki.py and store output
        content = get_wiki(search_term)
        return build_html(content, search_term)



# Clears all cached pages
@app.route('/clearCache')
def clearCache():
    query = f"DELETE FROM {cache_table};"
    send_query(query, "", "CLEAR", 0)
    return "<h1>All Cache Cleared<h1>"



# Function to execute wiki.py on instance and return result
def get_wiki(searched):
    try:
        # Command to activate venv before executing wiki.py
        command = "source wiki/wiki_env/bin/activate && python3 wiki.py"

        # Attempt to connect/ssh to the instance
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key = paramiko.RSAKey.from_private_key_file('/home/johnm/DistWebAppProj.pem')

        client.connect(hostname=instance_ip, username="johnm", pkey=key)

        # Executing wiki.py
        stdin, stdout, stderr = client.exec_command(f'{command} {searched}')
        stdin.close()

        outerr = stderr.readlines()
        print("ERRORS: ", outerr)

        result = stdout.readlines()

    except Exception as e:
        print(e)
        return render_template('error.html', searchTerm=searched,
                               results="Something went wrong, please try again...")

    finally:
        client.close()
        return result



# Function to submit query to db, data is data to be sent or blank if receiving. to_return should be 0 if sending, 1 if retrieving
def send_query(query, s_id, data, to_return):
    result = None
    try:
        connection = mysql.connector.connect(host=wiki_mysql_ip,
                                             port='6888',
                                             database=db,
                                             user='root',
                                             password='mypassword')

        if connection.is_connected():
            cursor = connection.cursor()

            if data:
                if data == "CLEAR":
                    cursor.execute(query)
                    connection.commit()

                else:
                    cursor.execute(query, (s_id, data))
                    connection.commit()

            else:
                cursor.execute(query)
                result = cursor.fetchone()

            print(f"'{query}' was sent successfully")

    except Error as e:
        print("Error while connecting to MySQL", e)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    if to_return == 1:
        if result:
            return result[0]



# Function to build HTML doc to return in /getResult. is_new used to split depending on if already cached
def build_html(content, search):
    query = f"SELECT body_compress FROM {build_table} WHERE pos='top1';"
    # Retrieve top1 and process
    c_top = send_query(query, "", "", 1)
    html_top1 = process_output("in", c_top)
    query = f"SELECT body_compress FROM {build_table} WHERE pos='top2';"
    # Retrieve top2 and process
    c_top = send_query(query, "", "", 1)
    html_top2 = process_output("in", c_top)
    # Retrieve bottom and process
    query = f"SELECT body_compress FROM {build_table} WHERE pos='bottom';"
    c_bottom = send_query(query, "", "", 1)
    html_bottom = process_output("in", c_bottom)

    html_build = ''''''

    for line in content:
        print(line)
        line = line.split('\n')
        line = line[0]

        if not line == '':
            # not including errors
            if not line.startswith("Oops"):
                # if the first line is the title/url/content line
                if line.startswith("title"):
                    html_build += '''</div></div></div></div></div><div class="card">
                                                                <div class="card">
                                                                    <div class="card-body container">
                                                                        <div class="row">
                                                                            <div class="col-10">
                                                                                <h1 class="card-title">'''

                    # Split first line into title, url and content for title of card
                    title1 = line.split("title:", 1)
                    title2 = title1[1].split("URL:", 1)
                    title3 = title2[1].split("Content:", 1)
                    html_build += title2[0] + '</h1>' + \
                                  '</div>' + \
                                  '<div class=col><a href="' + title3[0] + '">Wiki Source</a></div></div>' + \
                                  '<br><h5 class="card-subtitle mb-2 text-muted">' + title3[
                                      1] + '</h5><div><div>'

                # if next line is subtitle, e.g., "==sub==
                elif line.startswith("=="):
                    subTitle = line.split("=")
                    if len(subTitle) == 5:
                        html_build += '</div></div><div class="card"><div class="card-body container"><h4 class="card-title mb-2">' + \
                                      subTitle[2] + '</h4>'
                    elif len(subTitle) == 7:
                        html_build += '<br><h5 class="card-subtitle mb-2">' + subTitle[3] + '</h5>'
                    elif len(subTitle) == 9:
                        html_build += '<br><h6 class="card-subtitle mb-2">' + subTitle[4] + '</h6>'

                # if standard text
                else:
                    html_build += '<p>' + \
                                  line + \
                                  '</p>'
    html_build = html_top1 + search + html_top2 + html_build + html_bottom

    html_content = process_output("out", html_build)
    query = f"INSERT INTO {cache_table} (search_term,content_compress) VALUES (%s,%s);"
    send_query(query, search, html_content, 0)

    return html_build



# Function to process incoming and outgoing data from and to wiki_cache
def process_output(direction, data):
    if direction == "in":
        # data must be decompressed, then decoded
        data_decompressed = zlib.decompress(data)
        print(f"Size of compressed data : {len(data_decompressed)}")
        data_decoded = data_decompressed.decode('utf-8')
        print(f"Size of de-compressed data decoded: {len(data_decoded)}")
        print(data_decoded)
        return data_decoded
    elif direction == "out":
        data_encoded = bytearray()
        for line in data:
            data_encoded.extend(line.encode('utf-8'))
        print(f"Size of encoded data : {len(data_encoded)}")
        data_compressed = zlib.compress(data_encoded)
        print(f"Size of compressed data : {len(data_compressed)}")
        return data_compressed
    else:
        raise Exception("Something Went Wrong")



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888)
