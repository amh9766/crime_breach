from flask import Flask, render_template, request, redirect, session, send_file
from flask_mysqldb import MySQL
from flask_hashing import Hashing
import pandas as pd
import os

app = Flask(__name__)
hashing = Hashing(app)

# "everyone" user account is used for general public usage of app
# "administrator" user account is used when logged in
# For demonstration purposes, their passwords will be:
#   "everyone" -> "every1"
#   "administrator" -> "adm!n"
# This is entirely done in MySQL, the commands for which are provided.

app.config["MYSQL_HOST"] = "127.0.0.1"
app.config["MYSQL_USER"] = "everyone"
app.config["MYSQL_PASSWORD"] = "every1"
app.config["MYSQL_DB"] = "city_jail"

app.config["UPLOAD_FOLDER"] = "/queries/"
app.secret_key = "S3CR3T"

mysql = MySQL(app)

# ---- FUNCTIONS ----

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

def getAliasList(ids):
    aliasRequest = "SELECT Alias FROM alias_publicview WHERE ID = "
    aliasList = []
    for crimID in ids:
        aliasList.append(runSelectStatement(aliasRequest + str(crimID) + ";")["Alias"].tolist())
    # DEBUG: Console print to view the list of aliases
    #print(aliasList)
    return aliasList

def getSentencesList(ids):
    sentencesRequest = "SELECT Type, Start, End FROM sentences_publicview WHERE ID = "
    sentencesList = []
    for crimID in ids:
        sentencesList.append(runSelectStatement(sentencesRequest + str(crimID) +
                                                ";").values.tolist())
    # DEBUG: Console print to view the list of sentences
    #print(sentencesList)
    sentenceLabels = ["Type", "Start Date", "End Date"]
    return sentencesList, sentenceLabels

def getCrimeCharges(ids):
    chargesRequest = "SELECT Code, Description, Status FROM charges_publicview WHERE ID = "
    chargesList = []
    for crimID in ids:
        chargesList.append(runSelectStatement(chargesRequest + str(crimID) +
                                              ";").values.tolist())
    # DEBUG: Console print to view the list of charges 
    print(chargesList)
    return chargesList 

def getAdminAliasList(ids):
    aliasRequest = "SELECT Alias FROM alias_privateview WHERE ID = "
    aliasList = []
    for crimID in ids:
        aliasList.append(runSelectStatement(aliasRequest + str(crimID) + ";")["Alias"].tolist())
    # DEBUG: Console print to view the list of aliases
    #print(aliasList)
    return aliasList

def getAdminSentencesList(ids):
    sentencesRequest = "SELECT Type, Start, End FROM sentences_privateview WHERE ID = "
    sentencesList = []
    for crimID in ids:
        sentencesList.append(runSelectStatement(sentencesRequest + str(crimID) +
                                                ";").values.tolist())
    # DEBUG: Console print to view the list of sentences
    #print(sentencesList)
    sentenceLabels = ["Type", "Start Date", "End Date"]
    return sentencesList, sentenceLabels

# ---- PUBLIC/ADMIN PAGES ----

@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        form = request.form.to_dict()

        app.config.update(
            MYSQL_USER="administrator",
            MYSQL_PASSWORD="adm!n"
        )

        # SHA256 hashing on password on backend and in database
        searchRequest = "SELECT COUNT(*) FROM Users WHERE Username LIKE \"" + form["userID"] + "\" AND Password LIKE \"" + hashing.hash_value(form["password"]) + "\";"
        searchResult = runSelectStatement(searchRequest)["COUNT(*)"][0]

        if searchResult == 0:
            app.config.update(
                MYSQL_USER="everyone",
                MYSQL_PASSWORD="every1"
            )

            return redirect("/sign_in")
        else:
            session["user"] = form["userID"]

            return redirect("/home/" + session["user"])
    else:
        return render_template("index.html")

@app.route("/home/<user>")
def admin_home(user):
    return render_template("home.html", name=user)

