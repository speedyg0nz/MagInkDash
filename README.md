
# MagInkDash
This repo contains the code needed to drive an E-Ink Magic Dashboard that uses a Raspberry Pi to automatically retrieve updated content from Google Calendar, OpenWeatherMap and OpenAI ChatGPT, format them into the desired layout, before serving it to a battery powered E-Ink display (Inkplate 10). Note that the code has only been tested on the specific hardware mentioned, but can be easily modified to work with other hardware (for both the server or display).

![20230412_001704](https://user-images.githubusercontent.com/5581989/231361096-82e7ccba-c7db-4900-a48c-49fd5e4e9161.JPG)

## Background
Back in September 2021, I [shared about my E-Ink Calendar project (MagInkCal) on Reddit](https://www.reddit.com/r/raspberry_pi/comments/pugv7d/maginkcal_magic_calendar_project_completed_full/) (with [full source code on Github](https://github.com/speedyg0nz/MagInkCal/)), which was an attempt to replicate the [Android Magic Calendar concept](https://www.youtube.com/watch?v=2KDkFgOHZ5I) that inspired many DIY projects over the years. While the calendar has been serving me extremely well, I wanted a dashboard which offered additonal information that was rich, timely and glanceable, such as the weather for the next hour just before leaving the house. While there were many projects that might achieve a similar outcome, I wanted something that met my specific needs. Hence, this project was born. You can read more about the story and join the conversation over on Reddit.

## Hardware Required
- [Raspberry Pi](https://www.raspberrypi.org/) - Used as a server to retrieve content and generate a dashboard for the E-Ink display so any model would do. Personally, I dug out an old Raspberry Pi Model B Revision 2.0 from 2011 and it works fine for this purpose. In fact, it doesn't even need to be a RPi. Any other Single Board Computer, or old computer, or even a cloud service that runs the code would suffice.
- [Inkplate 10 Battery Powered E-Ink Display](https://soldered.com/product/soldered-inkplate-10-9-7-e-paper-board-with-enclosure-copy/) - Used as a client to display the generated dashboard. I went with this because it was an all-in-one with the enclosure and battery included so there's less hardware tinkering. But you could certainly go barebones and assemble the different parts yourself from scratch, i.e. display, microcontroller, case, and battery.


## How It Works
A cron job on RPi will trigger a Python script to run every hour to fetch calendar events from Google Calendar, weather forecast from OpenWeatherMap and random factoids from OpenAI's ChatGPT. The retrieved content is then formatted into the desired layout and saved as an image. An Apache server on the RPi will then host this image such that it can be accessed by the Inkplate 10. On the Inkplate 10, the corresponding script   will then connect to the RPi server on the local network via a WiFi connection, retrieve the image and display it on the E-Ink screen. The Inkplate 10 then goes to sleep to conserve battery. The dashboard remains displayed on the E-Ink screen, because well, E-Ink...

Some features of the dashboard: 
- **Battery Life**: As with similar battery powered devices, the biggest question is the battery life. I'm currently using a 1500mAh battery on the Inkplate 10 and based on current usage, it should last me around 3-4 months. With the 3000mAh that comes with the manufacturer assembled Inkplate 10, we could potentially be looking at 6-8 month battery life. With this crazy battery life, there are much more options available. Perhaps solar power for unlimited battery life? Or reducing the refresh interval to 15 or 30min to increase the information timeliness?
- **Calendar and Weather**: I'm currently displaying calendar events and weather forecast for current day and the upcoming two days. No real reason other than the desire to know what my weekend looks like on a Friday, and therefore helping me to better plan my weekend. Unfortunately, if you have a busy calendar with numerous events on a single day, the space on the dashboard will be consumed very quickly. If so, you might wish to modify the code to reduce/limit the number of days/events to be displayed.
- **OpenAI ChatGPT**: As with any new projects in 2023, we can't avoid bringing in ChatGPT. So I've also included a section in the dashboard to retrieve ChatGPT responses via OpenAI's API (free for now, paid in the future).  So far I'm using it to retrieve factoids on animals, historical figures, notable events, countries, world records, etc. It's a huge hit with the kids at home, and they'll be standing next to the dashboard on the hour to wait for the next refresh. The prompts fed to ChatGPT can certainly be customised, so please knock yourself out and think of the most outrageous things you can put on your dashboard. Note that you might have to test and adjust the prompts/parameters, else ChatGPT might return fairly repetitive responses, e.g. on Abraham Lincoln, Rosa Parks, Martin Luther King.
- **Telegram Bot**: Although the battery life is crazy long on the Inkplate 10, I still wish to be notified when the battery runs low. To do so, I set up a Telegram Bot and the Inkplate will trigger the bot to send me a message if the measured battery voltage falls below a specified threshold. That said, with the bot set up, there's actually much more you could do, e.g. send yourself a message when it's to expected to rain in the next hour.

![MagInkCal Basics](https://user-images.githubusercontent.com/5581989/231362411-207dc7e2-c27c-43aa-b030-72db6efaa7f5.png)

## Setting Up 

1. Start by flashing [Raspberrypi OS Lite](https://www.raspberrypi.org/software/operating-systems/) to a SD/MicroSD Card. If you're using a Raspberry Pi with 32bit CPU, there are [known issues](https://forums.raspberrypi.com/viewtopic.php?t=323478) between the latest RPiOS "bullseye" release and chromium-browser, which is required to run this code. As such, I would recommend that you keep to the legacy "buster" OS if you're still running this on older RPi hardware.

2. After setting up the OS, run the following commmand in the RPi Terminal, and use the [raspi-config](https://www.raspberrypi.org/documentation/computers/configuration.html) interface to setup Wifi connection, and set the timezone to your location. You can skip this if the image is already preconfigured using the Raspberry Pi Imager.

```bash
sudo raspi-config
```
3. Run the following commands in the RPi Terminal to setup the environment to run the Python scripts and function as a web server. It'll take some time so be patient here.

```bash
sudo apt update
sudo apt-get install python3-pip
sudo apt-get install chromium-chromedriver
sudo apt-get install libopenjp2-7-dev
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip3 install pytz
pip3 install selenium
pip3 install Pillow
pip3 install openai  
sudo apt-get install apache2 -y  
sudo chown pi:www-data /var/www/html
sudo chmod 755 /var/www/html
```
4. Download the over the files in this repo to a folder in your PC first. 

5. In order for you to access your Google Calendar events, it's necessary to first grant the access. Follow the [instructions here](https://developers.google.com/calendar/api/quickstart/python) on your PC to get the credentials.json file from your Google API. Don't worry, take your time. I'll be waiting here.

6. Once done, copy the credentials.json file to the "gcal" folder in this project. Navigate to the "gcal" folder and run the following command on your PC. A web browser should appear, asking you to grant access to your calendar. Once done, you should see a "token.pickle" file in your "gcal" folder.

```bash
python3 quickstart.py
```

7. Copy all the files (other than the "inkplate" folder) over to your RPi using your preferred means. 

8. Run the following command in the RPi Terminal to open crontab.
```bash
crontab -e
```
9. Specifically, add the following command to crontab so that the MagInkDash Python script runs on the hour, every hour.
```bash
0 * * * * cd /location/to/your/MagInkDash && python3 main.py
```
10. As for the Inkplate, I'm not going to devote too much space here since there are [official resources that describe how to set it up](https://inkplate.readthedocs.io/en/latest/get-started.html). It may take some trial and error for those new to microcontroller programming but it's all worth it! Only the Arduino portion of the guide is relevant, and you'll need to be able to run *.ino scripts via Arduino IDE before proceeding. From there, run the "inkplate.ino" file from the "inkplate" folder from the Arduino IDE when connected to the Inkplate.

12. That's all! Your Magic Dashboard should now be refreshed every hour! 

PS: I'm aware that the instructions above may not be complete, so feel free to ping me if you noticed anything missing and I'll add it to the steps above.

## Acknowledgements
- [Lexend Font](https://fonts.google.com/specimen/Lexend) and [Tilt Warp Font](https://fonts.google.com/specimen/Tilt+Warp): Fonts used for the dashboard display
- [Bootstrap](https://getbootstrap.com/): Styling toolkit to customise the look of the dashboard
- [Weather Icons](https://erikflowers.github.io/weather-icons/): Icons used for displaying of weather forecast information
- [Freepik](https://www.freepik.com/): For the background image used in this dashboard
  
## Contributing
I won't be updating this code much, since it serves my needs well. Nevertheless, feel free to fork the repo and modify it for your own purpose. At the same time, check out other similar projects, such as [InkyCal](https://github.com/aceisace/Inkycal) by [/u/aceisace](https://www.reddit.com/user/aceisace/). It's much more polished and also actively developed.

## Buy Me A Coffee
If this project has helped you in any way, do buy me a coffee so I can continue to build more of such projects in the future and share them with the community!

<a href="https://www.buymeacoffee.com/speedygonz" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>


## What's Next
Since building the Magic Calendar two years back, I've been looking at E-Ink tablets that emulate the experience of writing on paper, and allow the users to take notes on the go. Those familiar with this range of products would be aware of the Kindle Scribe, reMarkable tablet, Ratta Supernote, Kobo Elipsa and many others. I've had some limited success with getting a Kindle Paperwhite to display a calendar while sleeping but it felt too "hacky" and prone to breaking when Amazon updates the OS. I'm still looking for the right device (possibly a PineNote?), so if you're aware of any suitable candidates, do let me know!
