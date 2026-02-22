# RecordPlayer
Currently only for personal use, will update soon!


# RFID Record Player

A modern record player that repurposes a record player coaster as an interface for controlling Spotify playback via RFID and a Raspberry Pi, combining the physical experience of vinyl with digital playback.
Features RFID detection of tagged records for Spotify content, a stepper motor–driven spinning platter, and tone arm control to start and stop playback.

## Wiring
### RC522 RFID Reader (SPI)

| Pi Pin               | RC522 Pin |
|----------------------|-----------|
| Pin 24 (GPIO 8)      | SDA       |
| Pin 23 (GPIO 11)     | SCK       |
| Pin 19 (GPIO 10)     | MOSI      |
| Pin 21 (GPIO 9)      | MISO      |
| Pin 22 (GPIO 25)     | RST       |
| Pin 17 (3.3V)        | 3.3V      |
| Pin 25 (GND)         | GND       |

### A3144 Hall Effect Sensor

| Pi Pin           | A3144 Pin |
|------------------|-----------|
| Pin 11 (GPIO 17) | OUT       |
| Pin 1 (3.3V)     | VCC       |
| Pin 9 (GND)      | GND       |

## Installation

1. Run the installation script
    This sets up the Python virtual environment, installs python dependencies, and enables required interfaces.
    ```bash
    bash install/install.sh
    ```
    Once the installation finishes, you’ll be prompted to reboot your Raspberry Pi for the changes to take effect.
2. Run the setup script
    After rebooting, activate the virtual environment and run the setup script:
    ```bash
    source venv/bin/activate
    python3 install/setup.py
    ```
3. Set up Spotify Credentials
    - Visit [Spotify For Developers](https://developer.spotify.com/dashboard/applications) and Sign In
    - In the Developer Dashboard, click "Create an App"
        - Give your app a Name and Description
        - For the Redirect URIs, enter `http://127.0.0.1:8080`
        - Check `Web API` box
    - In the setup script, enter the `Client ID`, `Client Secret`, and `Redirect URI`
    - Visit the URL to authorize your app and paste the redirected URL back.
4. Write RFID tags
    - In the setup script, choose `Write RFID tags`
    - Scan an RFID tag
    - Paste a Spotify URI for a track, album, playlist, or artist
        - URIs follow the format `spotify:{track|album|artist|playlist}:...`
        - To copy a Spotify URI, use the desktop app, click the three dots on a song/album/artist, hover over "Share," then hold Alt (Windows) or Option (Mac) and select "Copy Spotify URI"
5. Start the Record Player
    Once the installation is complete, run the record player script to start playing music:
    ```bash
    source venv/bin/activate
    python3 record_player.py
    ```

Currently defaults to current playing device and backup is sonos speakers, can edit in record_player spotify play function if want to default sto speakers always later

make sure not having a device id or a blank one in env doesn't break anything