@app.route("/download_query")
def download():
    return send_file(os.path.join("queries", session["user"] + "query.json"),
                     as_attachment=True)

# ---- PUBLIC PAGES ----
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
        aliasCriteria = table + ".`ID` IN (SELECT ID FROM alias_publicview WHERE Alias LIKE \"" + query["alias"] + "\")"
        if len(criteria) == 0:
            searchRequest += aliasCriteria
        else:
            searchRequest += " AND " + aliasCriteria

    if sentenceStartSearch:
        sentenceStartCriteria = table + ".`ID` IN (SELECT ID FROM sentences_publicview WHERE Start >= DATE(" + query["sentenceStart"] + "))"
        if len(criteria) == 0 and not aliasSearch:
            searchRequest += sentenceStartCriteria
        else:
            searchRequest += " AND " + sentenceStartCriteria

    if sentenceEndSearch:
        sentenceEndCriteria = table + ".`ID` IN (SELECT ID FROM sentences_publicview WHERE End <= DATE(" + query["sentenceEnd"] + "))"
        if len(criteria) == 0 and (not aliasSearch and not sentenceStartSearch):
            searchRequest += sentenceEndCriteria
        else:
            searchRequest += " AND " + sentenceStartCriteria

    searchRequest += ";"
    # DEBUG: Console print to view the end-result SQL query
    #print(searchRequest)

    searchDF = runSelectStatement(searchRequest)
    searchList = searchDF.values.tolist()

    # Remove duplicates from observed IDs
    idList = list(set(searchDF["ID"].tolist()));
    #print(idList)

    sList, sLabels = getSentencesList(idList)

    return render_template("public_criminal_lookup_output.html",
                           data=searchList, aliases=getAliasList(idList),
                           sentences=sList, sentenceLabels=sLabels)

@app.route("/public/criminal_lookup/view_all")
def public_criminal_view_all():
    table = "criminals_publicview"
    searchRequest = "SELECT * FROM " + table + ";"

    searchDF = runSelectStatement(searchRequest)
    searchList = searchDF.values.tolist()

    # Remove duplicates from observed IDs
    idList = list(set(searchDF["ID"].tolist()))

    sList, sLabels = getSentencesList(idList)

    return render_template("public_criminal_lookup_output.html",
                           data=searchList, aliases=getAliasList(idList),
                           sentences=sList, sentenceLabels=sLabels)

@app.route("/public/crime_lookup/")
def public_crime_lookup():
    return render_template("public_crime_lookup.html")

