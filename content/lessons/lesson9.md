Hittills har våra variabler bara kunnat hålla ett enda värde åt gången (till exempel `x = 5`). Men i matematiken, särskilt inom statistik och sannolikhetslära, arbetar vi ofta med stora grupper av tal – som en serie mätvärden, provresultat eller utfall från ett experiment.

För att spara många värden i en och samma variabel använder vi en **lista**.

### Vad är en lista?

En lista skapas genom att vi räknar upp alla värden med kommatecken mellan och sätter klammerparenteser `[]` runt dem. 

```python
# En lista med provresultat (procent)
resultat = [45, 82, 77, 91, 54, 77]

```

#### Färdiga funktioner för listor

Python har flera inbyggda funktioner som är perfekta för att snabbt analysera vår data:

* **`len(lista)`** – Ger dig antalet element i listan (listans längd).
* **`sum(lista)`** – Adderar alla tal i listan och ger dig den totala summan.
* **`min(lista)`** och **`max(lista)`** – Hittar det minsta respektive största värdet.
* **`lista.append(varde)`** – Lägger till ett nytt värde i slutet av listan.
* **`lista.remove(varde)`** tar bort ett värde
* **`lista.sort()`** sorterar listan


Om man vill komma åt ett specifikt element i listan kan man använda indexering. Det första elementet i listan har index 0, det andra index 1, och så vidare. `lista[0]` ger det första elementet, `lista[1]` det andra, och `lista[-1]` ger det sista elementet i listan.

#### Kodexempel: Färger

```python
färger = ['röd', 'orange', 'gul', 'grön', 'blå', 'indigo', 'violett']
```

<img src="/illustrations/list_illustration.png" alt="Exempel på lista" class="theory-image">

#### Kodexempel: Statistik över poäng

```python
poäng = [12, 15, 9, 21, 16]
poäng.append(3) # Lägger till poängen 3
poäng[2] = 10 # Ändrar poäng på index 2 (alltså det tredje)

print('Alla poäng:', poäng)

poäng.sort()
print('Alla poäng sorterade:', poäng)
```

Utskriften blir:
```text
Alla poäng: [12, 15, 10, 21, 16, 3]
Alla poäng sorterade: [3, 10, 12, 15, 16, 21]
```

### Tillämpning: Statistik och medelvärde

Inom statistiken vill vi ofta sammanfatta en datamängd. Med hjälp av de färdiga funktionerna ovan blir detta superenkelt i Python.

Som du vet är formeln för **medelvärde**:

$$\text{Medelvärde} = \frac{\text{Summan av alla värden}}{\text{Antalet värden}}$$

I Python kan vi skriva denna formel direkt med hjälp av `sum()` och `len()`.

```python
temperaturer = [12.5, 15.0, 14.2, 11.8, 16.1, 15.5, 13.9]

# Vi beräknar statistik med de färdiga funktionerna
antal_dagar = len(temperaturer)
total_summa = sum(temperaturer)
medel = total_summa / antal_dagar

print("Högsta temp:", max(temperaturer), "°C")
print("Lägsta temp:", min(temperaturer), "°C")
print("Medeltemperaturen över", antal_dagar, "dagar var:", round(medel, 1), "°C")

```

### Tillämpning: Sannolikhet (frekvens)

Vi kan också använda listor för att spara utfall från sannolikhetsexperiment. Tänk dig att vi har kastat en tärning 10 gånger och sparat resultaten i en lista.

Med funktionen `.count()` kan vi räkna hur många gånger ett specifikt värde förekommer i listan. Detta kallas för värdets **absoluta frekvens**.

```python
tarnings_kast = [3, 6, 2, 6, 1, 4, 6, 5, 2, 6]

# Hur många gånger fick vi en 6:a?
antal_sexor = tarnings_kast.count(6)
totalt_antal = len(tarnings_kast)

# Relativ frekvens (Sannolikheten i experimentet)
sannolikhet_sexa = antal_sexor / totalt_antal

print("Antal sexor:", antal_sexor)
print("Experimentell sannolikhet för en sexa:", sannolikhet_sexa)

```

