from flask import Flask, render_template
from flask_mysqldb import MySQL
import pandas as pd

app = Flask(__name__)

app.config["MYSQL_HOST"] = "127.0.0.1"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "city_jail"

mysql = MySQL(app)

def runStatement(statement):
    cursor = mysql.connection.cursor()
    cursor.execute(statement)
    results = cursor.fetchall()
    mysql.connection.commit()
    df = ""
    if(cursor.description):
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=column_names)
    cursor.close()
    return df

@app.route("/")
def hello_world():
    df = runStatement("SELECT * FROM Criminals;")
    for i, j in df.iterrows():
        print(i, j)
    return "Hello"

@app.route("/sign_in")
def sign_in():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True);
