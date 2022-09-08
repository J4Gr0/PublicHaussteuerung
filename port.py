from portExpander import MCP23S17

from gpiozero import LED, Button
from signal import pause

mcp1 = MCP23S17(device_id = 0)
mcp2 = MCP23S17(device_id = 4)

mcp1.open()
mcp2.open()

aktivLed = LED(pin=17)
pumpeLed = LED(pin=27)
rolloLed = LED(pin=22)
pumpeOut = LED (pin=23)
ventiOut = LED(pin=13)
radioOut = LED(pin=19)
relais = LED(pin=18)


upButton = Button(pin=12)
downButton = Button(pin=16)
pumpButton = Button(pin=20)
fanButton = Button(pin=21)
magnetTerasse = Button(pin=24)
magnetAndere = Button(pin=25)

magnetAndere.when_pressed = aktivLed.on
magnetAndere.when_released= aktivLed.off

pause()

# for x in range(0, 16):
#    mcp1.setDirection(x, mcp1.DIR_OUTPUT)
#    mcp2.setDirection(x, mcp1.DIR_OUTPUT)




# while (True):

#     mcp2.digitalWrite(8, MCP23S17.LEVEL_HIGH)

    

#     aktivLed.on()
#     pumpeLed.on()
#     rolloLed.on()
#     pumpeOut.on()
#     ventiOut.on()
#     radioOut.on()
#     relais.on()
#     time.sleep(1)


#     for x in range(0, 16):
#         mcp1.digitalWrite(x, MCP23S17.LEVEL_LOW)
#         mcp2.digitalWrite(x, MCP23S17.LEVEL_LOW)
#     aktivLed.off()
#     pumpeLed.off()
#     rolloLed.off()
#     pumpeOut.off()
#     ventiOut.off()
#     radioOut.off()
#     relais.off()
#     time.sleep(1)



mcp1.digitalWrite(8, MCP23S17.LEVEL_HIGH)
mcp2.digitalWrite(7, MCP23S17.LEVEL_HIGH)