@app.route("/public/crime_lookup/search")
def public_crime_search():
    query = request.args.to_dict()

    # Check if query is empty; if so, default to viewing all entries
    empty = True 
    for values in query.values():
        if not values == "":
            empty = False
            break

    if empty:
        return redirect("/public/crime_lookup/view_all")

    table = "crime_publicview"
    searchRequest = "SELECT * FROM " + table + " WHERE "

    criteria = []

    aliasSearch = False
    hearingSearch = False
    chargedSearch = False
    statusSearch = False
    codeSearch = False

    if query["alias"] != "":
        aliasSearch = True
    if query["hearingDate"] != "":
        hearingSearch = True
    if query["dateCharged"] != "":
        chargedSearch = True
    if query["chargeStatus"] != "":
        statusSearch = True
    if query["crimeCode"] != "":
        codeSearch = True

    if query["firstName"] != "":
        criteria.append(table + ".`First Name` LIKE \"" + query["firstName"] + "\"")
    if query["lastName"] != "":
        criteria.append(table + ".`Last Name` LIKE \"" + query["lastName"] + "\"")
    if query["status"] != "":
        criteria.append(table + ".`Status` LIKE \"" + query["status"] + "\"")
    if query["classification"] != "":
        criteria.append(table + ".`Classification` LIKE \"" + query["classification"] + "\"")

    if len(criteria) == 1:
        searchRequest += criteria[0]
    else:
        for i in range(0, len(criteria)):
            if i == 0:
                searchRequest += criteria[i]
            else:
                searchRequest += " AND " + criteria[i]

    if aliasSearch:
        aliasCriteria = table + ".`Criminal ID` IN (SELECT ID FROM alias_publicview WHERE Alias LIKE \"" + query["alias"] + "\")"
        if len(criteria) == 0:
            searchRequest += aliasCriteria
        else:
            searchRequest += " AND " + aliasCriteria

    if hearingSearch:
        hearingCriteria = table + ".`Crime ID` IN (SELECT `Crime ID` FROM " + table + " WHERE " + table + ".`Hearing Date` >= DATE(\"" + query["hearingDate"] + "\"))"
        if len(criteria) == 0 and not aliasSearch:
            searchRequest += hearingCriteria
        else:
            searchRequest += " AND " + hearingCriteria 

    if chargedSearch:
        chargedCriteria = table + ".`Crime ID` IN (SELECT `Crime ID` FROM " + table + " WHERE " + table + ".`Date Charged` >= DATE(\"" + query["dateCharged"] + "\"))"
        if len(criteria) == 0 and (not aliasSearch and not hearingSearch):
            searchRequest += chargedCriteria
        else:
            searchRequest += " AND " + chargedCriteria

    if statusSearch:
        statusCriteria = table + ".`Crime ID` IN (SELECT `Crime ID` FROM charges_publicview WHERE Status LIKE \"" + query["chargeStatus"] + "\")"
        if len(criteria) == 0 and (not aliasSearch and (not hearingSearch and not chargedSearch)):
            searchRequest += statusCriteria
        else:
            searchRequest += " AND " + statusCriteria

    if codeSearch:
        codeCriteria = table + ".`Crime ID` IN (SELECT ID from charges_publicview WHERE Code = " + query["crimeCode"] + ")"
        if len(criteria) == 0 and (not aliasSearch and (not hearingSearch and (not chargedSearch and not statusSearch))):
            searchRequest += codeCriteria 
        else:
            searchRequest += " AND " + codeCriteria 
    
    searchRequest += ";"
    # DEBUG: Console print to view the end-result SQL query
    print(searchRequest)

    searchDF = runSelectStatement(searchRequest)
    searchList = searchDF.values.tolist()

    # No necessity to remove duplicates since the view is on a per crime basis
    # as opposed to a per criminal basis
    criminalIDList = searchDF["Criminal ID"].tolist()
    crimeIDList = searchDF["Crime ID"].tolist()

    return render_template("public_crime_lookup_output.html",
                           data=searchList,
                           aliases=getAliasList(criminalIDList),
                           charges=getCrimeCharges(crimeIDList))

@app.route("/public/crime_lookup/view_all")
def public_crime_view_all():
    table = "crime_publicview"
    searchRequest = "SELECT * FROM " + table + ";"

    searchDF = runSelectStatement(searchRequest)
    searchList = searchDF.values.tolist()

    # No necessity to remove duplicates since the view is on a per crime basis
    # as opposed to a per criminal basis
    criminalIDList = searchDF["Criminal ID"].tolist()
    crimeIDList = searchDF["Crime ID"].tolist()

    return render_template("public_crime_lookup_output.html",
                           data=searchList,
                           aliases=getAliasList(criminalIDList),
                           charges=getCrimeCharges(crimeIDList))

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
    searchRequest = "SELECT * FROM " + table
    return render_template("public_officer_lookup_output.html",
                           data=runSelectStatement(searchRequest).values.tolist())

# ---- ADMIN PAGES ----
@app.route("/admin/crime_lookup/")
def admin_crime_lookup():
    return render_template("admin_crime_lookup.html")

