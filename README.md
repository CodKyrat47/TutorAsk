# Progetto per il mio esame di Tecnologie Web A.A. 2023/2024
## Descrizione del progetto
L'applicazione si pone l'obiettivo di creare una piattaforma per la gestione di lezioni private.<br>
Un utente non registrato può visionare i vari tutor presenti sulla piattaforma e leggere le recensioni a riguardo.<br>
Nel momento in cui vuole cercare di prenotare una lezione gli viene richiesto di registrarsi.<br>
Ci sono due tipologie di utente: tutor e studente.<br>
Il tutor può creare delle disponibilità che verranno poi prenotate dagli studenti.<br>
Gli studenti possono scrivere recensioni in merito ai tutor con i quali hanno sostenuto delle lezioni.<br>
Le conferme delle varie operazioni sono seguite da un invio via email agli utenti interessati.<br>
Per questo è essenziale configurare le proprie credenziali SMTP:
```python
EMAIL_HOST_USER = 'user'
EMAIL_HOST_PASSWORD = 'password'
```
Le modifiche vanno applicate nel file [tutorask/settings.py](tutorask/settings.py) e, per le funzioni di testing,
in [lessons/tests.py](lessons/tests.py).<br>
Inoltre bisogna aggiungere una directory con il nome *profile_imgs* nella directory *media*.<br>
La directory creata conterrà le immagini di profilo caricate dai tutor sulla piattaforma.
## Come eseguire il progetto
Una volta clonato il repository, bisogna assicurarsi di avere installato [pipenv](https://pypi.org/project/pipenv/).<br>
Dopodichè si eseguono i comandi seguenti nella directory:
```bash
pipenv install
pipenv shell
```
Per creare il DB digitare:
```bash
python manage.py migrate
```
Nel progetto è presente il file [tutorask/initcmds.py](tutorask/initcmds.py), il quale contiene funzioni per svuotare e popolare il DB.<br>
Se si vuole eseguire alcune funzioni bisogna decommentare le chiamate di funzione desiderate in fondo al file [tuorask/urls.py](tutorask/urls.py).<br>
Una volta sistemati tutti i dettagli, si può procedere con l'avvio del progetto:
```bash
python manage.py runserver
```
Per eseguire i file di testing presenti nelle varie applicazioni, scrivere il seguente comando:
```bash
python manage.py test nome_app
```
Per la prima esecuzione è consigliato l'utilizzo della funzione `init_db()`, in moodo tale da riempire il DB con dei valori fittizi ed evitare errori. 
