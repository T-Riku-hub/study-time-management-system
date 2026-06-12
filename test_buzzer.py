from gpiozero import Buzzer 
from time import sleep

buzzer = Buzzer(21)
try:
	while True:
		buzzer.on()
		sleep(0.1)
		buzzer.off()
		sleep(0.1)
except KeyboardInterrupt:
	buzzer.close()
