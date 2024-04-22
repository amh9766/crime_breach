from flask import Flask, render_template, request, redirect, session, send_file, flash
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

def runStatement(statement, needAdmin=False):
    flushPermissions(needAdmin)
    cursor = mysql.connection.cursor()
    cursor.execute(statement)
    mysql.connection.commit()

def runSelectStatement(statement, needAdmin=False):
    flushPermissions(needAdmin)
    cursor = mysql.connection.cursor()
    cursor.execute(statement)
    results = cursor.fetchall()
    df = ""
    if(cursor.description):
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=column_names)
    cursor.close()
    return df

def flushPermissions(needAdmin):
    if (session.get("user", None) != None) or needAdmin:
        app.config.update(
            MYSQL_USER="administrator",
            MYSQL_PASSWORD="adm!n"
        )
    else:
        app.config.update(
                MYSQL_USER="everyone",
                MYSQL_PASSWORD="every1"
        )
        
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


def getAdminAliasList(ids):
    aliasRequest = "SELECT Alias FROM Alias WHERE Criminal_ID = "
    aliasList = []
    for crimID in ids:
        aliasList.append(runSelectStatement(aliasRequest + str(crimID) + ";")["Alias"].tolist())
    # DEBUG: Console print to view the list of aliases
    #print(aliasList)
    return aliasList

def getAdminSentencesList(ids):
    sentencesRequest = "SELECT Type, Start_date, End_date, Violations FROM Sentences WHERE Criminal_ID = "
    sentencesList = []
    for crimID in ids:
        sentencesList.append(runSelectStatement(sentencesRequest + str(crimID) +
                                                ";").values.tolist())
    # DEBUG: Console print to view the list of sentences
    #print(sentencesList)
    sentenceLabels = ["Type", "Start Date", "End Date", "Violations"]
    return sentencesList, sentenceLabels

def getAdminCrimeCharges(ids):
    chargesRequest = "SELECT Charge_ID, Crime_charges.Crime_code, Code_description, Charge_status, Fine_amount, Court_fee, Amount_paid, Pay_due_date FROM Crime_charges INNER JOIN Crime_codes ON Crime_charges.Crime_code = Crime_codes.Crime_code WHERE Crime_charges.Crime_ID = "

    chargesList = []
    for crimID in ids:
        chargesList.append(runSelectStatement(chargesRequest + str(crimID) +
                                              ";").values.tolist())
    # DEBUG: Console print to view the list of charges 
    #print(chargesList)
    return chargesList 

def getAdminOfficers(ids):
    officersRequest = "SELECT Officer_ID FROM Crime_officers WHERE Crime_ID = "
    officersList = []
    for crimID in ids:
        officersList.append(runSelectStatement(officersRequest + str(crimID) +
                                              ";").values.tolist())
    return officersList

def getAdminAppeals(ids):
    appealsRequest = "SELECT Appeal_ID, Filing_date, Hearing_date FROM Appeals WHERE Crime_ID = "
    appealsList = []
    for crimID in ids:
        appealsList.append(runSelectStatement(appealsRequest + str(crimID) +
                                              ";").values.tolist())
    #print(appealsList)
    return appealsList


# ---- PUBLIC/ADMIN PAGES ----

@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        form = request.form.to_dict()
        
        # SHA256 hashing on password on backend and in database
        searchRequest = "SELECT COUNT(*) FROM Users WHERE Username LIKE \"" + form["userID"] + "\" AND Password LIKE \"" + hashing.hash_value(form["password"]) + "\";"

        searchResult = runSelectStatement(searchRequest, True)["COUNT(*)"][0]

        if searchResult == 0:
            return redirect("/sign_in")
        else:
            session["user"] = form["userID"]

            return redirect("/home/" + session["user"])
    else:
        return render_template("index.html")

@app.route("/sign_out")
def sign_out():
    session.pop("user", None)
    return redirect("/sign_in")

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

    sentenceStartSearch = False
    sentenceEndSearch = False

    if query["alias"] != "":
        criteria.append(table + ".`ID` IN (SELECT ID FROM alias_publicview WHERE Alias LIKE \"" + query["alias"] + "\")")
    if query["sentenceStart"] != "":
        criteria.append(table + ".`ID` IN (SELECT ID FROM sentences_publicview WHERE Start >= DATE(" + query["sentenceStart"] + "))")
    if query["sentenceEnd"] != "":
        criteria.append(table + ".`ID` IN (SELECT ID FROM sentences_publicview WHERE End <= DATE(" + query["sentenceEnd"] + "))")
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
        criteria.append(table + ".`Criminal ID` IN (SELECT ID FROM alias_publicview WHERE Alias LIKE \"" + query["alias"] + "\")")
    if query["hearingDate"] != "":
        criteria.append(table + ".`Crime ID` IN (SELECT `Crime ID` FROM " + table + "WHERE " + table + ".`Hearing Date` >= DATE(\"" + query["hearingDate"] + "\"))")
    if query["dateCharged"] != "":
        criteria.append(table + ".`Crime ID` IN (SELECT `Crime ID` FROM " + table + "WHERE " + table + ".`Date Charged` >= DATE(\"" + query["dateCharged"] + "\"))")
    if query["chargeStatus"] != "":
        criteria.append(table + ".`Crime ID` IN (SELECT `Crime ID` FROM charges_publicview WHERE Status LIKE \"" + query["chargeStatus"] + "\"")
    if query["crimeCode"] != "":
        criteria.append(table + ".`Crime ID` IN (SELECT ID from charges_publicview WHERE Code = " + query["crimeCode"] + ")")
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

