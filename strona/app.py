# -*- coding: utf-8 -*-
from flask import Flask , render_template , request , redirect , session, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors


app = Flask(__name__)


app.secret_key = 'projekt_baza'
mysql = MySQL(app)
app.config['MYSQL_USER'] = 'test'
app.config['MYSQL_PASSWORD'] = 'test'
app.config['MYSQL_DB'] = 'mydb'
app.config['MYSQL_HOST'] = 'localhost'


#routing to strony glownej po zalogowaniu
@app.route('/home' , methods=['GET','POST'])
def home():
    msg=''
    #data=[]
    #sprawdzenie czy logowanie nastapiło w sesji jesli tak , pozwol wejsc na strone home.html
    if 'loggedin' in session:
        indeks = session['id']
        if request.method == 'POST' and 'id_car' in request.form:
            id_car = request.form['id_car']
            cursor = mysql.connection.cursor()
            cursor.execute('DELETE FROM Samochod WHERE idSamochod ={}'.format(id_car))
            mysql.connection.commit()
            print("usuwanie complete")
            msg ="Samochód zostal usuniety"

        if request.method == 'POST' and 'marka' in request.form and 'model' in request.form and 'wersja' in request.form and 'rok' in request.form and 'vin' in request.form and 'silnik' in request.form and 'paliwo' in request.form and 'przebieg' in request.form:
            marka = request.form['marka']
            model = request.form['model']
            wersja = request.form['wersja']
            rok = request.form['rok']
            vin = request.form['vin']
            silnik = request.form['silnik']
            paliwo = request.form['paliwo']
            przebieg = request.form['przebieg']

            if not marka or not model or not wersja or not rok or not vin or not silnik or not paliwo or not przebieg:
                msg = "Brak wszytskich danych"
            else:
                cursor = mysql.connection.cursor()
                cursor.execute('INSERT INTO Samochod (Marka,Model,Wersja,Rok_produkcji,VIN,Silnik,Rodzaj_paliwa,Przebieg,idUzytkownika) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',(marka,model,wersja,rok,vin,silnik,paliwo,przebieg,indeks))      
                mysql.connection.commit()
                msg="Samochod zostal dodany"

        print("tuz przed adresem")        
        if request.method == 'POST' and 'miasto' in request.form and 'ulica' in request.form and 'kod_pocztowy' in request.form and 'nr_domu' in request.form and 'nr_tel_p' in request.form:
            miasto = request.form['miasto']
            ulica = request.form['ulica']
            kod_pocztowy = request.form['kod_pocztowy']
            nr_domu = request.form['nr_domu']
            nr_tel_p = request.form['nr_tel_p']
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * From Adres WHERE idUzytkownika = %s',(str(indeks)))
            account_2 = cursor.fetchone()
            
            if account_2:
                cursor = mysql.connection.cursor()
                cursor.execute('UPDATE Adres SET Miasto=%s , Ulica=%s , Kod_pocztowy=%s , Nr_domu=%s WHERE idUzytkownika=%s',(miasto,ulica,kod_pocztowy,nr_domu,indeks)) 
                mysql.connection.commit()
                cursor.execute('UPDATE Uzytkownik SET Nr_tel=%s WHERE idUzytkownika=%s',(nr_tel_p,indeks))
                mysql.connection.commit()
                msg="Dane zostaly zaktualizowane"
            else:
                cursor = mysql.connection.cursor()
                cursor.execute('INSERT INTO Adres (idUzytkownika,Miasto,Ulica,Kod_pocztowy,Nr_domu) VALUES (%s,%s,%s,%s,%s)',(indeks,miasto,ulica,kod_pocztowy,nr_domu))    
                mysql.connection.commit()
                msg="Dane zostaly dodane"


        #indeks = session['id']
        data=[]
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM Uzytkownik WHERE idUzytkownika = %s',(str(indeks)))
        data.append(cursor.fetchall())
        cursor.execute('SELECT * FROM Adres WHERE idUzytkownika = %s',(str(indeks)))
        data.append(cursor.fetchall())
        cursor.execute('SELECT * FROM Samochod WHERE idUzytkownika = %s',(str(indeks)))
        data.append(cursor.fetchall())
        

        cursor=mysql.connection.cursor()
        cursor.execute('SELECT * from widok_wiz where idUzytkownika= %s ORDER BY Data desc',(str(indeks)))
        data.append(cursor.fetchall())
    
        return render_template('home.html', data=data)



    return redirect(url_for('login'))

@app.route('/' ,methods=['GET','POST'])
def login():
    msg=''

    if request.method == 'POST' and 'login' in request.form and 'password' in request.form:
        login = request.form['login']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT idUzytkownika FROM Uzytkownik WHERE Login = %s AND Haslo = %s', (login,password))
        account = cursor.fetchone()

        if account[0]==1:
            session['loggedin'] = True
            session['id'] = account[0]
            return redirect(url_for('admin'))
        elif account:
            session['loggedin'] = True
            session['id'] = account[0]
            return redirect(url_for('home'))
        else:
            msg = 'Bledne dane, nie ma takiego konta'

    return render_template('index.html' , msg=msg)

@app.route('/rejestracja' , methods=['GET','POST'])
def singup():
    msg=''

    if request.method == 'POST' and 'login' in request.form and 'password' in request.form and 'imie' in request.form and 'nazwisko' in request.form and 'pesel' in request.form and 'nr_tel' in request.form:
        login = request.form['login']
        password = request.form['password']
        imie = request.form['imie']
        nazwisko = request.form['nazwisko']
        pesel = request.form['pesel']
        nr_tel = request.form['nr_tel']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Uzytkownik WHERE login = %s" , [login])
        account = cursor.fetchone()

        if account:
            msg = 'Login jest juz zajęty'
        elif not login or not password or not imie or not nazwisko or not pesel or not nr_tel:
            msg = 'Nie podano wszytskich danych'
        else:
            cursor.execute("INSERT INTO Uzytkownik (Imie,Nazwisko,PESEL,Nr_tel,Login,Haslo) VALUES (%s,%s,%s,%s,%s,%s)" , (imie,nazwisko,pesel,nr_tel,login,password))
            mysql.connection.commit()
            msg = 'Rejestracja zakonczona powodzeniem'

    elif request.method == 'POST':
        msg = "Prosze wprowadzic wszystkie dane!"

    return render_template('rejestracja.html' ,msg=msg)


@app.route('/home_a' ,methods=['GET','POST'])
def admin():
    msg=''
    data=[]

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM Mechanik')
    data.append(cursor.fetchall())

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM Uzytkownik')
    data.append(cursor.fetchall())

    return render_template('home_a.html' ,data=data ,msg=msg)
    
if __name__ == '__main__':
	app.run(debug=True)