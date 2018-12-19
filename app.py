from flask import Flask, render_template, request,session,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import hashlib
import time
app = Flask(__name__)
app.secret_key = 'samet'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Kullanicilar(db.Model):
    __tablename__ = "kullanicilar"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kadi = db.Column(db.Text, primary_key=True,nullable=False)
    sifre = db.Column(db.Integer)
    email = db.Column(db.Text, unique=True, nullable=False)
    yetki = db.Column(db.Integer)
class Kategoriler(db.Model):
    __tablename__ = "kategoriler"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kismi = db.Column(db.Text, unique=True, nullable=False)
class Urunler(db.Model):
    __tablename__ = "urunler"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    uismi = db.Column(db.Text, nullable=False)
    fiyat = db.Column(db.Integer, nullable=False)
    stok = db.Column(db.Integer, nullable=False)
    populer = db.Column(db.Text)
    resim = db.Column(db.Text)
    kategori_id = db.Column(db.Integer, db.ForeignKey('kategoriler.id'))
class Siparisler(db.Model):
    __tablename__ = "siparisler"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'))
    urun_id = db.Column(db.Integer, db.ForeignKey('urunler.id'))
    adet = db.Column(db.Text, nullable=False)
    fiyat = db.Column(db.Text,nullable=False)
    toplam = db.Column(db.Text,nullable=False)
    tarih = db.Column(db.Text,nullable=False)

db.create_all()
urunler = Urunler.query.all();
kategoriler = Kategoriler.query.all();
sepett=[]

@app.route('/')
def index():
    urunler = Urunler.query.all();
    kategoriler = Kategoriler.query.all();
    return render_template('index.html',urunler= urunler,kategoriler=kategoriler)
#kullanıcı işlemleri
@app.route('/dur')
def dur():
    return render_template('dur.html')
@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if request.method == 'GET':
        if 'giris_ok' in session:
            if session['giris_ok'] == True:
                return redirect(url_for('index'))
            else:
                return render_template('giris.html')
        else:
            session['giris_ok'] = False
            return redirect(url_for('giris'))
    else:
        email = request.form['email']
        sifre = request.form['pass']
        sifrelenmis = hashlib.sha256(sifre.encode("utf8")).hexdigest()

        print(sifrelenmis)
        if Kullanicilar.query.filter_by(email=email, sifre=sifrelenmis).first():
            veri = Kullanicilar.query.filter_by(email=email, sifre=sifrelenmis).first()
            session['giris_ok'] = True
            session['isim'] = veri.kadi
            session['id'] = veri.id
            session['yetki'] = veri.yetki
            session['sepet']=sepett
            return redirect(url_for('index'))
        else:
            return redirect(url_for('giris'))            
@app.route('/cikis')
def cikis():
    session['giris_ok'] = False
    session.pop('sepet',None)
    session.pop('isim',None)
    session.pop('id',None)
    session.pop('yetki',None)
    sepett.clear()
    session['sepet']=sepett
    return redirect(url_for('index'))
@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    if request.method == 'GET':
        if 'giris_ok' in session:
            if session['giris_ok'] == True:
                return redirect(url_for('index'))
            else:
                return render_template('kayit.html')
        else:
            session['giris_ok']=False
            return render_template('kayit.html')
    else:
        try:
            isim = request.form['username']
            email = request.form['email']
            sifre = request.form['pass']
            sifrelenmis = hashlib.sha256(sifre.encode("utf8")).hexdigest()
            kullanıcı = Kullanicilar(kadi=isim, sifre=sifrelenmis, email=email, yetki='0')
            db.session.add(kullanıcı)
            db.session.commit()
            return redirect(url_for('index'))
        except:
            return redirect(url_for('kayit'))

#admin ürün ekleme güncelleme silme işlemleri
@app.route('/ekle', methods=['GET','POST'])
def ekle():
    if 'giris_ok' in session:
        if (session['giris_ok'] == True):
            if request.method == 'GET':
                if (session["yetki"] == 1):
                    kategoriler = Kategoriler.query.all()
                    return render_template('ekle.html', kategoriler=kategoriler)
                else:
                    return redirect(url_for('dur'))
            else:
                uismi = request.form['uismi']
                fiyat = request.form['fiyat']
                stok = request.form['stok']
                resim = request.form['resim']
                kategorisi = request.form['kategorisec']
                yeniurun = Urunler(uismi=uismi, fiyat=fiyat, stok=stok, populer=0, resim=resim, kategori_id=kategorisi)
                db.session.add(yeniurun)
                db.session.commit()
                return redirect(url_for('ekle'))
        else:
            return redirect(url_for('giris'))
    else:
        session['giris_ok'] = False
        return redirect(url_for('giris'))