def getCrimeCharges(ids):
    chargesRequest = "SELECT Code, Description, Status FROM charges_publicview WHERE ID = "
    chargesList = []
    for crimID in ids:
        chargesList.append(runSelectStatement(chargesRequest + str(crimID) +
                                              ";").values.tolist())
    # DEBUG: Console print to view the list of charges 
    #print(chargesList)
    return chargesList 

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

    table = "Crimes"
    searchRequest = "SELECT * FROM " + table + " WHERE "

    criteria = []

    if query["criminalID"] != "":
        criteria.append(table + ".Criminal_ID = " + query["criminalID"])
    if query["crimeID"] != "":
        criteria.append(table + ".Crime_ID = " + query["crimeID"])
    if query["crimeStatus"] != "":
        criteria.append(table + ".Status LIKE \"" + query["crimeStatus"] + "\"")
    if query["classification"] != "":
        criteria.append(table + ".Classification LIKE \"" + query["classification"] + "\"")
    if query["hearingDate"] != "":
        criteria.append(table + ".Hearing_date >= DATE(\"" + query["hearingDate"] + "\")")
    if query["dateCharged"] != "":
        criteria.append(table + ".Date_charged >= DATE(\"" + query["dateCharged"] + "\")")
    if query["appealCutOffDate"] != "":
        criteria.append(table + ".Appeal_cut_date <= DATE(\"" + query["appealCutOffDate"] + "\")")
    if query["chargeStatus"] != "":
        criteria.append(table + ".Crime_ID IN (SELECT Crime_ID FROM Crime_charges WHERE Charge_status LIKE \"" + query["chargeStatus"] + "\")")
    if query["crimeCode"] != "":
        criteria.append(table + ".Crime_ID IN (SELECT Crime_ID from Crime_charges WHERE Crime_code = " + query["crimeCode"] + ")")
    
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
    #print(searchRequest)

    searchDF = runSelectStatement(searchRequest)
    #print(searchDF)
    searchList = searchDF.values.tolist()
    #print(searchList)

    # No necessity to remove duplicates since the view is on a per crime basis
    # as opposed to a per criminal basis
    criminalIDList = searchDF["Criminal_ID"].tolist()
    crimeIDList = searchDF["Crime_ID"].tolist()
    

    return render_template("admin_crime_lookup_output.html",
                           data=searchList,
                           charges=getAdminCrimeCharges(crimeIDList),
                           officers=getAdminOfficers(crimeIDList),
                           appeals=getAdminAppeals(crimeIDList))

@app.route("/admin/crime_lookup/view_all")
def admin_crime_view_all():
    searchRequest = "SELECT * FROM Crimes;"
    searchDF = runSelectStatement(searchRequest)
    searchList = searchDF.values.tolist()
    #print(searchList)

    # No necessity to remove duplicates since the view is on a per crime basis
    # as opposed to a per criminal basis
    criminalIDList = searchDF["Criminal_ID"].tolist()
    crimeIDList = searchDF["Crime_ID"].tolist()
    

    return render_template("admin_crime_lookup_output.html",
                           data=searchList,
                           aliases=getAdminAliasList(criminalIDList),
                           charges=getAdminCrimeCharges(crimeIDList),
                           officers=getAdminOfficers(crimeIDList),
                           appeals=getAdminAppeals(crimeIDList))

@app.route("/admin/crime_lookup/delete", methods=["GET", "POST"])
def admin_delete_crime():
    form = request.form.to_dict()

    recordNum = ""
    # Search for the record associated with the button press 
    for key in form.keys():
        if form[key] == "Delete Record":
            recordNum = key

    criminalID = form["crimeID-" + recordNum]
    deleteStatement = "DELETE FROM Crimes WHERE Crime_ID = " + criminalID + ";"
    runStatement(deleteStatement)

    return redirect("/admin/crime_lookup/")

