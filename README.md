# Progetto per il mio esame di Tecnologie Web A.A. 2023/2024
## Descrizione del progetto
L'applicazione si pone l'obiettivo di creare una piattaforma per la gestione di lezioni private.<br>
Un utente non registrato può visionare i vari tutor presenti sulla piattaforma e leggere le recensioni a riguardo.<br>
Nel momento in cui vuole cercare di prenotare una lezione gli viene richiesto di registrarsi.<br>
Ci sono due tipologie di utente: tutor e studente.<br>
Il tutor può creare delle disponibilità che verranno poi prenotate dagli studenti.<br>
Gli studenti possono scrivere recensioni in merito ai tutor con i quali hanno sostenuto delle lezioni.<br>
Le conferme delle varie operazioni sono seguite da un invio via email agli utenti interessati.<br>
Per questo è essenziale configurare le proprie credenziali SMTP
```python
EMAIL_HOST_USER = 'user'
EMAIL_HOST_PASSWORD = 'password'
```
Le modifiche vanno applicate nel file [tutorask/settings.py](tutorask/settings.py) e, per le funzioni di testing,
in [lessons/test.py](lessons/test.py).<br>
Inoltre bisogna aggiungere una directory con il nome profile_imgs nella directory media. La directory
create conterrà le immagini di profilo caricate dai tutor sulla piattaforma
## Come eseguire il progetto
