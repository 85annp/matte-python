I matematiken pratar vi ofta om sannolikhet i teorin ‒ till exempel att chansen att få en sexa när vi slår en tärning är 1/6. Men för att testa om teorin stämmer i verkligheten behöver vi göra experiment. Att kasta en fysisk tärning 10 000 gånger tar väldigt lång tid. Som tur är kan vi låta datorn göra det på ett ögonblick med hjälp av slumptal.

För att använda slumpen i Python behöver vi först hämta en färdig modul som heter `random`. Det gör vi längst upp i koden med kommandot `import random`.

### Slumpa heltal
När du vill simulera händelser som handlar om siffror – som att kasta en tärning eller dra ett nummer i ett lotteri – använder du funktionen `random.randint(a, b)`. Den här funktionen väljer ett slumpmässigt heltal från och med `a` till och med `b`.

Viktigt att komma ihåg: Till skillnad från många andra funktioner i Python där slutnumret inte räknas med, så är `random.randint()` inklusiv. Det betyder att både det första och det sista numret kan väljas!

Exempel:
```python
import random

slumptal = random.randint(1, 6)
print(slumptal)
```

<img src="/illustrations/random_illustration.png" alt="Exempel på random" class="theory-image">

### Slumpa från en lista
Ibland handlar sannolikhet inte om siffror, utan om saker eller alternativ. Det kan vara att singla slant (krona/klave) eller att dra en färgad kula ur en påse. Då använder vi funktionen `random.choice(lista)`. Du ger funktionen en lista med alternativ, och Python "blundar och pekar" på ett av elementen i listan.

Exempel på att singla slant:
```python
import random

mynt = ['Krona', 'Klave']
resultat_mynt = random.choice(mynt)
print('Du singlade slant och det blev:', resultat_mynt)
```

<img src="/illustrations/randomchoice_illustration.png" alt="Exempel på random choice" class="theory-image">

Exempel på att dra en kula ur en påse:
```python
import random

# Påsen innehåller 3 röda, 1 blå och 1 grön kula
pase = ['Röd', 'Röd', 'Röd', 'Blå', 'Grön']
resultat_kula = random.choice(pase)
print('Du drog en kula och färgen blev:', resultat_kula)
```

### Sammanfattning för minnet

* `import random` måste alltid stå högst upp i ditt program.
* `random.randint(min, max)` används för heltal (t.ex. tärningar, lotterinummer). Både min- och max-värdet kan väljas.
* `random.choice(lista)` används för att välja ett slumpmässigt alternativ från en lista (t.ex. krona/klave, färger, namn).