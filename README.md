# BeleggenTool

## Installatie voor Vince
Voor het gebruiken van de tool is de applicatie “Github desktop” nodig. Via Github kan Mila makkelijk updates maken aan de tool, en kan jij ook makkelijk deze updates installeren. 

Wanneer Github desktop geïnstalleerd is, moet er worden ingelogd via een Github account. Deze zijn gratis aan te maken via github, en het account dient toegevoegd te worden aan de projectomgeving van de tool zodat het account gebruik kan maken van de tool. Neem hiervoor contact op met Mila om een account toe te voegen.

Zodra er is ingelogd op een account, kan de applicatie worden geinstalleerd. Klik links bovenin het venster op “Current repository”, daarna op de knop “Add” en “Clone repository”

Kies dan de “Milakaasplank/BeleggenTool” repository, en kies bij je “Local path” de plek waar je het project wilt opslaan. Klik hierna op “Clone” om het project te downloaden.

Open de folder waar het project is opgeslagen, en navigeer vervolgens naar de “tool_opstarten” applicatie die te vinden is in “build>exe.win-amd64-3.11”. Dubbelklik op deze applicatie om de applicatie te starten. Dit opent een command line prompt, en vanuit de command line wordt de applicatie opgestart, dit kan eventjes duren. 

TIP: Maak een snelkoppeling aan op je bureaublad voor de “tool_opstarten” applicatie!

## Setup van het lokale dashboard runnen
1. Maak een virtual environment aan: python -m venv .venv
2. Activeer de venv: .venv\Scripts\activate
3. Installeer de requirements.txt: pip install -r requirements.txt
4. Run de volgende command in de terminal: streamlit run app.py
5. Het dashboard wordt nu lokaal gelaunched!

## Build the executable
1. Als de bovenstaande stappen werken, type het volgende in je terminal: cxfreeze --script launch_app.py
2. Kopieer de app.py en launch.app.py in de build\exe.win folder
3. Klik op launch_app.exe in build\exe.win



Note: Als je een andere .py file aanmaakt moet je die ook meekopieren in het build\exe.win folder (gok ik)