@app.route("/admin/crime_lookup/search")
def admin_crime_search():
    query = request.args.to_dict()

    # Check if query is empty; if so, default to viewing all entries
    empty = True 
    for values in query.values():
        if not values == "":
            empty = False
            break

    if empty:
        return redirect("/admin/crime_lookup/view_all")

    table = "crime_privateview"
    searchRequest = "SELECT * FROM " + table + " WHERE "

    criteria = []

    aliasSearch = False
    hearingSearch = False
    chargedSearch = False
    statusSearch = False
    codeSearch = False


    criminalIdSearch = False
    chargeIdSearch = False
    crimeIdSearch = False

    if query["criminalID"] != "":
        criminalIdSearch = True
    if query["chargeID"] != "":
        chargeIdSearch = True    
    if query["crimeID"] != "":
        crimeIdSearch = True

    # perform the following if we are searching on ID
    if criminalIdSearch or chargeIdSearch or crimeIdSearch:
        if criminalIdSearch:
            criteria.append(table + ".`Criminal ID` = " + query["criminalID"] + "")
        if chargeIdSearch:
            criteria.append(table + ".`Charge ID` = " + query["chargeID"] + "")
        if crimeIdSearch:
            criteria.append(table + ".`Crime ID` = " + query["crimeID"] + "")


    # if query["alias"] != "":
    #     aliasSearch = True
    if query["hearingDate"] != "":
        hearingSearch = True
    if query["dateCharged"] != "":
        chargedSearch = True
    if query["chargeStatus"] != "":
        statusSearch = True
    if query["crimeCode"] != "":
        codeSearch = True

    # if query["firstName"] != "":
    #     criteria.append(table + ".`First Name` LIKE \"" + query["firstName"] + "\"")
    # if query["lastName"] != "":
    #     criteria.append(table + ".`Last Name` LIKE \"" + query["lastName"] + "\"")
    if query["crimeStatus"] != "":
        criteria.append(table + ".`Status` LIKE \"" + query["crimeStatus"] + "\"")
    if query["classification"] != "":
        criteria.append(table + ".`Classification` LIKE \"" + query["classification"] + "\"")

    if len(criteria) == 1:
        searchRequest += criteria[0]
    else:
        for i in range(0, len(criteria)):
            if i == 0:
                searchRequest += criteria[i]
            else:
                searchRequest += " AND " + criteria[i]

    # if aliasSearch:
    #     aliasCriteria = table + ".`Criminal ID` IN (SELECT ID FROM alias_publicview WHERE Alias LIKE \"" + query["alias"] + "\")"
    #     if len(criteria) == 0:
    #         searchRequest += aliasCriteria
    #     else:
    #         searchRequest += " AND " + aliasCriteria

    if hearingSearch:
        hearingCriteria = table + ".`Crime ID` IN (SELECT `Crime ID` FROM " + table + " WHERE " + table + ".`Hearing Date` >= DATE(\"" + query["hearingDate"] + "\"))"
        if len(criteria) == 0 and not aliasSearch:
            searchRequest += hearingCriteria
        else:
            searchRequest += " AND " + hearingCriteria 

    if chargedSearch:
        chargedCriteria = table + ".`Crime ID` IN (SELECT `Crime ID` FROM " + table + " WHERE " + table + ".`Date Charged` >= DATE(\"" + query["dateCharged"] + "\"))"
        if len(criteria) == 0 and (not aliasSearch and not hearingSearch):
            searchRequest += chargedCriteria
        else:
            searchRequest += " AND " + chargedCriteria

    if statusSearch:
        statusCriteria = table + ".`Crime ID` IN (SELECT `Crime ID` FROM charges_publicview WHERE Status LIKE \"" + query["chargeStatus"] + "\")"
        if len(criteria) == 0 and (not aliasSearch and (not hearingSearch and not chargedSearch)):
            searchRequest += statusCriteria
        else:
            searchRequest += " AND " + statusCriteria

    if codeSearch:
        codeCriteria = table + ".`Crime ID` IN (SELECT ID from charges_publicview WHERE Code = " + query["crimeCode"] + ")"
        if len(criteria) == 0 and (not aliasSearch and (not hearingSearch and (not chargedSearch and not statusSearch))):
            searchRequest += codeCriteria 
        else:
            searchRequest += " AND " + codeCriteria 
    
    searchRequest += ";"
    # DEBUG: Console print to view the end-result SQL query
    print(searchRequest)

    searchDF = runSelectStatement(searchRequest)
    # searchRequest2 = "SELECT c.`First` and c.`Last` FROM Criminals c WHERE c.Criminal_ID = " + query["criminalID"] + ""
    # print(searchRequest2)
    # first_and_last = runSelectStatement(searchRequest2)
    print(searchDF)
    # print(first_and_last)
    searchList = searchDF.values.tolist()
    print(searchList)

    # No necessity to remove duplicates since the view is on a per crime basis
    # as opposed to a per criminal basis
    criminalIDList = searchDF["Criminal ID"].tolist()
    crimeIDList = searchDF["Crime ID"].tolist()

    return render_template("admin_crime_lookup_output.html",
                           data=searchList,
                           aliases=getAliasList(criminalIDList),
                           charges=getCrimeCharges(crimeIDList))