@app.route('/guncelle', methods=['GET','POST'])
def guncelle():
    if 'giris_ok' in session:
        if (session['giris_ok'] == True):
            if request.method == 'GET':
                if (session["yetki"] == 1):
                    kategoriler = Kategoriler.query.all()
                    urunler = Urunler.query.all()
                    return render_template('guncelle.html', urunler=urunler, kategoriler=kategoriler);
                else:
                    return redirect(url_for('dur'))
            else:
                urun = Urunler.query.filter_by(id=request.form['guncelleurun']).first()
                urun.uismi = request.form['uismi']
                urun.fiyat = request.form['fiyat']
                urun.stok = request.form['stok']
                urun.resim = request.form['resim']
                urun.kategori_id = request.form['kategorisec']
                db.session.add(urun)
                db.session.commit()
                return redirect(url_for('guncelle'))
        else:
            return redirect(url_for('giris'))
    else:
        session['giris_ok'] = False
        return redirect(url_for('giris'))
@app.route('/sil',methods=['GET','POST'])
def sil():
    if 'giris_ok' in session:
        if(session['giris_ok']==True):
            if request.method == 'GET':
                if(session["yetki"] == 1):
                    kategoriler = Kategoriler.query.all()
                    urunler = Urunler.query.all()
                    return render_template('sil.html',urunler=urunler,kategoriler=kategoriler)
                else:
                    return redirect(url_for('dur'))
            else:
                urunsec = request.form['urunsec']
                urun = Urunler.query.filter_by(id=urunsec).first()
                db.session.delete(urun)
                db.session.commit()
                return redirect(url_for('sil'))
        else:
            return redirect(url_for('giris'))
    else:
        session['giris_ok'] = False
        return redirect(url_for('giris'))
#sepet işlemleri
@app.route('/sepet')
def sepet():
    if 'giris_ok' in session:
        if(session['giris_ok']==True):
            sepetteki = session["sepet"]
            kategoriler = Kategoriler.query.all()
            return render_template('sepet.html',sepetteki=sepetteki,kategoriler=kategoriler)
        else:
            return render_template('giris.html')
    else:
        session['giris_ok'] = False
        return redirect(url_for('giris'))
@app.route('/sepeteEkle/<urunid>')
def sepeteEkle(urunid):
    if 'giris_ok' in session:
        if(session['giris_ok']==True):
            urungetir = Urunler.query.filter_by(id=urunid).first()
            durum=False
            sepett = session["sepet"]
            for bul in sepett:
                if str(bul['id'])==str(urunid):
                    durum=True
            if sepett==[]:
                adet=1
                hesap = adet * 0.99
                fiyat = int(urungetir.fiyat) + hesap
                toplam = adet * fiyat
                sepeteEkle = {
                    'id': urungetir.id,
                    'uismi': urungetir.uismi,
                    'fiyat': fiyat,
                    'resim': urungetir.resim,
                    'adet': adet,
                    'toplam':toplam
                }
                sepett.append(sepeteEkle)
            elif durum==True:
                sepet=[]
                for bul in sepett:
                    if str(bul['id'])==str(urunid):
                        adet=int(bul["adet"])
                        adet += 1
                        hesap = adet * 0.99
                        fiyat = int(bul['fiyat'])
                        toplam = (fiyat * adet) + hesap
                        bul['adet']=str(adet)
                        bul['toplam']=str(toplam)
                        sepet.append(bul)
                    else:
                        sepet.append(bul)
            else:
                adet=1
                hesap = adet * 0.99
                fiyat = int(urungetir.fiyat) + hesap
                toplam = adet * fiyat

                sepeteEkle = {
                    'id': urungetir.id,
                    'uismi': urungetir.uismi,
                    'fiyat': fiyat,
                    'resim': urungetir.resim,
                    'adet': adet,
                    'toplam':toplam
                }
                sepett.append(sepeteEkle)
            session["sepet"] = sepett
            return redirect(url_for('sepet'))
        else:
            return redirect(url_for('giris'))
    else:
        session['giris_ok'] = False
        return redirect(url_for('giris'))
