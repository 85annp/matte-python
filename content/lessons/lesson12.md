Välkommen till den sista lektionen! Idag ska vi lägga bort kalkylerna och statistiken för en stund och istället använda programmering för att skapa konst. Vi ska bekanta oss med Pythons egna ritrobot: **Turtle**.

Turtle (sköldpaddan) är en klassisk programmeringsmiljö där du styr en liten pil (eller sköldpadda) över skärmen med kod. När sköldpaddan rör sig drar den ett streck efter sig, precis som en penna.

För att använda Turtle måste vi hämta en modul som inte fungerar här på webbsidan. För den här lektionen behöver du ladda ner och installera Thonny från <a href="https://thonny.org" target="_blank">https://thonny.org/</a>. Thonny är en enkel Python-miljö som fungerar bra med Turtle och gör det lätt att se ritningen i ett eget fönster. När du får upp editorn i Thonny kan du importera Turtle. Testa gärna att köra programmet med bara importen så att du ser att du har en fungerande miljö.


```python
import turtle
```

### Grunderna: Flytta pennan

Innan vi ritar former måste vi lära oss hur vi styr sköldpaddan. Tänk på det som att du ger instruktioner till någon som blint följer dina order i ett koordinatsystem.

De vanligaste kommandona är:

| Kommando | Betydelse | Exempel |
| --- | --- | --- |
| **`turtle.forward(steg)`** | Gå framåt ett visst antal steg (pixlar). | `turtle.forward(100)` |
| **`turtle.backward(steg)`** | Gå bakåt. | `turtle.backward(50)` |
| **`turtle.right(grader)`** | Sväng höger (medsols) i angivna grader. | `turtle.right(90)` |
| **`turtle.left(grader)`** | Sväng vänster (motsols) i angivna grader. | `turtle.left(120)` |

####💡 Enkel start 

Testa den här koden! Den ritar ett enkelt L.

```python
import turtle

turtle.forward(100) # Gå framåt
turtle.right(90)    # Sväng 90 grader höger
turtle.forward(50)  # Gå framåt igen

turtle.done()       # Måste stå sist för att fönstret inte ska stängas!
```

### Geometri och loopar: Rita polygoner

Det är nu det roliga börjar. För att rita en regelbunden polygon (en månghörning där alla sidor och vinklar är lika stora, t.ex. en kvadrat eller en liksidig triangel) måste vi upprepa två kommandon: `forward` och `right` (eller `left`).

Detta passar perfekt för en **for-loop**.

#### Matematiken bakom svängen (yttervinkeln)

Det vanligaste misstaget när man ska rita en triangel är att tänka: *"En triangel har vinkeln 60 grader, alltså ska jag svänga 60 grader"*.

**Detta är fel.** 60 grader är *innervinkeln*. Sköldpaddan bryr sig inte om innervinkeln; den bryr sig om hur mycket den måste *vrida sig* från den kurs den redan går på. Denna vinkel kallas **yttervinkel**.

<img src="/illustrations/turtle_angle.png" alt="Yttervinkel i Turtle" class="theory-image">


Matematiken är enkel: För att rita en fullständig, sluten polygon måste sköldpaddan vrida sig totalt ett helt varv, alltså **360 grader**.

**Formel för svängvinkeln:**
 
$$\text{Svängvinkel (yttervinkel)} = \frac{360}{\text{Antalet sidor}}$$


#### Kodexempel: Rita en kvadrat vs en triangel

**En kvadrat (4 sidor):**
Vi ska loopa 4 gånger. Vinkeln blir $360 / 4 = 90$ grader.

```python
import turtle

# Loopa 4 gånger för 4 sidor
for i in range(4):
    turtle.forward(100)
    turtle.right(90)     # 360 / 4 = 90

turtle.done()
```

**En liksidig triangel (3 sidor):**
Vi ska loopa 3 gånger. Vinkeln blir $360 / 3 = 120$ grader.

```python
import turtle

# Loopa 3 gånger för 3 sidor
for i in range(3):
    turtle.forward(100)
    turtle.right(120)    # 360 / 3 = 120 (Yttervinkeln!)

turtle.done()
```

### Generalisera: Rita VILKEN polygon som helst

Nu när vi har formeln kan vi kombinera allt vi lärt oss i kursen (variabler, input, matte och loopar) för att skapa ett program där användaren får bestämma vilken form vi ska rita.

```python
import turtle

# 1. Ta emot input från användaren
antal_sidor = int(input("Hur många sidor ska polygonen ha? "))
sidlangd = int(input("Hur lång ska varje sida vara? "))

# 2. Räkna ut svängvinkeln
vinkel = 360 / antal_sidor

# 3. Rita polygonen med en loop
turtle.color("blue") # Snygga till med färg!
turtle.pensize(3)    # Gör strecket tjockare!

for i in range(antal_sidor):
    turtle.forward(sidlangd)
    turtle.right(vinkel)

turtle.done()
```

**Avslutande tips:** 

Testa att köra programmet ovan och skriv in `100` som antal sidor och `5` som sidlängd. Vad ritar sköldpaddan då? Diskutera med din bänkgranne!

### Sammanfattning för minnet

* **Ladda ner Thonny** från <a href="https://thonny.org" target="_blank">https://thonny.org/</a> för att köra Turtle-program
* **`import turtle`** hämtar ritroboten.
* Använd **for-loopar** för att repetera sidor i polygoner.
* Sköldpaddan svänger i **yttervinklar**.
* För en regelbunden polygon är svängen **360 / antalet sidor**.
* Glöm inte **`turtle.done()`** längst ner i din kod!

**Tack för den här kursen, och lycka till med ditt framtida kodande inom matematiken! 😃**