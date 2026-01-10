from sense_hat import SenseHat

sense = SenseHat()
sense.show_message(str(sense.get_temperature()))
sense.show_message(str(sense.get_pressure()))
sense.show_message(str(sense.get_humidity()))
