Hittills har vi bestämt värdena på våra variabler direkt i koden, till exempel genom att skriva `basen = 10`. Men om vi vill göra ett program som andra kan använda – till exempel en app som räknar ut arean på vilken triangel som helst – vill vi att användaren själv ska kunna skriva in sina tal.

För att göra programmen interaktiva använder vi kommandot `input()`.

### Hur `input()` fungerar (och fällan du måste undvika)

När Python stöter på kommandot `input()` stannar programmet och väntar på att användaren ska skriva något på tangentbordet och trycka på Enter.

Det som användaren skriver sparas i en variabel:

```python
namn = input("Vad heter du? ")
print("Hej", namn)

```
<img src="/illustrations/input_illustration.png" alt="Exempel med input()" class="theory-image">

#### Fällan: Allt blir till text!

Här kommer det absolut viktigaste du behöver veta om `input()`: **Datorn tolkar ALLT som skrivs in som text (en sträng), även om användaren bara skriver siffror.**

Om användaren skriver in siffran `5`, så ser Python det inte som talet $5$, utan som texten `"5"`. Om du försöker räkna med text blir det fel:

```python
# OBS! Det här fungerar INTE som du tror:
tal = input("Skriv ett tal: ") # Användaren skriver 5
resultat = tal * 2             # Python gör text-multiplikation!
print(resultat)                # Svaret blir 55 (texten "5" två gånger), inte 10!

```


### Omvandla text till tal: `int()` och `float()`

För att skriva matteprogram måste vi berätta för Python att texten från `input()` ska omvandlas till ett faktiskt tal som går att räkna med. Detta kallas för att *typomvandla*.

Vi har två verktyg för detta:

* `int()` – Omvandlar texten till ett **heltal** (integer).
* `float()` – Omvandlar texten till ett **decimaltal** (flyttal).

#### Kodexempel: Räkna ut cirkelns area

Eftersom en radie kan vara ett decimaltal (t.ex. $3.5$ cm) är det bäst att använda `float()` när vi tar emot värdet. Vi kan baka ihop `float()` och `input()` på samma rad:

```python
# Vi tar emot texten och omvandlar den direkt till ett decimaltal
radie = float(input("Skriv cirkelns radie i cm: "))

# Formeln för area: pi * r^2
area = 3.14159 * radie * radie

print("Cirkelns area är:", area)

```

### Avrunda resultatet i en `print()`

När datorer räknar med decimaltal blir svaret ofta väldigt långt och fult. Om radien i exemplet ovan är $3$ blir arean $28.27431$. Det är sällan vi vill ha så många decimaler i ett mattesvar.

För att snygga till svaret använder vi funktionen `round()`. Den tar två saker i sin parentes: `round(talet_som_ska_avrundas, antal_decimaler)`.

Du kan använda `round()` direkt inuti ditt `print()`-kommando:

```python
pi = 3.14159
radie = 3
area = pi * radie * radie

# Vi avrundar arean till 2 decimaler direkt i utskriften
print("Cirkelns area är ungefär:", round(area, 2))
```

Om programmet körs nu kommer det att skriva ut: `Cirkelns area är ungefär: 28.27`

### Sammanfattning för minnet

* **`input()`** läser in det användaren skriver, men sparar det *alltid* som text.
* **`int(input(...))`** används när du vill ha ett **heltal** från användaren.
* **`float(input(...))`** används när du vill ha ett **decimaltal** från användaren.
* **`round(tal, 2)`** avrundar ett tal (i detta fall till 2 decimaler) och är perfekt att lägga inuti en `print()` för att få snygga mattesvar.