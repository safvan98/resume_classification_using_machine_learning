from flask import Flask,render_template,request,flash,redirect,url_for
import os
import sqlite3
import pandas as pd
import comparison
from comparison import *
import contentEctraction
from contentEctraction import file
from sklearn.feature_extraction.text import TfidfVectorizer
app=Flask(__name__)
app.secret_key="123"
app.config['UPLOAD_FOLDER']=r"static\PDF"






# jd = contentEctraction.cleaned_jd
# score = jd_profile_comparison.match(cleaned_jd,resume)
con=sqlite3.connect("MyPDF.db")
con.execute("create table if not exists myfile(pid integer primary key,pdf TEXT)")
# con.execute("create table if not exists employeefile(pid integer primary key,pdf TEXT)")
con.close()

@app.route("/",methods=["GET","POST"])
def home():
    return render_template('home.html')

@app.route("/employer",methods=["GET","POST"])
def employer_upload():
    con = sqlite3.connect("MyPDF.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from myfile")
    data = cur.fetchall()
    con.close()



    if request.method == 'POST':
        upload_pdf = request.files['upload_PDF']
        if upload_pdf.filename!='':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], upload_pdf.filename)
            upload_pdf.save(filepath)
            con = sqlite3.connect("MyPDF.db")
            cur = con.cursor()
            cur.execute("insert into myfile(pdf)values(?)", (upload_pdf.filename,))
            con.commit()
            flash("File Upload Successfully", "success")

            con = sqlite3.connect("MyPDF.db")
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("select * from myfile")
            data = cur.fetchall()
            con.close()
            return render_template("employer.html", data=data,output=output)
    return render_template("employer.html",data=data,output=output)

@app.route('/update_record/<string:id>',methods=['GET','POST'])
def update_record(id):
    con = sqlite3.connect("MyPDF.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from myfile where pid=?",(id))
    data = cur.fetchall()
    con.close()

    if request.method == 'POST':
        try:
            upload_pdf = request.files['upload_PDF']
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], upload_pdf.filename)
            upload_pdf.save(filepath)
            con = sqlite3.connect("MyPDF.db")
            cur = con.cursor()
            cur.execute("UPDATE myfile SET pdf=? where pid=?", (upload_pdf.filename, id))
            con.commit()
            flash("Record Update Successfully", "success")
        except:
            flash("Record Update Failed", "danger")
        finally:
            return redirect(url_for("upload"))
            con.close()
    return render_template("update.html",data=data)

@app.route('/delete_record/<string:id>')
def delete_record(id):
    try:
        con = sqlite3.connect("MyPDF.db")
        cur = con.cursor()
        cur.execute("delete from myfile where pid=?", [id])
        con.commit()
        flash("Record Deleted Successfully", "success")
    except:
        flash("Record Deleted Failed", "danger")
    finally:
        return redirect(url_for("upload"))
        con.close()

@app.route('/match', methods=("POST","GET"))
def match():
    con = sqlite3.connect("MyPDF.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from myfile ")
    data = cur.fetchall()
    con.close()

    refile = contentEctraction.file
    jd = pdfextract(refile)
    cleaned_jd = cleanResume(str(jd))
    final_resumes = []

    i = 0
    while i < len(Rfiles):
        file = Rfiles[i]
        #     dat = create_profile(file)
        resumeText = str(pdfextract(file))
        cleaned = cleanResume(resumeText)
        final_resumes.append(cleaned)
        i += 1
    pickle.dump(obj_jd_profile_comparison, open("jd_profile_comparison.pkl", "wb"))
    x = len(final_resumes)
    pers = []
    for i in range(x):
        result = obj_jd_profile_comparison.match(final_resumes[i], cleaned_jd)
        #     print(result)
        pers.append(result)

    name_lis = []
    i = 0
    while i < len(Rfiles):
        file = Rfiles[i]
        base = os.path.basename(file)
        filename = os.path.splitext(base)[0]

        name = filename.split('_')
        name2 = name[0]
        name2 = name2.lower()
        name_lis.append(name2)
        i = i + 1

        in_text = final_resumes
        # terget=data['Category'].values

    vect = TfidfVectorizer(
        sublinear_tf=True,
        stop_words='english',
        max_features=400)

    vect.fit(in_text)

    in_Word_feature = vect.transform(in_text)

    loaded_model = pickle.load(open('final_model.pkl', 'rb'))
    prd1 = loaded_model.predict(in_Word_feature)
    # print(prd1)

    d = {'Advocate': 0, 'Arts': 1, 'Automation Testing': 2, 'Blockchain': 3, 'Business Analyst': 4, 'Civil Engineer': 5,
         'Data Science': 6, 'Database': 7, 'DevOps Engineer': 8, 'DotNet Developer': 9, 'ETL Developer': 10,
         'Electrical Engineering': 11, 'HR': 12, 'Hadoop': 13, 'Health and fitness': 14, 'Java Developer': 15,
         'Mechanical Engineer': 16, 'Network Security Engineer': 17, 'Operations Manager': 18, 'PMO': 19,
         'Python Developer': 20, 'SAP Developer': 21, 'Sales': 22, 'Testing': 23, 'Web Designing': 24}
    leng = len(prd1)
    fields = []
    for i in d:
        x = d.get(i)
        for j in range(leng):
            if x == prd1[j]:
                fields.append(i)

    # df = pd.DataFrame(data, columns=['Numbers'])
    data1 = {
        "Name": name_lis,
        "Match_Score": pers,
        "Predicted Feild":fields
    }

    output1=pd.DataFrame(data1)
    output=output1.sort_values(by=['Match_Score'], ascending=False).head(10)

    return render_template('output.html', tables=[output.to_html(classes='data')],titles=output.columns.values)

# @app.route('/view')
# def job_post():
#     return render_template('view.html',data=data1)



@app.route('/output', methods=("POST","GET"))

def output():



    return render_template('output.html', tables=[output.to_html(classes='data')],titles=output.columns.values)

@app.route("/employee",methods=["GET","POST"])
def employee_upload():
    con = sqlite3.connect("MyPDF.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from myfile")
    data = cur.fetchall()
    con.close()



    if request.method == 'POST':
        upload_pdf = request.files['upload_PDF']

        if upload_pdf.filename!='':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], upload_pdf.filename)
            upload_pdf.save(filepath)
            con = sqlite3.connect("MyPDF.db")
            cur = con.cursor()
            cur.execute("insert into myfile(pdf)values(?)", (upload_pdf.filename))
            con.commit()
            flash("File Upload Successfully", "success")

            con = sqlite3.connect("MyPDF.db")
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("select * from myfile")
            data = cur.fetchall()
            con.close()
            return render_template("employee.html", data=data,output=output)
    return render_template("employee.html",data=data,output=output)


if __name__ == '__main__':
    app.run(debug=True)