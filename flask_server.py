from table_control.relays_controller import RelaysControl
from table_control.led_effects import LedsEffectsControl, Rgb

import logging
import time

from flask import Flask, request, render_template, jsonify
app = Flask(__name__)

relaysControl = RelaysControl()
ledsEffectsControl = LedsEffectsControl()


def now():
    return time.strftime("%a, %d %b %Y %H:%M:%S")

def log_to_file(msg):
    with open(".logs/log.log", "a") as log_file:
        log_file.write(now() + " => " + str(msg) + "\n")
        logging.debug(now() + " => " + str(msg) + "\n")


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

    # todo improve syntax
    
    if "Relays8bit" in value:
        relaysControl.SetFromValue(value["Relays8bit"])
    if "SetSome" in value:
        relaysControl.SetSome(value["SetSome"])

    if "TurnOnAll" in value:
        relaysControl.TurnOnAll()
    if "TurnOffAll" in value:
        relaysControl.TurnOffAll()
        
    if "TurnOnPcComponents" in value:
        relaysControl.TurnOnPcComponents()
    if "TurnOffPcComponents" in value:
        relaysControl.TurnOffPcComponents()

    if "StartPc" in value:
        relaysControl.StartPc()
    if "TurnOffPc" in value:
        relaysControl.TurnOffPc()

    if "TurnOnLeds" in value:
        relaysControl.TurnOnLeds()
    if "TurnOffLeds" in value:
        relaysControl.TurnOffLeds()



# todo ajax to refresh sites

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/leds',methods=['GET'])
def leds():
    return render_template('leds.html')


# @app.route('/ledsStatus.json')
# def ledsStatus():
#     logging.debug("ledsStatus.json")
#     logging.debug(f"ledsStatus.json => {ledsEffectsControl.GetStatus()}")
#     return ledsEffectsControl.GetStatus()


@app.route('/relays',methods=['GET'])
def relays():
    logging.debug("relays")
    return render_template('relays.html', relaysValue=relaysControl.relaysValue, )


@app.route('/setRelays',methods=['POST', 'GET'])
def setRelays():
    logging.debug("setRelays")
    relays_controller(request.get_json())
    return jsonify({'processed': 'true'})


@app.route('/relaysValue',methods=['POST', 'GET'])
def relaysValue():
    logging.debug("relaysValue")
    return jsonify(relaysControl.GetStatus())


def create_app():
    log_to_file("app created for server start") 
    return app


if __name__ == '__main__':

    log_to_file("server started using main")

    logging.basicConfig(
        # level=logging.DEBUG
        # level=logging.WARNING
        level=logging.ERROR
    )

    app.run()
