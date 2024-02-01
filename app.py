from functools import wraps

from flask import Flask, render_template, request, redirect, flash, session,make_response
from flask_mysqldb import MySQL
import pdfkit
app = Flask(__name__)


app.config['SECRET_KEY'] = 'ISLEM'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'gestion_stock'

mysql = MySQL(app)




def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:  # logged_in == true
            return f(*args, **kwargs)
        else:
            flash('you must be logged in ', 'error')
            return redirect('/')

    return wrap






@app.route('/')
def index():
    return render_template('login.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
        email = request.form.get('email')
        password = request.form.get('pass')
        # Check if account exists using MySQL
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM tbl_users WHERE email = %s AND password = %s', (email, password,))
        # Fetch one record and return result
        account = cur.fetchone()
        if (account):
            session['logged_in'] = True
            return redirect('/dashad')
           
        else:
            flash('Mot de passe invalide', 'error')
            return redirect('/')


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect('/')



# -----------------------------------------------------------ADMIN-----------------------------------------------------------------------------------------------
# dash admin
@app.route('/dashad')
@login_required
def dashad():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM produit')
    # Fetch one record and return result
    prdts = cur.fetchall()
    
    cur1 = mysql.connection.cursor()
    cur1.execute('SELECT * FROM commande')
    # Fetch one record and return result
    cmds = cur1.fetchall()
    
    cur2 = mysql.connection.cursor()
    cur2.execute('SELECT * FROM client')
    # Fetch one record and return result
    clts = cur2.fetchall()
    

 
        
    
    return render_template('dashad.html',nbrprd=len(prdts),nbrcmd=len(cmds),nbrclt=len(clts))

   




#gerer produit
@app.route('/produit')
@login_required
def produit():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM produit')
    # Fetch one record and return result
    prdts = cur.fetchall()
    return render_template('produit.html', prdts=prdts)


@app.route('/addprod',methods=['POST'])
@login_required
def addprod():
    nom=request.form.get('name')
    desc=request.form.get('desc')
    quant=request.form.get('quant')
    prix=request.form.get('prix')
    
    cur = mysql.connection.cursor()
    cur.execute('insert into produit (Nom_prod,Description,qantite,Prix_unit) values (%s,%s,%s,%s)',[nom,desc,quant,prix])
    mysql.connection.commit()
    flash('Product added successfully', 'success')
    return redirect('/produit')

@app.route('/updateprod/<string:id>',methods=['POST'])
@login_required
def updateprod(id):
    nom=request.form.get('name')
    desc=request.form.get('desc')
    quant=request.form.get('quant')
    prix=request.form.get('prix')
    
    cur = mysql.connection.cursor()
    sql='update  produit set  Nom_prod=%s,Description=%s,Qantite=%s,Prix_unit=%s where Code_prod=%s'
    data=(nom,desc,quant,prix,id)
    cur.execute(sql,data)
    mysql.connection.commit()
    flash('Product updated successfully', 'success')
    return redirect('/produit')

@app.route('/deleteprod/<string:id>',methods=['POST'])
@login_required
def deleteclass(id):
    cur = mysql.connection.cursor()
    sql='delete from  produit  where Code_prod=%s'
    cur.execute(sql,id)
    mysql.connection.commit()
    flash('Product deleted successfully', 'success')
    return redirect('/produit')



#gerer client
@app.route('/client')
@login_required
def client():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM client')
    # Fetch one record and return result
    clts = cur.fetchall()
    return render_template('client.html', clts=clts)


@app.route('/addclt',methods=['POST'])
@login_required
def addclient():
    nom=request.form.get('name')
    adress=request.form.get('adress')
    phone=request.form.get('phone')
 
    
    cur = mysql.connection.cursor()
    cur.execute('insert into client (name,adresse,phone) values (%s,%s,%s)',[nom,adress,phone])
    mysql.connection.commit()
    flash('client added successfully', 'success')
    return redirect('/client')

@app.route('/updateclt/<string:id>',methods=['POST'])
@login_required
def updateclient(id):
    nom=request.form.get('name')
    adress=request.form.get('adress')
    phone=request.form.get('phone')
    
    cur = mysql.connection.cursor()
    sql='update  client set  name=%s,adresse=%s,phone=%s where id=%s'
    data=(nom,adress,phone,id)
    cur.execute(sql,data)
    mysql.connection.commit()
    flash('Client updated successfully', 'success')
    return redirect('/client')

@app.route('/deleteclt/<string:id>',methods=['POST'])
@login_required
def deleteclient(id):
    cur = mysql.connection.cursor()
    sql='delete from  client  where id=%s'
    cur.execute(sql,id)
    mysql.connection.commit()
    flash('Product deleted successfully', 'success')
    return redirect('/client')



#gerer commande
@app.route('/commande')
@login_required
def commande():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM commande')
    # Fetch one record and return result
    cmds = cur.fetchall()
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM produit')
    # Fetch one record and return result
    prdts = cur.fetchall()
    return render_template('commande.html', cmds=cmds,prdts=prdts)


@app.route('/addcom',methods=['POST'])
@login_required
def addcom():
    quant=request.form.get('quant')
    id=request.form.get('prod_id')
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM produit where Code_prod=%s',[id])
    # Fetch one record and return result
    prd = cur.fetchone()
    if (int(quant)>prd[3]): 
        flash('Quantite is higher of Product', 'error')
        return redirect('/commande')
        
    else:    
        cur = mysql.connection.cursor()
        sql='update  produit set Qantite=%s where Code_prod=%s'
        data=(prd[3]-int(quant),id)
        cur.execute(sql,data)
    
        cur = mysql.connection.cursor()
        cur.execute('insert into commande (Code_prod,Quantite_cmd) values (%s,%s)',[id,quant])
        mysql.connection.commit()
        
        flash('Order added successfully', 'success')
        return redirect('/commande')

@app.route('/updatecom/<string:id>',methods=['POST'])
@login_required
def updatecom(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM commande where Code_cmd=%s',[id])
    # Fetch one record and return result
    cmd = cur.fetchone()
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM produit where Code_prod=%s',[cmd[1]])
    # Fetch one record and return result
    prd = cur.fetchone()
    quant=request.form.get('quant')

    if (int(quant)>prd[3]): 
        flash('Quantite is higher of Product', 'error')
        return redirect('/commande')
        
    else:
        
        cur = mysql.connection.cursor()
        sql='update  produit set Qantite=%s where Code_prod=%s'
        data=(prd[3]-int(quant),id)
        cur.execute(sql,data)
    
        cur = mysql.connection.cursor()
        cur.execute('update commande set Quantite_cmd=%s where Code_cmd=%s',[quant,id])
        mysql.connection.commit()
        
        flash('Order updated successfully', 'success')
        return redirect('/commande')

@app.route('/deletecom/<string:id>',methods=['POST'])
@login_required
def deletecom(id):
    cur = mysql.connection.cursor()
    sql='delete from  commande  where Code_cmd=%s'
    cur.execute(sql,id)
    mysql.connection.commit()
    flash('order deleted successfully', 'success')
    return redirect('/commande')

@app.route('/facture/<string:id>')
@login_required
def facture(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM commande inner join produit on commande.Code_prod=produit.Code_prod where commande.Code_cmd=%s',[id])
    # Fetch one record and return result
    cmd = cur.fetchone()
  
    return render_template('facture.html',cmd=cmd)

@app.route('/generate_pdf/<string:id>')
def generate_pdf(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM commande inner join produit on commande.Code_prod=produit.Code_prod where commande.Code_cmd=%s',[id])
    # Fetch one record and return result
    cmd = cur.fetchone()
    html = render_template('facture.html',cmd=cmd)

    # Generate PDF from HTML
    pdf = pdfkit.from_string(html, False)

    # Create a response object with PDF data
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=output.pdf'

    return response


if __name__ == '__main__':
    app.run()