def admin_crime_search():
    return render_template("admin_crime_lookup_output.html")

@app.route("/admin/crime_lookup/view_all")
def admin_crime_view_all():
    return render_template("admin_crime_lookup_output.html")

@app.route("/admin/officer_lookup/")
def admin_officer_lookup():
    return render_template("admin_officer_lookup.html")

@app.route("/admin/officer_lookup/search", methods=["GET", "POST"])
def admin_officer_search():
    if request.method == "POST":
        print(request.form.to_dict())
        return redirect("/admin/officer_lookup")
    query = request.args.to_dict()

    # Check if query is empty; if so, default to viewing all entries
    empty = True 
    for values in query.values():
        if not values == "":
            empty = False
            break

    if empty:
        return redirect("/admin/officer_lookup/view_all")

    table = "Officers"
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

    searchDF = runSelectStatement(searchRequest)
    searchList = searchDF.values.tolist()

    searchDF.to_json(os.path.join("queries", session["user"] + "query.json"),
                     orient="records")
    
    print(searchList)

    return render_template("admin_officer_lookup_output.html",
                           data=searchList)

@app.route("/admin/officer_lookup/view_all")
def admin_officer_view_all():
    table = "Officers"
    searchRequest = "SELECT * FROM " + table
    searchDF = runSelectStatement(searchRequest)

    searchDF.to_json(os.path.join("queries", session["user"] + "query.json"),
                     orient="records")

    return render_template("admin_officer_lookup_output.html",
                           data=runSelectStatement(searchRequest).values.tolist())

    return render_template("admin_officer_lookup_output.html")

@app.route("/admin/criminal_lookup/")
def admin_criminal_lookup():
    return render_template("admin_criminal_lookup.html")