@app.route('/urunSil/<urunid>')
def urunSil(urunid):
    if 'giris_ok' in session:
        if(session['giris_ok']==True):
            sepet=[]
            sepet = session["sepet"]
            sepett.clear()
            for sil in sepet:
                if str(sil['id'])!=str(urunid) :
                    sepett.append(sil)
            session["sepet"] = sepett
            return render_template('sepet.html',sepetteki=session["sepet"])
        else:
            return redirect(url_for('giris'))
    else:
        session['giris_ok'] = False
        return redirect(url_for('giris'))
@app.route('/urunGuncelle/<urunid>',methods=['POST','GET'])   
def urunGuncelle(urunid):
    if 'giris_ok' in session:
        if(session['giris_ok']==True):
            if request.method == 'GET':
                return redirect(url_for('index'))
            else:
                adet = int(request.form['adet'])
                sepet=[]
                sepet = session["sepet"]
                sepett.clear()
                for degistir in sepet:
                    if str(degistir['id'])==str(urunid):
                        fiyat = int(degistir['fiyat'])
                        hesap = adet * 0.99
                        toplam = (fiyat * adet)+hesap
                        degistir['adet']=str(adet)
                        degistir['toplam']=str(toplam)
                    sepett.append(degistir)
                session["sepet"] = sepett
                return redirect(url_for('sepet'))
        else:
            return redirect(url_for('giris'))
    else:
        session['giris_ok'] = False
        return redirect(url_for('giris'))
@app.route('/sepetibosalt',methods = ['GET'])
def sepetibosalt():
    if 'giris_ok' in session:
        if(session['giris_ok']==True):
            sepett.clear()
            session["sepet"] = sepett
            return redirect(url_for('sepet'))
        else:
            return redirect(url_for('giris'))
    else:
        session['giris_ok'] = False
        return redirect(url_for('giris'))
#urundetayı
@app.route('/urun/<urunid>')
def urun(urunid):
    urundetay = Urunler.query.filter_by(id=urunid).first()
    kategorisi = Kategoriler.query.filter_by(id=urundetay.kategori_id).first()
    kategoriler = Kategoriler.query.all()
    return render_template('urun.html',urundetay=urundetay,kategorisi=kategorisi,kategoriler=kategoriler)
#siparis verme sepetteki ürünleri siparislere kaydetme ve listeleme
@app.route('/siparisver')
def siparisver():
    if 'giris_ok' in session:
        if(session['giris_ok']==True):
            kid = session['id']
            sepett=session["sepet"]
            for urun in sepett:
                urun_id = int(urun["id"])
                adet = str(urun["adet"])
                urunn = Urunler.query.filter_by(id=urun_id).first()
                urunn.populer += int(adet)
                urunn.stok -= int(adet)
                db.session.add(urunn)
                db.session.commit()
                tarih = str(time.strftime("%x")+"-"+time.strftime("%X"))
                fiyat = urun["fiyat"]
                toplam = urun["toplam"]
                siparis = Siparisler(kullanici_id=kid, urun_id=urun_id, adet=adet, tarih=tarih,fiyat=fiyat,toplam=toplam)
                db.session.add(siparis)
                db.session.commit()
            sepett.clear()
            session["sepet"]=sepett
            return redirect(url_for('sepet'))
        else:
            return redirect(url_for('giris'))
    else:
        session['giris_ok'] = False
        return redirect(url_for('giris'))
@app.route('/siparis')
def siparis():
    if 'giris_ok' in session:
        if(session['giris_ok']==True):
            kullanici_id = session["id"]
            siparisverilen = Siparisler.query.filter_by(kullanici_id=kullanici_id)
            veri=[]
            for dön in siparisverilen:
                uruncagir = Urunler.query.filter_by(id = dön.urun_id).first()
                siparislerim ={
                'uismi' : str(uruncagir.uismi),
                'ufiyat' : dön.fiyat,
                'uresim' : str(uruncagir.resim),
                'uadet' : dön.adet,
                'utoplam': dön.toplam,
                'starih' : dön.tarih
                }
                veri.append(siparislerim)
            return render_template('siparisler.html',siparisler=veri,kategoriler=kategoriler)
        else:
            return redirect(url_for('giris'))
    else:
        session['giris_ok'] = False
        return redirect(url_for('giris'))
@app.route('/kategori/<kategori_id>')
def kategori(kategori_id):
    veri = Urunler.query.filter_by(kategori_id=kategori_id).order_by(desc(Urunler.populer))
    kategoriler = Kategoriler.query.all()
    return render_template('index.html',kategoriler=kategoriler,urunler=veri)
if __name__ == '__main__':
    app.run(debug=True)