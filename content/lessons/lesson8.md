I matematiken används exponentialfunktioner för att beskriva något som ökar eller minskar med en viss procentsats varje tidsperiod. Formeln skrivs ofta som:

$$y = C \cdot a^x$$

* $C$ är startvärdet (kapitalet, mängden bakterier, etc.).
* $a$ är förändringsfaktorn (t.ex. $1.03$ för en $3\text%$ ökning).
* $x$ är tiden (ofta i år, timmar eller dygn).

Istället för att bara räkna ut vad värdet blir efter ett visst antal år med formeln, kan vi låta en loop simulera vad som händer **år för år**. Det ger oss en mycket djupare förståelse för hur tillväxten faktiskt sker.


### Simulera förändring år för år

Tänk dig att du sätter in $10\ 000$ kr på ett bankkonto med $4\text%$ årlig ränta (förändringsfaktor $1.04$). Vi vill se hur pengarna växer under de första $5$ åren.

Genom att använda en `for`-loop kan vi låta datorn räkna ut det nya värdet för varje år genom att hela tiden multiplicera det gamla värdet med förändringsfaktorn.

```python
kapital = 10000
ranta = 1.04

# Loopen körs 5 gånger (för år 1 till 5)
for ar in range(1, 6):
    kapital = kapital * ranta
    print("Efter år", ar, "är kapitalet", round(kapital, 2), "kr.")
```

**Hur fungerar `kapital = kapital * ranta`?**
För varje varv tar datorn det nuvarande värdet i lådan `kapital`, multiplicerar det med $1.04$, och sparar det nya, högre värdet i samma låda. Det är precis så här ränta-på-ränta fungerar i verkligheten!

### Hitta x-värdet (tiden) med en `while`-loop och en räknare

Ett mycket vanligt problem i matematiken är att vända på frågan: *"Efter hur många år har pengarna fördubblats?"*.

Om vi vill veta när kapitalet har nått $20\ 000$ kr vet vi inte i förväg hur många varv loopen behöver snurra. Därför använder vi en `while`-loop. För att hålla reda på tiden (vårt $x$-värde i funktionen) skapar vi en egen variabel som fungerar som en **räknare**.

#### Kodexempel: Hur lång tid tar en fördubbling?

```python
kapital = 10000
ranta = 1.04

# Vi skapar en räknare för tiden (x-värdet) och startar på år 0
ar = 0 

# Så länge kapitalet är MINDRE än 20 000 kr ska loopen fortsätta
while kapital < 20000:
    kapital = kapital * ranta  # Pengarna växer med räntan
    ar = ar + 1                # Räknaren ökar med 1 år!

print("Det tar", ar, "år innan pengarna har fördubblats.")
print("Det exakta kapitalet är då", round(kapital, 2), "kr.")
```

#### Så här tänker datorn:

1. Innan loopen startar är `kapital = 10000` och `ar = 0`.
2. Datorn kollar villkoret: Är $10000 < 20000$? Ja, det är sant. Gå in i loopen!
3. Pengarna multipliceras med $1.04$ ($10400$ kr). Räknaren `ar` ökar till $1$.
4. Datorn hoppar upp och kollar villkoret igen: Är $10400 < 20000$? Ja. Loopen körs igen.
5. Detta upprepas ända tills `kapital` har passerat $20\ 000$ kr. Då blir villkoret falskt, loopen stängs av, och datorn skriver ut det slutgiltiga värdet på vår räknare `ar`.

### Sammanfattning för minnet

* **Exponentialfunktioner** handlar om upprepad multiplikation. Det passar perfekt för loopar.
* Genom att skriva `kapital = kapital * förändringsfaktor` inuti en loop skapar vi en automatisk ränta-på-ränta-effekt.
* När du vill ta reda på **när** ett visst värde uppnås (hitta $x$-värdet), använder du en `while`-loop kombinerat med en egen variabel (t.ex. `ar = ar + 1`) som fungerar som en tidsräknare.