@app.route("/admin/criminal_lookup/search")
def admin_criminal_search():
    query = request.args.to_dict()
    # print(query)

    # Check if query is empty; if so, default to viewing all entries
    empty = True 
    for values in query.values():
        if not values == "":
            empty = False
            break

    if empty:
        return redirect("/admin/criminal_lookup/view_all")

    table = "criminals_privateview"
    searchRequest = "SELECT * FROM " + table + " WHERE "

    criteria = []

    aliasSearch = False

    criminalIdSearch = False
    aliasIdSearch = False
    # sentenceIdSearch = False
    # poIdSearch = False



    if query["criminalID"] != "":
        criminalIdSearch = True
    if query["aliasID"] != "":
        aliasIdSearch = True

    # perform the following if we are searching on ID
    if criminalIdSearch or aliasIdSearch:
        # print(query["criminalID"])
        if criminalIdSearch:
            criteria.append(table + ".`Criminal ID` = " + query["criminalID"] + "")
        if aliasIdSearch:
            criteria.append(table + ".`Alias ID` = " + query["aliasID"] + "")


        if len(criteria) == 1:
            searchRequest += criteria[0]
        else:
            for i in range(0, len(criteria)):
                if i == 0:
                    searchRequest += criteria[i]
                else:
                    searchRequest += " AND " + criteria[i]

        searchRequest += ";"

        # DEBUG: Console print to view the end-result SQL query
        # print(searchRequest)

        searchDF = runSelectStatement(searchRequest)
        searchList = searchDF.values.tolist()
        # print(searchList)

        # Remove duplicates from observed IDs
        idList = list(set(searchDF["Criminal ID"].tolist()))

        sList, sLabels = getSentencesList(idList)

    # otherwise, perform the following if we are searching on other criteria
    else:
        if query["alias"] != "":
            aliasSearch = True

        if query["firstName"] != "":
            criteria.append(table + ".`Criminal First` LIKE \"" + query["firstName"] + "\"")
        if query["lastName"] != "":
            criteria.append(table + ".`Criminal Last` LIKE \"" + query["lastName"] + "\"")
        if query["violentOffender"] != "":
            criteria.append(table + ".`Violent Offender?` LIKE \"" + query["violentOffender"] + "\"")
        if query["probation"] != "":
            criteria.append(table + ".`On Probation?` LIKE \"" + query["probation"] + "\"")
        if query["violations"] != "":
            criteria.append(table + ".Violations LIKE \"" + query["violations"] + "\"")

        if len(criteria) == 1:
            searchRequest += criteria[0]
        else:
            for i in range(0, len(criteria)):
                if i == 0:
                    searchRequest += criteria[i]
                else:
                    searchRequest += " AND " + criteria[i]

        if aliasSearch:
            aliasCriteria = table + ".`Criminal ID` IN (SELECT ID FROM alias_publicview WHERE Alias LIKE \"" + query["alias"] + "\")"
            if len(criteria) == 0:
                searchRequest += aliasCriteria
            else:
                searchRequest += " AND " + aliasCriteria

        searchRequest += ";"
        # print(searchRequest)
        # DEBUG: Console print to view the end-result SQL query
        # print(searchRequest)

        searchDF = runSelectStatement(searchRequest)
        # for removing duplicates - can remove later
        searchDF = searchDF.drop_duplicates(subset='Criminal ID')
        searchList = searchDF.values.tolist()
        # print(searchList)

        # Grab unique IDs
        idList = list(set(searchDF["Criminal ID"].tolist()))

        sList, sLabels = getSentencesList(idList)

    return render_template("admin_criminal_lookup_output.html",
                           data=searchList, aliases=getAliasList(idList),
                           sentences=sList, sentenceLabels=sLabels)

@app.route("/admin/criminal_lookup/view_all")
def admin_criminal_view_all():
    table = "criminals_privateview"
    searchRequest = "SELECT * FROM " + table + ";"

    searchDF = runSelectStatement(searchRequest)
    searchList = searchDF.values.tolist()

    # Remove duplicates from observed IDs
    idList = list(set(searchDF["Criminal ID"].tolist()))

    sList, sLabels = getSentencesList(idList)

    return render_template("admin_criminal_lookup_output.html",
                           data=searchList, aliases=getAliasList(idList),
                           sentences=sList, sentenceLabels=sLabels)

# Redirects
@app.route("/")
def root_redirect():
    if session.get("user", None) == None:
        return redirect("/sign_in")
    else:
        return redirect("/home/" + session["user"])

@app.route("/crime")
def crime_redirect():
    crime_lookup = "/crime_lookup"
    if session.get("user", None) == None:
        return redirect("/public" + crime_lookup)
    else:
        return redirect("/admin" + crime_lookup)

@app.route("/criminal")
def criminal_redirect():
    criminal_lookup = "/criminal_lookup"
    if session.get("user", None) == None:
        return redirect("/public" + criminal_lookup)
    else:
        return redirect("/admin" + criminal_lookup)

@app.route("/officer")
def officer_redirect():
    officer_lookup = "/officer_lookup"
    if session.get("user", None) == None:
        return redirect("/public" + officer_lookup)
    else:
        return redirect("/admin" + officer_lookup)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
