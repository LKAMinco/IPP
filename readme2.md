# Implementačná dokumentácia k 2. úlohe do IPP 2021/2022

* Meno a priezvysko: Milan Hrabovský
* Login: xhrabo15

## interpret.py

Na analýzu parametrov som použíl knižnicu argparse, ktorá zároveň vie vygenerovať aj nápovedu. Po spracovaní argumentov
program prejde prvý krát celý XML súbor a uloží všetky inštrukcie ako objekty do dictionary **instructions** a ich
argumenty ako zoznam v objekte kde sa po dokončení spracovávania inštrukcie zoradia všetky argumenty podľa poradia a po
dokončení prechodu XML suborom sa zoradia aj inštrukcie podľa orderu. Zároveň sa pri prvom prechode ukladaju nazvy
Labelov, ich pozícia v xml a vykonáva sa kontrola štruktúry xml. V druhom prechode sa vykonávajú jednotlívé inštrukcie,
kde sa spracovávaju postupne podľa toho ako su zoradené v poli.

## Objekty v interpret.py

### Instruction

Šablona ktora definuje inštrukciu, každá inštrukcia ma svoje meno, poradie, index v poli aby sa na nu dalo odkazat pri
skoku na label a pole argumentov. Trieda má dve metódy, **addArgument** ktorá pridava argumenty do zoznamu a
**checkOrdOfArgs**, ktorá usporiadava argumenty v zozname. Trieda bola zvolená pre jednoduchší priśtup k inštrukciam a
ich uchovavaniu v poli.

### Variable

Šablona pre premenné. Trieda udržiava nazov premennej, rámec, hodnotu a typ. Metoda triedy **updateVar** služí na
aktualizovanie hodnoty v premennej.

### Argument

Jednoduchá trieda ktorá služi na ulahčenie uchovavania dat o argumente,

### Stack

Jednoduchá implementácia zásobniku a operacii nad nim. Umôžnuje jednoduchší prístpu k zásobniku a operaciam s ním.

## Pomocné funkcie v interpret.py

* **getType** - vracia typ premennej
* **getValue** - ziskava hodnotu z premennej
* **putValue** - ukladáa hodnotu do premennej
* **checkVar** - kontroluje či existuje premenna v kokretnom rámci
* **checkFrame** - kontroluje či existuje zadaný rámec
* **getSymb** - získava hodnotu zo symbolu ktorý môže byt bud premenna alebo konštanta
* **checkConst** - kontroluje validitu konštanty
* **EOF** - kontroluje či nieje na konci súboru s inputmi

## test.php

Ako prvé sa spracovávajú parametre z príkazovej riadky, k čomu slúži funkcie parseArgs a pomocnáa trieda ArgumentParser
ktorá je šablonou pre argumenty a uchováva aktualnu konfiguráciu. Po spracovaní argumentov sa načítajú konkretna/všetky
zložka/y zo subormi kde sú testy a uložia sa do pole. Ďalej sú načítané a zoradné podľa abecedy jednotlívé testy z
každého súboru ktorý načítaný. Každý test je uložený ako objekt. Trieda **TestCase** definuje tvar a operacie nad testami.
TestCase obsahuje dve hlavné metódy **doParse** ktorá vykonáva testy parseru a **doInterpret** ktorá vykonáva testy
interpreteru. Pre jednoduchšie pracovanie s vysledkami testu, su výsledky uchovávané ako objekt ktorému je trieda
**TestResult** šablonou. Všetky výsledky testov su uchovanée v poli a na konci je podľa výsledkový vygenerovaný html
dokument s celkovým vyhodnotením. Na generáciu html služí trieda ResultPage, ktorá hned pri vytvorení objektu vygeneruje
hlavičku a zakladnu štruktúru html dokumentu a dalej sú generovane vysledky jednotlivých testov.
