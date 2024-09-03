# Progetto per il mio esame di Tecnologie Web A.A. 2023/2024
## Descrizione del progetto
L'applicazione ha come obiettivo di creare una piattaforma per la gestione di lezioni private.
Un utente non registrato può visionare i vari tutor presenti sulla piattaforma e leggere le recensioni a riguardo.
Nel momento in cui vuole cercare di prenotare una lezione gli viene richiesto di registrarsi.
Ci sono due tipologie di utente: tutor e studente.
Il primo può creare delle disponibilità che verranno poi prenotate dagli studenti.
Gli studenti possono scrivere recensioni in merito ai tutor con i quali hanno sostenuto delle lezioni.
Le conferme delle varie operazioni sono seguite da un invio via email agli utenti interessati.
Per questo è essenziale configurare le proprie credenziali SMTP
"""python
EMAIL_HOST_USER = 'user'
EMAIL_HOST_PASSWORD = 'password'
'''
