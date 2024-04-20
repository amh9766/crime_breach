from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
import pandas as pd

app = Flask(__name__)

app.config["MYSQL_HOST"] = "127.0.0.1"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "city_jail"

loggedIn = False

mysql = MySQL(app)

# Functions

def runStatement(statement):
    cursor = mysql.connection.cursor()
    cursor.execute(statement)
    mysql.connection.commit()

def runSelectStatement(statement):
    cursor = mysql.connection.cursor()
    cursor.execute(statement)
    results = cursor.fetchall()
    df = ""
    if(cursor.description):
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=column_names)
    cursor.close()
    return df

# Pages

@app.route("/sign_in")
def sign_in():
    return render_template("index.html")

@app.route("/public/criminal_lookup")
def public_crim_lookup():
    return render_template("public_criminal_lookup.html")

@app.route("/public/criminal_lookup/search")
def public_crim_search():
    query = request.args.to_dict()

    # Check if query is empty; if so, default to viewing all entries
    empty = True 
    for values in query.values():
        if not values == "":
            empty = False
            break

    if empty:
        return redirect("/public/criminal_lookup/view_all")

    table = "criminals_publicview"
    searchRequest = "SELECT * FROM " + table + " WHERE "

    criteria = []

    if query["alias"] != "":
        criteria.append(table + ".`Alias` LIKE \"" + query["alias"] + "\"")
    if query["firstName"] != "":
        criteria.append(table + ".`First Name` LIKE \"" + query["firstName"] + "\"")
    if query["lastName"] != "":
        criteria.append(table + ".`Last Name` LIKE \"" + query["lastName"] + "\"")
    if query["violent"] != "":
        criteria.append(table + ".`Violent Offender?` LIKE \"" + query["violent"] + "\"")
    if query["probation"] != "":
        criteria.append(table + ".`On Probation?` LIKE \"" + query["probation"] + "\"")

    if len(criteria) == 1:
        searchRequest += criteria[0]
    else:
        for i in range(0, len(criteria)):
            if i == 0:
                searchRequest += criteria[i]
            else:
                searchRequest += " AND " + criteria[i]

    #if query["city"] != "":
    #    criteria.append(table + ".`` LiKE \"" + query["city"] + "\"")

    searchRequest += ";"

    print(searchRequest)

    return runSelectStatement(searchRequest).to_json() 

@app.route("/public/criminal_lookup/view_all")
def public_crim_view_all():
    return runSelectStatement("SELECT * FROM criminals_publicview;").to_json()

# Redirects
@app.route("/")
def root_redirect():
    if not loggedIn:
        return redirect("/sign_in")
    else:
        return redirect("/public/criminal_lookup")

@app.route("/crime")
def crime_redirect():
    crime_lookup = "/crime_lookup"
    if not loggedIn:
        return redirect("/public" + crime_lookup)
    else:
        return redirect("/admin" + crime_lookup)

@app.route("/criminal")
def criminal_redirect():
    criminal_lookup = "/criminal_lookup"
    if not loggedIn:
        return redirect("/public" + criminal_lookup)
    else:
        return redirect("/admin" + criminal_lookup)

@app.route("/officer")
def officer_redirect():
    officer_lookup = "/officer_lookup"
    if not loggedIn:
        return redirect("/public" + officer_lookup)
    else:
        return redirect("/admin" + officer_lookup)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000);
