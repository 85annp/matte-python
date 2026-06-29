I matematiken stöter vi ofta på villkor. Vi kan till exempel säga att en funktion bara gäller om $x > 0$, eller så vill vi undersöka om ett tal är jämnt eller udda.

För att få Python att fatta beslut och köra olika kod beroende på om ett villkor är sant eller falskt använder vi **if-satser**.

### Jämförelseoperatorer (hur vi jämför värden)

Innan vi kan be datorn fatta beslut måste vi lära oss hur vi jämför saker i Python. Vi använder *jämförelseoperatorer*. De påminner mycket om de tecken du använder i matematiken, men eftersom vi skriver på ett tangentbord ser vissa lite annorlunda ut.

Här är de sex viktigaste jämförelseoperatorerna:

| Matematik | Python | Betydelse | Exempel |
| --- | --- | --- | --- |
| $=$ | `==` | Lika med | `x == 5` |
| $\neq$ | `!=` | Inte lika med | `x != 5` |
| $>$ | `>` | Större än | `x > 5` |
| $<$ | `<` | Mindre än | `x < 5` |
| $\ge$ | `>=` | Större än eller lika med | `x >= 5` |
| $\le$ | `<=` | Mindre än eller lika med | `x <= 5` |

⚠️ **Viktig skillnad:** 

* Ett enskilt likhetstecken (`=`) betyder **tilldelning** (Du lägger något i en variabel-låda, t.ex. `x = 5`).
* Dubbla likhetstecken (`==`) betyder **jämförelse** (Du frågar datorn: *"Är x lika med 5?"*).

### Grunden: `if` och `else`

En `if`-satser fungerar som en vägkorsning i koden. Om villkoret är sant svänger datorn av och kör en viss kod. Om det är falskt kan vi använda `else` (annars) för att berätta vad datorn ska göra istället.

#### Kodexempel: Är talet positivt?

Vi ber användaren skriva in ett tal och kontrollerar om det är större än noll.

```python
tal = float(input("Skriv ett tal: "))

if tal > 0:
    print("Talet är positivt!")
else:
    print("Talet är INTE positivt!")
```

**Titta noga på strukturen:**

1. Villkoret avslutas alltid med ett **kolon (`:`)**.
2. Koden som ska köras om villkoret är sant måste ha ett **indrag** (tabsteg).
3. `else:` skrivs längst ut till vänster igen och avslutas också med kolon.

### Flera alternativ med `elif`

Ibland räcker det inte med bara två alternativ (ja eller nej). Om vi tar exemplet ovan: vad händer om användaren skriver in exakt talet `0`? Noll är varken positivt eller negativt.

För att kontrollera flera villkor på rad använder vi `elif` (en förkortning av *else if*). Datorn kollar villkoren i ordning uppifrån och ned. Så fort den hittar ett villkor som är sant körs den koden, och sedan hoppar den förbi resten.

#### Kodexempel: Positivt, negativt eller noll?

Här utvecklar vi vårt program så att det hanterar alla tre matematiska fall:

```python
tal = float(input("Skriv ett tal: "))

if tal > 0:
    print("Talet är positivt!")
elif tal < 0:
    print("Talet är negativt!")
else:
    print("Talet är exakt noll!")
```

**Så här tänker datorn här:**

1. Är `tal > 0`? Om ja: skriv ut "positivt" och avsluta if-satsen. Om nej: gå vidare till nästa rad.
2. Är `tal < 0`? Om ja: skriv ut "negativt" och avsluta. Om nej: gå vidare.
3. Om *inget* av villkoren ovan stämde, körs koden under `else:` (det blir vår "fånga upp allt annat"-station).

<img src="/illustrations/if_elif_else_illustration.png" alt="Exempel med if-sats" class="theory-image">

### Sammanfattning för minnet

* Använd **`==`** för att kolla om något är lika med, och **`!=`** för inte lika med.
* Kom ihåg **kolon (`:`)** efter `if`, `elif` och `else`.
* Kom ihåg **indrag** på koden som ska köras inuti villkoret.
* **`if`** är det första villkoret.
* **`elif`** används för att testa nya villkor om de tidigare var falska.
* **`else`** körs bara om *inget* av de andra villkoren var sant.