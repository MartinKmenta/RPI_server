from table_control.table_control import LedsEffectsControl, RelaysControl, Rgb

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
    if "leds_color" in value:
        ledsEffectsControl.StartEffect("OneColor", 
            {"color":Rgb().FromHex(value["leds_color"])}
        )

    if "r" in value and "g" in value and "b" in value:
        ledsEffectsControl.StartEffect("OneColor", 
            {"color":Rgb(r=value["r"], g=value["g"], b=value["b"])}
        )



def relays_controller(value):
    logging.debug(value)
    if "relays" in value:
        relaysControl.SetAll(int(value["relays"], 2))

# todo ajak to refresh sites

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