@app.route("/admin/crime_lookup/add", methods=["GET", "POST"])
def admin_add_crime():
    form = request.form.to_dict()

    empty = False

    for value in form.values():
        if value == "":
            empty = True

    if empty:
        return redirect("/home/" + session["user"])

    insertStatement = "INSERT INTO Crimes(Crime_ID, Criminal_ID, Classification, Date_charged, Status, Hearing_date, Appeal_cut_date) VALUES (" + form["crimeID"] + ", " + form["criminalID"] + ", \"" + form["classification"] + "\", DATE(\"" + form["dateCharged"] + "\"), \"" + form["crimeStatus"] + "\", DATE(\"" + form["hearingDate"] + "\"), DATE(\"" + form["appealCutOffDate"] + "\"));"

    print(insertStatement)

    try:
        runStatement(insertStatement)
    except MySQLdb.Error:
        return redirect("/home/" + session["user"])
    else:
        return redirect("/admin/crime_lookup")

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

@app.route("/admin/officer_lookup/update", methods=["GET", "POST"])
def admin_update_officer():
    form = request.form.to_dict();

    for i in range(0, int(form["save"])):
        iStr = str(i)
        updateStatement = "UPDATE Officers SET Last = \"" + form["lastName-" + iStr] + "\", First = \"" + form["firstName-" + iStr] + "\", Precinct = \"" + form["precinct-" + iStr] + "\", Phone = " + form["officerPhone-" + iStr] + ", Status = \"" + form["officerStatus-" + iStr] + "\" WHERE Officer_ID = " + form["officerID-" + iStr] + ";"
        runStatement(updateStatement)

    return redirect("/admin/officer_lookup/")

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

    table = "Criminals"
    searchRequest = "SELECT * FROM " + table + " WHERE "

    criteria = []

    if query["alias"] != "":
        criteria.append(table + ".Criminal_ID IN (SELECT Criminal_ID FROM Alias WHERE Alias LIKE \"" + query["alias"] + "\")")
    if query["aliasID"] != "":
        criteria.append(table + ".Criminal_ID IN (SELECT Criminal_ID FROM Alias WHERE Alias_ID = " + query["aliasID"] + ")")
    if query["sentenceStart"] != "":
        criteria.append(table + ".Criminal_ID IN (SELECT Criminal_ID FROM Sentences WHERE Start_date >= DATE(\"" + query["sentenceStart"] + "\"))")
    if query["sentenceEnd"] != "":
        table + ".Criminal_ID IN (SELECT Criminal_ID FROM Sentences WHERE End_date <= DATE(\"" + query["sentenceEnd"] + "\"))"
    if query["criminalID"] != "":
        criteria.append(table + ".Criminal_ID = " + query["criminalID"])
    if query["firstName"] != "":
        criteria.append(table + ".First LIKE \"" + query["firstName"] + "\"")
    if query["lastName"] != "":
        criteria.append(table + ".Last LIKE \"" + query["lastName"] + "\"")
    if query["violentOffender"] != "":
        criteria.append(table + ".V_status LIKE \"" + query["violentOffender"] + "\"")
    if query["probation"] != "":
        criteria.append(table + ".P_status LIKE \"" + query["probation"] + "\"")
    if query["zip"] != "":
        criteria.append(table + ".Zip = " + query["zip"])
    if query["city"] != "":
        criteria.append(table + ".City LIKE \"" + query["city"] + "\"")
    if query["state"] != "":
        criteria.append(table + ".State LIKE \"" + query["state"] + "\"")

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
    print(searchRequest)

    searchDF = runSelectStatement(searchRequest)
    searchList = searchDF.values.tolist()

    # Remove duplicates from observed IDs
    idList = list(set(searchDF["Criminal_ID"].tolist()));
    #print(idList)

    sList, sLabels = getAdminSentencesList(idList)

    return render_template("admin_criminal_lookup_output.html",
                           data=searchList, aliases=getAdminAliasList(idList),
                           sentences=sList, sentenceLabels=sLabels)

@app.route("/admin/criminal_lookup/view_all")
def admin_criminal_view_all():
    table = "Criminals"
    searchRequest = "SELECT * FROM " + table + ";"

    searchDF = runSelectStatement(searchRequest)
    searchList = searchDF.values.tolist()

    # Remove duplicates from observed IDs
    idList = list(set(searchDF["Criminal_ID"].tolist()))

    sList, sLabels = getAdminSentencesList(idList)

    return render_template("admin_criminal_lookup_output.html",
                           data=searchList, aliases=getAdminAliasList(idList),
                           sentences=sList, sentenceLabels=sLabels)

@app.route("/admin/criminal_lookup/delete", methods=["GET", "POST"])
def admin_delete_criminal():
    form = request.form.to_dict();

    recordNum = ""
    # Search for the record associated with the button press 
    for key in form.keys():
        if form[key] == "Delete Record":
            recordNum = key

    criminalID = form["criminalID-" + recordNum]
    deleteStatement = "DELETE FROM Criminals WHERE Criminal_ID = " + criminalID + ";"
    runStatement(deleteStatement)

    return redirect("/admin/criminal_lookup/")

@app.route("/home/<user>")
def admin_home(user):
    return render_template("home.html", name=user)

@app.route("/download_query")
def download():
    return send_file(os.path.join("queries", session["user"] + "query.json"),
                     as_attachment=True)

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

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file('favicon.ico')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
