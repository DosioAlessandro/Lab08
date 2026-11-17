from database.distributore_DAO import DistributoreDAO
from model.distributore_DTO import Distributore
from model.prezzo_DTO import Prezzo

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        prezzi = []
        for distributore in self._distributori:
            totale = 0
            prezzo_totale = 0
            lista_prezzi = distributore.get_prezzi()
            for prezzo in lista_prezzi:
                if prezzo.data.month == mese:
                    totale += 1
                    prezzo_totale += prezzo.prezzo_litro
            prezzo_medio = (prezzo_totale / totale)
            prezzi.append((distributore.nome, prezzo_medio))
        return prezzi

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__costo_ottimo, self.__sequenza_ottima = self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        risultato_migliore = (float("inf"), [])
        if giorno == 8:
            return costo_corrente, sequenza_parziale.copy()
        else:
            for i in prezzi_settimana:
                costo_corrente += prezzi_settimana[i][giorno - 1] * 100
                cambio = 0
                if ultimo_distributore is not None and ultimo_distributore != i:
                    costo_corrente += 5
                    cambio = 5
                sequenza_parziale.append(i)
                risultato = self.__ricorsione(sequenza_parziale, giorno + 1, i, costo_corrente, prezzi_settimana)
                if risultato[0] < risultato_migliore[0]:
                    risultato_migliore = risultato
                sequenza_parziale.pop(-1)
                costo_corrente -= prezzi_settimana[i][giorno - 1] * 100
                costo_corrente -= cambio
            return risultato_migliore

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        diz = {}
        for distributore in self._distributori:
            lista_prezzi = distributore.get_prezzi()
            giorni = []
            for prezzo in lista_prezzi:
                if prezzo.data.month == mese and 1 <= prezzo.data.day <= 7:
                    giorni.append(prezzo.prezzo_litro)
            diz[distributore.id] = giorni
        return diz