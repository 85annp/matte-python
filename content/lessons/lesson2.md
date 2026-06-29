I matematiken är du van vid variabler som $x$ och $y$, till exempel i ekvationen $x + 5 = 12$. I programmering fungerar variabler på ett liknande sätt, men de är mycket mer flexibla!

En variabel i Python kan liknas vid en **låda med en etikett på**. I lådan kan du spara ett värde (ett tal, en text eller något annat). Etiketten är variabelns **namn**, så att du enkelt kan hitta och använda värdet senare.

När vi skriver `x = 5` i Python betyder det inte att $x$ är exakt samma sak som 5 för alltid. Det betyder: *"Ta talet 5 och lägg det i lådan som heter x"*. På samma sätt kan vi lägga en text i en variabel med till exempel `y = 'John'`.

<img src="/illustrations/variables_illustration.png" alt="Exempel med variabler" class="theory-image">

#### Kodexempel: Skapa och använda variabler

```python
# Vi skapar två variabler och lägger tal i dem
basen = 10
hojden = 5

# Vi använder variablerna för att räkna ut arean på en triangel
area = (basen * hojden) / 2

print("Triangelns area är:", area)
```

### Hur du namnger dina variabler

I matematiken använder vi oftast bara en enda bokstav ($x, y, z$) som variabel. I programmering blir koden mycket lättare att förstå om vi använder hela ord.

Det finns dock några viktiga regler och riktlinjer för hur man får döpa variabler i Python:

* **Inga å, ä eller ö:** Python kan bli förvirrat av svenska tecken i variabelnamn. Använd `a`, `a` och `o` istället (t.ex. `hojden` istället för `höjden`).
* **Inga mellanslag:** En variabel kan inte ha mellanslag i namnet. Om du vill ha flera ord använder du understreck `_`. Detta kallas för *snake_case* (t.ex. `antal_elever` eller `basta_resultat`).
* **Måste börja med en bokstav:** Ett variabelnamn får innehålla siffror, men det får inte *börja* med en siffra (t.ex. är `val_1` godkänt, men `1_val` är felaktigt).
* **Python är känsligt för stora och små bokstäver:** Variabeln `svar` och `Svar` är två helt olika lådor för Python! Använd <strong>bara små bokstäver</strong> (gemener) i dina variabelnamn.

**Tips för bra mattekod:** Ge dina variabler namn som beskriver vad de faktiskt gör. Skriv hellre `radie = 5` än `r = 5`. Det gör det mycket lättare att hitta fel i beräkningarna!

### Viktigt: Punkt istället för komma vid decimaltal

Det här är kanske det vanligaste felet i början, särskilt i Sverige!

I matematiken skriver vi ofta decimaltal med ett kommatecken (t.ex. $3,14$). **I Python måste du alltid använda punkt `.` som decimaltecken.**

```python
# RÄTT SÄTT: Python förstår att detta är talet pi
pi = 3.14

# FEL SÄTT: Detta kommer att krascha eller ge felaktigt resultat
pi = 3,14
```

#### Varför är det så?

Python använder internationell (amerikansk) standard där punkt är decimaltecken. I Python används kommatecknet `,` istället för att separera olika saker från varandra, till exempel olika element i en lista eller olika saker i en `print()`-funktion:

```python
# Här används kommatecknet för att separera texten från variabeln
pris = 49.50
print("Boken kostar", pris, "kronor.")
```

### Sammanfattning för minnet

* En **variabel** är som en namngiven låda där datorn sparar ett värde.
* Variabelnamn ska vara beskrivande, sakna mellanslag (använd `_`) och skrivas utan å, ä, ö.
* Använd alltid **punkt** `.` för decimaltal (t.ex. `0.5`). Kommatecken används för att separera olika saker i koden.