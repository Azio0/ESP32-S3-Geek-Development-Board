#/---------------------------------
#/ A simple real-time clock display
#/---------------------------------
import libraries.lcd_driver
import network, ntptime, time # pyright: ignore[reportMissingImports]

ntptime.host = "uk.pool.ntp.org" # The time server to be used
utc_offset = 3600 # Used to adjust time from UTC by seconds, exaple for BST

lcd_driver = libraries.lcd_driver
lcd_driver.show_text("Loading", scale=3)

wlan = network.WLAN(network.STA_IF) # Use the on-board network card
wlan.active(True)
wlan.connect('ssid', 'password') # Your network's name (ssid) and password

while not wlan.isconnected():
    time.sleep(1)

else: # If connected
    lcd_driver.clear()
    ntptime.settime()

while True:
    current_time = time.localtime(time.time() + utc_offset)

    lcd_driver.show_text(f"{current_time[3]}:{current_time[4]}:{current_time[5]}", scale=3)
    time.sleep(1)
