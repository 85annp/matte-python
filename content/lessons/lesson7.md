Hittills har vi använt `for`-loopar för att upprepa kod. En `for`-loop är jättebra när vi i förväg vet exakt hur många varv loopen ska snurra (till exempel 10 eller 100 gånger).

Men i matematiken och programmeringen stöter vi ofta på problem där vi **inte vet i förväg** hur många steg som krävs. Vi vet bara att vi vill fortsätta *så länge ett visst villkor är sant*. Då använder vi en **while-loop** (eller *while-sats*).

### Jämförelse: `for` eller `while`?

För att förstå skillnaden kan vi titta på hur vi löser samma problem med båda looparna, och när den ena är bättre än den andra.

#### Exempel 1: Räkna till 5 (båda fungerar lika bra)

Om vi bara vill skriva ut talen 1 till 5 vet vi antalet varv i förväg.

**Med `for`:**

```python
for i in range(1, 6):
    print(i)

```

**Med `while`:**
Här måste vi skapa räknarvariabeln själva innan loopen, och komma ihåg att öka den manuellt inuti loopen.

```python
i = 1
while i <= 5:
    print(i)
    i = i + 1  # Öka i med 1 för varje varv, annars stannar loopen aldrig!

```

#### Exempel 2: Halvera ett tal tills det är mindre än 1 (bara `while` fungerar!)

Tänk dig att vi startar med talet 100. Vi vill dela talet med 2, om och om igen, så länge som talet är större än 1. Hur många halveringar krävs?

Eftersom vi inte vet antalet steg i förväg kan vi inte använda `range()`. Vi använder `while`:

```python
tal = 100
steg = 0

# Så länge talet är större än 1, fortsätt dela!
while tal > 1:
    tal = tal / 2
    steg = steg + 1
    print("Steg", steg, ": Talet är nu", tal)

print("Loopen är klar!")
print("Det krävdes", steg, "halveringar.")

```

<img src="/illustrations/while_illustration.png" alt="Exempel med while-sats" class="theory-image">

### Eviga loopar med `while True:` och `break`

Ibland vill vi att en loop ska starta och köra "för evigt", eller åtminstone tills vi själva bestämmer inuti loopen att det är dags att avbryta.

Genom att skriva `while True:` skapar vi en medveten evig loop, eftersom villkoret `True` (sant) alltid är sant. För att ta oss ut ur en sådan loop använder vi kommandot **`break`**. Så fort Python stöter på `break` avbryts loopen omedelbart, och programmet hoppar vidare till koden under loopen.

#### Matematisk tillämpning: Felhantering vid inmatning

Tänk dig och du bygger ett program som ska räkna ut roten ur ett tal. Eftersom vi inte kan ta roten ur ett negativt tal i reell matematik, vill vi tvinga användaren att skriva in ett positivt tal. Om de skriver ett negativt tal ska loopen snurra vidare och fråga igen.

```python
import math # Innehåller matematiska funktioner

while True:
    tal = float(input("Skriv ett positivt tal för att se dess kvadratrot: "))
    
    if tal >= 0:
        # Om talet är godkänt (större än eller lika med 0)
        break # Det här avbryter loopen omedelbart!
    else:
        print("Fel! Du kan inte skriva ett negativt tal. Försök igen.")

# Den här koden nås först när vi har kört "break"
rot = math.sqrt(tal)
print("Kvadratroten ur", tal, "är", rot)

```

**Varför är detta så smidigt?**

* Loopen kommer att fortsätta fråga användaren i all evighet om de fortsätter mata in negativa tal.
* Först när `if`-villkoret `tal >= 0` blir sant, körs `break`, loopen stängs av, och datorn räknar ut kvadratroten.

### Sammanfattning för minnet

* **`for`-loopar** används när du vet antalet varv i förväg (t.ex. med `range()`).
* **`while`-loopar** används när du vill att koden ska köras så länge ett visst villkor är sant (t.ex. `while tal > 1`).
* Om du använder en `while`-loop med en räknare måste du själv komma ihåg att ändra räknaren inuti loopen, annars skapar du en oavsiktlig evig loop.
* **`while True:`** skapar en medveten evig loop.
* **`break`** är nödutgången som avbryter en loop omedelbart och hoppar vidare i programmet.