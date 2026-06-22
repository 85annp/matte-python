I matematiken stöter vi ofta på upprepningar. Det kan handla om att beräkna värden för en talföljd, göra en värdetabell för en funktion, eller addera hundra tal med ett summatecken.

Att göra detta för hand tar tid. I programmering använder vi en **for-loop** (eller *for-sats*) för att tala om för datorn att den ska upprepa en viss kodsekvens ett bestämt antal gånger.

### Grunden: Upprepa med `range()`

För att bestämma hur många gånger en loop ska köras använder vi funktionen `range()`.

Titta på det här exemplet:

```python
for i in range(5):
    print("Python är kul!")

```

#### Hur fungerar det?

1. `for i in range(5):` betyder: *"Skapa en räknarvariabel som heter i. Kör koden här nedanför 5 gånger."*
2. **Indraget (tabulatur/steg):** Lägg märke till att `print()`-raden är inskjuten ett par snäpp. Detta kallas *indrag* (indentering). All kod som är inskjuten hör till loopen och kommer att upprepas.
3. Räknaren `i` startar automatiskt på **0** och räknar uppåt med 1 för varje varv. Så i det här fallet kommer `i` att ha värdena 0, 1, 2, 3 och 4.

Vi kan skriva ut själva räknaren `i` för att se vad som händer:

```python
for i in range(5):
    print("Varv nummer:", i)

```

Detta program kommer att skriva ut:

```text
Varv nummer: 0
Varv nummer: 1
Varv nummer: 2
Varv nummer: 3
Varv nummer: 4

```

<img src="/illustrations/for_illustration.png" alt="Exempel med for-loop och range" class="theory-image">

### Kontrollera start, stopp och steg (aritmetiska talföljder)

I matematiken vill vi sällan starta på 0. Vi vill kanske starta på 1, eller räkna i steg om 2 (t.ex. bara jämna tal). Vi kan styra detta genom att ge `range()` upp till tre argument: `range(start, stopp, steg)`.

**Viktigt:** Stopp-värdet i `range()` är **exkluderat**. Loopen stannar alltså *innan* den når stopp-numret.

#### Exempel A: Start och stopp

Om vi vill räkna från 1 till 10 (och ha med 10), måste vi sätta stopp-värdet till 11.

```python
for i in range(1, 11):
    print(i) # Skriver ut 1, 2, 3... upp till 10

```

#### Exempel B: Skapa en aritmetisk talföljd (använda *steg*)

Vi vill skriva ut alla udda tal mellan 1 och 15. Vi startar på 1, sätter stopp till 16, och hoppar 2 steg i taget.

```python
for i in range(1, 16, 2):
    print(i) # Skriver ut 1, 3, 5, 7, 9, 11, 13, 15

```

### Matematisk tillämpning: Beräkna summor ($\sum$)

Ett klassiskt problem i matematiken är att beräkna summan av en talföljd, till exempel alla heltal från 1 till 100:


$$1 + 2 + 3 + 4 + ... + 100$$

För att lösa detta med en loop skapar vi en variabel (en "ackumulator") som vi kan kalla `summa`. Vi sätter den till 0 från början, och för varje varv i loopen lägger vi till räknaren `i`.

```python
summa = 0

# Loopen går från 1 till 100
for i in range(1, 101):
    summa = summa + i # Lägg till det aktuella talet till summan

print("Summan av talen 1 till 100 är:", summa)

```

**Hur raden `summa = summa + i` fungerar:** Kom ihåg att likhetstecknet betyder *"lägg i lådan"*. Raden betyder alltså: *"Ta det som redan ligger i lådan summa, lägg till värdet på i, och stoppa tillbaka det nya resultatet i lådan summa."*

### Sammanfattning för minnet

* En **for-loop** används för att upprepa kod ett bestämt antal gånger.
* Koden som ska upprepas måste ha ett **indrag** (vara inskjuten).
* **`range(5)`** loopar 5 gånger och räknaren går från 0 till 4.
* **`range(1, 11)`** startar på 1 och slutar på 10 (stopp-värdet 11 räknas inte med).
* **`range(1, 11, 2)`** det tredje talet bestämmer steget (räknar varannat tal).