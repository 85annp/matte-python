I den här lektionen ska vi titta på hur vi kan göra våra `if`-satser ännu smartare. Vi ska lära oss att kontrollera flera villkor samtidigt – som när ett tal måste ligga inom ett visst intervall – och vi ska introducera ett nytt räknesätt som hjälper oss att undersöka delbarhet.

### Restoperatorn: `%` (modulo)

Du minns säkert från grundskolan hur man dividerade innan man hade lärt sig decimaltal. Om du delade $11$ med $3$, så gick det $3$ hela gånger, och sedan fick du **2 i rest** (eftersom $3 \cdot 3 = 9$, och $11 - 9 = 2$).

I Python kallas detta för **modulo** och skrivs med procenttecknet `%`. Den här operatorn struntar i själva kvoten och ger dig *bara* resten som blir över efter en heltalsdivision.

**Exempel:**

* `17 % 5` ger 2 eftersom 17/5 = 3 hela och 2 i rest.
* `19 % 5` ger 4 eftersom 19/5 = 3 hela och 4 i rest.
* `20 % 5` ger 0 eftersom 20/5 = 4 hela och 0 i rest.

#### Matematisk koppling: Jämna och udda tal

Det absolut vanligaste användningsområdet för `%` i matematisk programmering är att undersöka om ett tal är **jämnt eller udda**, eller om ett tal är **delbart** med ett annat.

* Om `tal % 2 == 0` är resten noll när vi delar med 2, vilket betyder att talet är **jämnt**.
* Om resten blir 1 är talet **udda**.

#### Kodexempel: Kontrollera delbarhet

```python
tal = int(input("Skriv ett heltal: "))

if tal % 2 == 0:
    print("Talet är ett jämnt tal.")
else:
    print("Talet är ett udda tal.")
```

#### Kodexempel: Tidsomvandling
```python
sekunder = 125
minuter = sekunder // 60
resterande_sekunder = sekunder % 60
print(sekunder, 'sekunder är', minuter, 'minuter och', resterande_sekunder, 'sekunder')
```
Ger utskriften: `125 sekunder är 2 minuter och 5 sekunder.`

### Utökade villkor med `and` och `or` (och en smart matte-genväg!)

Ibland räcker det inte med att testa en sak i en `if`-sats. Vi vill kanske kontrollera om ett tal är delbart med flera olika tal, eller om ett tal ligger i ett visst intervall. Då använder vi de logiska operatorerna `and` och `or`.

#### `and` (båda villkoren måste vara sanna)

För att koden inuti `if`-satsen ska köras när du använder `and`, måste **både** villkoret till vänster och villkoret till höger vara sanna.

**Exempel:** Vi vill kontrollera om ett tal $x$ ligger i intervallet $[10, 50]$, det vill säga att $x$ ska vara större än eller lika med 10 **och** mindre än eller lika med 50.

Det traditionella sättet att skriva detta i programmering är:

```python
x = float(input("Skriv ett tal: "))

if x >= 10 and x <= 50:
    print("Talet ligger i intervallet mellan 10 och 50!")
```

#### 💡 Matte-genvägen i Python!

Eftersom Python är skapat för att vara lättläst, har utvecklarna lagt till en fantastisk genväg som nästan inga andra programmeringsspråk har. Du kan skriva intervallet **exakt** som du gör i matematiken:

```python
x = float(input("Skriv ett tal: "))

# Detta betyder exakt samma sak som exemplet med 'and' ovan!
if 10 <= x <= 50:
    print("Talet ligger i intervallet mellan 10 och 50!")
else:
    print("Talet ligger utanför intervallet.")
```

Det här gör koden mycket renare och lättare att förstå för någon som är van vid matematisk notation!

#### `or` (minst ett av villkoren måste vara sant)

När du använder `or` räcker det att **ett** av villkoren är sant för att datorn ska köra koden. Det gör ingenting om båda är sanna, men minst ett måste stämma.

**Exempel:** Vi vill veta om ett tal är delbart med *antingen* 3 eller 5.

```python
tal = int(input("Skriv ett tal: "))

# Vi kollar om resten blir 0 när vi delar med 3 ELLER när vi delar med 5
if tal % 3 == 0 or tal % 5 == 0:
    print("Talet är delbart med 3, 5 eller båda!")
else:
    print("Talet är inte delbart med något av dem.")
```

### Sammanfattning för minnet

* **`%` (modulo)** ger dig *resten* vid en division (t.ex. `tal % 2 == 0` för jämna tal).
* **`and`** kräver och kontrollerar att flera villkor är sanna samtidigt.
* **Genväg för intervall:** I Python kan du skriva matematiska intervall direkt, som `10 <= x <= 50`, istället för att använda `and`.
* **`or`** kräver att **minst ett** av villkoren är sant.