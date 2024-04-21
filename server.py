from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from flask_hashing import Hashing
import pandas as pd

app = Flask(__name__)
hashing = Hashing(app)

# "everyone" user account is used for general public usage of app
# "administrator" user account is used when logged in
# For demonstration purposes, their passwords will be:
#   "everyone" -> "every1"
#   "administrator" -> "adm!n"
# This is entirely done in MySQL, the commands for which are provided.

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

@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        form = request.form.to_dict()

        # SHA256 hashing on password on backend and in database
        searchRequest = "SELECT COUNT(*) FROM users WHERE Username LIKE \"" + form["userID"] + "\" AND Password LIKE \"" + hashing.hash_value(form["password"]) + "\";"
        searchResult = runSelectStatement(searchRequest)["COUNT(*)"][0]

        if searchResult == 0:
            return redirect("/sign_in")
        else:
            loggedIn = True

            app.config.update(
                MYSQL_USER="everyone",
                MYSQL_PASSWORD="every1"
            )
            
            #NOTE: Change this to home page when there is one
            return redirect("/public/criminal_lookup")
    else:
        return render_template("index.html")

@app.route("/public/criminal_lookup")
def public_criminal_lookup():
    return render_template("public_criminal_lookup.html")

@app.route("/public/criminal_lookup/search")
def public_criminal_search():
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

    aliasSearch = False
    sentenceStartSearch = False
    sentenceEndSearch = False

    if query["alias"] != "":
        aliasSearch = True
    if query["sentenceStart"] != "":
        sentenceStartSearch = True
    if query["sentenceEnd"] != "":
        sentenceEndSearch = True

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

    if aliasSearch:
        #NOTE: change this to a public view table
        aliasCriteria = table + ".`ID` IN (SELECT Criminal_ID FROM Alias WHERE Alias LIKE \"" + query["alias"] + "\")"
        if len(criteria) == 0:
            searchRequest += aliasCriteria
        else:
            searchRequest += " AND " + aliasCriteria

    if sentenceStartSearch:
        sentenceStartCriteria = table + ".`ID` IN (SELECT Criminal_ID FROM Sentences WHERE Start_date >= DATE(" + query["sentenceStart"] + "))"
        if len(criteria) == 0 and not aliasSearch:
            searchRequest += sentenceStartCriteria
        else:
            searchRequest += " AND " + sentenceStartCriteria

    if sentenceEndSearch:
        sentenceStartCriteria = table + ".`ID` IN (SELECT Criminal_ID FROM Sentences WHERE End_date <= DATE(" + query["sentenceEnd"] + "))"
        if len(criteria) == 0 and (not aliasSearch and not sentenceStartSearch):
            searchRequest += sentenceStartCriteria
        else:
            searchRequest += " AND " + sentenceStartCriteria

    searchRequest += ";"
    # DEBUG: Console print to view the end-result SQL query
    print(searchRequest)

    searchDF = runSelectStatement(searchRequest)
    searchList = searchDF.values.tolist()

    # Remove duplicates from observed IDs
    idList = list(set(searchDF["ID"].tolist()));
    print(idList)

    return render_template("public_criminal_lookup_output.html",
                           data=searchList, aliases=getAliasList(idList))

def getAliasList(ids):
    # NOTE: change this to a public view table
    aliasRequest = "SELECT Alias FROM Alias WHERE Criminal_ID = "
    aliasList = []
    for crimID in ids:
        aliasList.append(runSelectStatement(aliasRequest + str(crimID))["Alias"].tolist())
    # DEBUG: Console print to view the list of aliases
    #print(aliasList)
    return aliasList

@app.route("/public/criminal_lookup/view_all")
def public_criminal_view_all():
    table = "criminals_publicview"
    searchRequest = "SELECT * FROM " + table + ";"

    searchDF = runSelectStatement(searchRequest)
    searchList = searchDF.values.tolist()

    # Remove duplicates from observed IDs
    idList = list(set(searchDF["ID"].tolist()));

    return render_template("public_criminal_lookup_output.html",
                           data=searchList, aliases=getAliasList(idList))

@app.route("/public/crime_lookup/")
def public_crime_lookup():
    return render_template("public_crime_lookup.html")

@app.route("/public/crime_lookup/search")
def public_crime_search():
    return render_template("public_crime_lookup_output.html")

@app.route("/public/officer_lookup/")
def public_officer_lookup():
    return render_template("public_officer_lookup.html")

@app.route("/public/officer_lookup/search")
def public_officer_search():
    query = request.args.to_dict()

    # Check if query is empty; if so, default to viewing all entries
    empty = True 
    for values in query.values():
        if not values == "":
            empty = False
            break

    if empty:
        return redirect("/public/officer_lookup/view_all")

    table = "officer_publicview"
    searchRequest = "SELECT * FROM " + table + " WHERE "

    criteria = []

    if query["badgeNumber"] != "":
        criteria.append(table + ".`Badge #` LIKE \"" + query["badgeNumber"] + "\"")
    if query["firstName"] != "":
        criteria.append(table + ".`First Name` LIKE \"" + query["firstName"] + "\"")
    if query["lastName"] != "":
        criteria.append(table + ".`Last Name` LIKE \"" + query["lastName"] + "\"")
    if query["precinct"] != "":
        criteria.append(table + ".`Precinct` LIKE \"" + query["precinct"] + "\"")
    if query["status"] != "":
        criteria.append(table + ".`Status` LIKE \"" + query["status"] + "\"")

    if len(criteria) == 1:
        searchRequest += criteria[0]
    else:
        for i in range(0, len(criteria)):
            if i == 0:
                searchRequest += criteria[i]
            else:
                searchRequest += " AND " + criteria[i]

    # DEBUG: Console print to view the end-result SQL query
    #print(searchRequest)

    searchList = runSelectStatement(searchRequest).values.tolist()

    return render_template("public_officer_lookup_output.html",
                           data=searchList)

@app.route("/public/officer_lookup/view_all")
def public_officer_view_all():
    table = "officer_publicview"
    searchRequest = "SELECT * FROM " + table;
    return render_template("public_officer_lookup_output.html",
                           data=runSelectStatement(searchRequest).values.tolist())

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
