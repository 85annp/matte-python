Välkommen till din första lektion i Python! Idag ska vi titta på hur vi får datorn att visa information på skärmen, och hur vi använder den som en kraftfull miniräknare.

För att datorn ska visa text eller siffror på skärmen använder vi kommandot `print()`. Det som du vill att datorn ska skriva ut placerar du inom parenteserna.

### Skriva ut text (strängar) på skärmen med `print()`

När du vill skriva ut vanlig text måste du sätta citattecken `''` eller `""` runt texten. Detta berättar för Python att det handlar om text (som programmerare kallar för en *sträng*).

Exempel:
```python
print('Hej världen!')
print('Välkommen till Python.')
```

### Skriva ut tal på skärmen med `print()`

Om du vill skriva ut tal eller göra matematiska beräkningar ska du **inte** använda citattecken. Skriver du citattecken tror datorn bara att det är text och kommer inte att räkna ut något.

Exempel:
```python
print('Svaret är', 42)
print(5 + 5) # Datorn kommer att räkna ut detta och skriva ut 10
```

<img src='/illustrations/print_illustration.png' alt='Exempel med print()' class='theory-image'>

### De fyra räknesätten (och ett bonus-sätt!)

I Python använder vi nästan samma symboler som i vanliga matematiken, men med några små skillnader (speciellt för multiplikation och division).

Här är de tecken du använder på tangentbordet:

| Räknesätt | Symbol i Python | Matematisk operation | Exempel | Resultat |
| :--- | :--- | :--- | :--- | :--- |
| **Addition** | `+` | Plus | `7 + 3` | `10` |
| **Subtraktion** | `-` | Minus | `10 - 4` | `6` |
| **Multiplikation** | `*` | Gånger | `4 * 5` | `20` |
| **Division (vanlig)** | `/` | Delat med (med decimaler) | `9 / 2` | `4.5` |
| **Heltalsdivision** | `//` | Delat med (utan decimaler) | `9 // 2` | `4` |


### Skillnaden mellan `/` och `//`

I matematiken är vi vana vid att division kan ge decimaltal. I Python finns det två olika sätt att dela tal på, och det är viktigt att hålla koll på skillnaden:

#### Vanlig division: `/`
Det här fungerar exakt som på din vanliga miniräknare. Svaret blir alltid ett decimaltal (som i Python kallas för *float*), även om det går jämnt ut.

```python
print(10 / 2) # Svaret blir 5.0
print(7 / 4)  # Svaret blir 1.75
```

#### Heltalsdivision: `//`
Ibland vill vi inte ha några decimaler. Heltalsdivision kallas ofta för "så många hela gånger det går". Python klipper helt enkelt av decimalerna och avrundar **alltid nedåt** till närmaste heltal.

```python
print(10 // 2) # Svaret blir 5 (eftersom 2 går exakt 5 gånger i 10)
print(7 // 4)  # Svaret blir 1 (eftersom 4 får plats 1 hel gång i 7)
print(9 // 2)  # Svaret blir 4 (eftersom 2 får plats 4 hela gånger i 9)
```

Heltalsdivision `//` är användbart när du till exempel vill räkna ut hur många hela veckor det går på 25 dagar (`25 // 7 = 3` hela veckor), eller hur många hela chokladkakor du kan köpa för en viss summa pengar. Det är också användbart när du vill göra omvandlingar mellan sekunder, minuter och timmar eller månader och år.

### Sammanfattning för minnet

* `print("text")` har citattecken för text, `print(5 + 5)` har inte citattecken för matte.
* Multiplikation skrivs med en stjärna: `*`.
* Vanlig division `/` ger ett svar med decimaler (t.ex. 4.5).
* Heltalsdivision `//` kastar bort decimalerna och ger bara det hela talet (t.ex. 4).