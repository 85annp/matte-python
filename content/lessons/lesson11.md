I matematiken stöter vi ofta på situationer där saker händer i flera steg, eller där vi måste undersöka kombinationer av flera olika variabler. För att göra detta i Python använder vi nästlade slingor. Det betyder helt enkelt att vi placerar en loop inuti en annan loop.

**Tänk på det som en klocka:** Den inre loopen är som minutvisaren, och den yttre loopen är som timvisaren. Minutvisaren (den inre loopen) måste gå ett helt varv runt innan timvisaren (den yttre loopen) kan flytta sig ett enda steg framåt.

Exempel:
```python
for timme in range(0, 12):
    for minut in range(0, 60):
        print(timme, minut)
```

<img src="/illustrations/nested_for_illustration.png" alt="Exempel på lista" class="theory-image">

### Kombinatorik och sannolikhet
När vi arbetar med sannolikhet i flera steg eller kombinatorik vill vi ofta lista alla möjliga utfall – det som i matematiken kallas för **utfallsrummet**. Med nästlade loopar kan vi enkelt kombinera element från två eller flera listor. När vi gör detta använder Python multiplikationsprincipen: om den första listan har *a* element och den andra har *b* element, kommer de nästlade looparna att köras totalt *a* &sdot; *b* gånger.

Exempel: Kombinera färger och nummer
Tänk dig att vi ska dra en färgad lapp (Röd, Blå, Grön) och sedan kasta en fyrsidig tärning (1, 2, 3, 4). Hur ser alla möjliga kombinationer ut?
```python
farger = ['Röd', 'Blå', 'Grön']
tarnings_sidor = [1, 2, 3, 4]

# Den yttre loopen väljer en färg i taget
for farg in farger:
    # För VARJE färg går den inre loopen igenom alla tärningssidor
    for tarning in tarnings_sidor:
        print(farg, 'och', tarning)
```
Utskriften blir:
```text
Röd och 1
Röd och 2
Röd och 3
Röd och 4
Blå och 1
Blå och 2
Blå och 3
Blå och 4
Grön och 1
Grön och 2
Grön och 3
Grön och 4
```

### Lösa ekvationer med flera obekanta
Vissa matematiska problem och ekvationer (särskilt så kallade diofantiska ekvationer där vi bara söker heltalslösningar) kan vara svåra att lösa algebraiskt. Datorer är däremot extremt snabba på att testa sig fram.

Genom att använda nästlade `for`-loopar med funktionen `range()` kan vi låta Python systematiskt testa tusentals kombinationer av *x* och *y* på bråkdelen av en sekund för att se vilka som löser ekvationen.

Exempel: Vi vill hitta alla positiva heltalslösningar till ekvationen: *x* + 5*y* = 31 där både *x* och *y* är heltal mellan 1 och 10.
```python
# Vi testar alla x-värden från 1 till 10
for x in range(1, 11):
    # För varje x-värde testar vi alla y-värden från 1 till 10
    for y in range(1, 11):
        # Vi kontrollerar om den aktuella kombinationen löser ekvationen
        if 3 * x + 5 * y == 31:
            print('Hittade en lösning! x =', x, 'y =', y)
```
Utskriften blir:
```text
Hittade en lösning! x = 2 y = 5
Hittade en lösning! x = 7 y = 2
```

### Sammanfattning för minnet

* **Nästlad loop:** En loop inuti en annan loop. Den inre loopen måste köras klart helt och hållet för varje enskilt steg som den yttre loopen tar
* **Kombinatorik:** Används för att skapa kombinationer mellan listor. Det totala antalet kombinationer följer multiplikationsprincipen.
* **Ekvationslösning:** Genom att låta den yttre loopen representera variabeln $x$ och den inre loopen representera variabeln $y$, kan vi söka igenom ett stort antal sifferkombinationer för att hitta korrekta heltalslösningar.