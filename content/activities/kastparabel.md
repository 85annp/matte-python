När vi jobbar med matematiska funktioner i Python blir vanliga listor snabbt klumpiga. Om vi vill beräkna $y$-värden för 1 000 olika $x$-värden måste vi vanligtvis skriva en loop som räknar ut ett värde i taget.

Med biblioteket NumPy slipper vi det. NumPy låter oss göra matematiska operationer på hela listor (arrays) samtidigt. Kombinerar vi detta med biblioteket Matplotlib (PyPlot) kan vi dessutom rita upp resultatet som en snygg graf med bara några få rader kod.

I den här aktiviteten ska vi analysera en boll som kastas rakt upp i luften. Höjden $h$ (i meter) efter $t$ sekunder beskrivs av den kända fysikaliska andragradsfunktionen:

$$h(t) = v_0 \cdot t - \frac{g \cdot t^2}{2}$$

* $v_0$ = utgångshastigheten (hur hårt vi kastar bollen i m/s)
* $g$ = tyngdaccelerationen (gravitationen som drar bollen nedåt)

Genom att använda `np.linspace(start, stopp, antal)` skapar vi en array med massor av tidssteg mellan 0 och den sluttid vi väljer. NumPy beräknar hela formeln på en gång, och PyPlot ritar upp det. 