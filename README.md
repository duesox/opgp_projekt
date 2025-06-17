
# Hra Connect 4 (Python)
  Tento projekt je implementácia populárnej stolnej hry Connect 4 v Pythone pomocou knižnice pygame. Po spustení sa objaví menu, kde si hráč môže vybrať, či chce hrať na 1 PC (offline) alebo cez LAN sieť (online).

# 📄 Obsah 
- [Inštalácia](#-inštalácia)
- [Použitie](#-použitie)
- [Opis projektu](#ℹ%EF%B8%8F-opis-projektu)
- [Licencia](#%EF%B8%8F-licencia)

# 💾 Inštalácia
  Stiahnite si súbor hry ktorý obsahuje všetky potrebné knižnice a súbory pre spustenie hry. Tento súbor je už pripravený na spustenie bez nutnosti inštalácie ďalších závislostí. Stačí ho spustit, prípadne udeliť administrátorské práva, aby mohla hra komunikovať cez internet a môžete hrať! 🙂

# 🫳 Použitie
  Po prvom spustení aplikácie vyskočí administrátorské okno, ktoré je potrebné potvrdiť na fungovanie multiplayeru. Po spustení hry znova by sa to už nemalo zobrazovať. Potom sa klasicky zobrazí hlavné menu, kde hráč vyberie jeden z nasledujúcich režimov:
  ## Offline
  Dvaja hráči sa striedajú v hraní na jednom zariadení.
  ## Online
  Dvaja hráči sa môžu striedať v hraní na 2 rôznych zariadeniach cez LAN sieť.
  Po výbere režimu sa zobrazí herná obrazovka, kde sa hráči striedajú v hádzaní žetónov do mriežky. Hráči používajú rôzne farby žetónov a cieľom je vytvoriť sériu štyroch žetónov v rade.

  ## Ovládanie:
  - Kliknutím myšou na stĺpec umiestnite žetón do voľného riadku.
  - Po každom ťahu sa kontroluje, či niektorý hráč nevyhral.
  - Hra pokračuje, kým niekto nevyhrá alebo nedôjde k remíze.
# ℹ️ Opis projektu
  Tento projekt implementuje hru Connect 4 v Pythone pomocou knižnice pygame. Hra obsahuje:
- ### Menu na výber režimu hry
  Po spustení sa zobrazí menu, kde si hráči vyberú, či chcú hrať na 1 zariadení, alebo cez sieť na 2.
- ### Logika hry
  Hra hodnotí ťahy, vyhodnocuje víťaza a kontroluje remízu.
- ### Hlavné funkcie
  Herná doska je vizualizovaná pomocou pygame.
- ### Animácie
  Žetóny padajú do stĺpcov a po výhre sa spustí animácia oslavy.
- ### Skóre
  Zobrazuje skóre pre oboch hráčov.

# 🏛️ Licencia
Tento projekt je licencovaný pod MIT licenciou - pozri LICENSE pre viac informácií.