### Rita grafer med `matplotlib.pyplot`

När vi har data sparad i listor kan vi använda ett externt bibliotek som heter `matplotlib.pyplot` för att rita diagram och grafer.

Tänk på det som att du skapar en **värdetabell**: du skapar en lista för alla $x$-värden och en lista för alla motsvarande $y$-värden. Datorn prickar sedan in dessa koordinater $(x, y)$ i ett koordinatsystem och drar streck emellan dem.

#### Kodexempel: Rita en fysikalisk funktion

Här skapar vi en graf över hur temperaturen förändras under en dag:

```python
# Importera plotverktyget och ge det smeknamnet plt
import matplotlib.pyplot as plt 

# Vår värdetabell uppdelad i x- och y-värden (måste innehålla lika många element!)
tid_timmar = [8, 10, 12, 14, 16, 18]
temp_grader = [10, 14, 19, 21, 18, 13]

# 1. Skapa själva grafen utifrån listorna: plt.plot(x, y)
#    marker='o' lägger till en tydlig prick på varje koordinat
plt.plot(tid_timmar, temp_grader, marker='o') 

# 2. Snygga till koordinatsystemet med rubriker och rutnät
plt.title('Temperaturförändring under dagen')
plt.xlabel('Tid (klockslag)')
plt.ylabel('Temperatur (°C)')
plt.grid(True) # Visar ett rutnät, precis som i matteboken!

# 3. Visa fönstret med grafen
plt.show()
```

<img src="/illustrations/list_pyplot_physics.png" alt="PyPlot med fysik" class="theory-image">

Om vi vill göra matematiska funktioner vill vi inte själva räkna ut $y$-värden. De ska ju beräknas med ett funktionsuttryck. För att göra det enkelt att hantera matematiska funktioner kan vi importera `NumPy` (Numerical Python), som är ett grundläggande bibliotek för vetenskapliga beräkningar och dataanalys i Python. 

#### Kodexempel: Rita en matematisk funktion

Här skapar vi en graf över en andragradsfunktion och en rät linje:

```python
# Importera plotverktyget och ge det smeknamnet plt
import matplotlib.pyplot as plt 
# Importera matteverktyget och ge det smeknamnet np
import numpy as np

# Vår värdetabell uppdelad i x- och y-värden
x_varden = np.arange(-10, 10.1, 0.5)  # Ger värden ungefär som range
y_parabel = x_varden ** 2 - 2         # Beräknar y-värden med y = x² - 2
y_linje = 5 * x_varden + 40           # Beräkna y-värden med y = 5x + 40

# 1. Skapa själva graferna utifrån listorna: plt.plot(x, y)
plt.plot(x_varden, y_parabel, color='magenta') 
plt.plot(x_varden, y_linje, color='dodgerblue') 

# 2. Snygga till koordinatsystemet med rubriker och rutnät
plt.title('Parabel och linje')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True) # Visar ett rutnät, precis som i matteboken!

# 3. Visa fönstret med grafen
plt.show()
```

<img src="/illustrations/list_pyplot_math.png" alt="PyPlot med matematik" class="theory-image">


### Sammanfattning för minnet

* En **lista** skapas med `[]` och sparar flera värden i en sekvens.
* **`len(lista)`** ger antal värden, **`sum(lista)`** adderar alla värden.
* **Medelvärde** räknas ut genom `sum(lista) / len(lista)`.
* **`lista.count(x)`** räknar hur många gånger värdet $x$ finns i listan (absolut frekvens).
* Genom att skicka en $x$-lista och en $y$-lista till **`plt.plot(x, y)`** kan vi rita grafer och funktioner i ett koordinatsystem.
* Genom att använda **`numpy`** kan vi låta datorn skapa matematiska grafer.
