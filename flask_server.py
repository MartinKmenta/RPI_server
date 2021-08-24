from table_control.relays_controller import RelaysControl
from table_control.led_effects import LedsEffectsControl, Rgb

from flask import Flask, request, render_template
app = Flask(__name__)

import logging

logging.basicConfig(
    level=logging.DEBUG
    # level=logging.WARNING
    # level=logging.ERROR
)

relaysControl = RelaysControl()
ledsEffectsControl = LedsEffectsControl()

def led_controller(value):
    print(value)
    if "leds_color" in value:
        ledsEffectsControl.StartEffect("OneColor", 
            {"color":Rgb.FromHex(value["leds_color"])}
        )

    if "r" in value and "g" in value and "b" in value:
        print(value)
        print(Rgb.from_dict(dict(value)))
        ledsEffectsControl.StartEffect("OneColor", 
            {"color":Rgb.from_dict(dict(value))}
        )



def relays_controller(value):
    logging.debug(value)
    if "relays" in value:
        relaysControl.SetFromValue(int(value["relays"], 2))

# todo ajax to refresh sites

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/leds',methods=['GET', 'POST'])
def leds():
    if request.method == 'POST':
        led_controller(request.form)
    
    return render_template('leds.html')


@app.route('/ledsStatus.json')
def ledsStatus():
    logging.error("ledsStatus.json")
    logging.debug(f"ledsStatus.json => {ledsEffectsControl.GetStatus()}")
    return ledsEffectsControl.GetStatus()


@app.route('/relays',methods=['GET', 'POST'])
def relays():
    if request.method == 'POST':
        relays_controller(request.form)
    
    return render_template('relays.html', avaiableRelays=relaysControl.avaiableRelays)


@app.route('/relaysStatus.json')
def relaysStatus():
    logging.error("relaysStatus.json")
    return relaysControl.GetStatus()


@app.route('/stat')
def stat():
    return "Nothing yet"

if __name__ == '__main__':
    app.run()