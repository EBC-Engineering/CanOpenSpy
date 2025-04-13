import can
import time
from prettytable import PrettyTable

# PGN-definities met veldnamen, typen, bewerkingen en eenheden
pgn_definitions = {
    126992: [
        {"name": "Sequence Di",                 "type": "byte",     "signed": True,     "operation": lambda x: x,       "unit": "Number"},
        {"name": "Time source / reserved",  "type": "byte",     "signed": True,     "operation": lambda x: x,       "unit": "bits"},
        {"name": "Generic date",            "type": "word",     "signed": False,    "operation": lambda x: x,       "unit": "days"},
        {"name": "Generic time of day",     "type": "double",   "signed": False,    "operation": lambda x: x * 1e-4, "unit": "TOD"}
    ],
    126993: [
        {"name": "Update rate",                 "type": "word",     "signed": False, "operation": lambda x: x * 1e-3,  "unit": "sec"},
        {"name": "HartBeat Sequence Counter",   "type": "byte",     "signed": False, "operation": lambda x: x,  "unit": "Number"},
        {"name": "Class 1,2,equip state",       "type": "byte",     "signed": False, "operation": lambda x: x,  "unit": "bits"},
        {"name": "NMEA Reserved",               "type": "double",   "signed": False, "operation": lambda x: x,  "unit": ""},
    ],
    127250: [
        {"name": "Heading",     "type": "word", "signed": False,    "operation": lambda x: x * 0.01, "unit": "degrees"},
        {"name": "Pitch",       "type": "word", "signed": True,     "operation": lambda x: x * 0.01, "unit": "degrees"},
        {"name": "Roll",        "type": "word", "signed": True,     "operation": lambda x: x * 0.01, "unit": "degrees"},
        {"name": "Speed",       "type": "byte", "signed": False,    "operation": lambda x: x,        "unit": "m/s"}
    ],
    127488: [
        {"name": "Engine Instance",         "type": "byte", "signed": False, "operation": lambda x: x,      "unit": "Nummer"},
        {"name": "Engine Speed",            "type": "word", "signed": False, "operation": lambda x: x * 0.25,   "unit": "RPM"},
        {"name": "Engine Boost Pressure",   "type": "word", "signed": False, "operation": lambda x: x * 100,    "unit": "pa"},
        {"name": "Engine tilt/trim",        "type": "byte", "signed": False, "operation": lambda x: x,           "unit": "degrees"},
	    {"name": "NMEA Reserved bits",      "type": "word", "signed": False, "operation": lambda x: x,           "unit": "status"},
        ],
    127489: [
        {"name": "Engine Instance",         "type": "byte",  "signed": False, "operation": lambda x: x,          "unit": "Nummer"},
        {"name": "Engine oil pressure",     "type": "word",  "signed": False, "operation": lambda x: x * 100,    "unit": "pa"},
        {"name": "Engine oil temp",         "type": "word",  "signed": False, "operation": lambda x: x * 0.1,    "unit": "Kelvin"},
        {"name": "Engine temp",             "type": "word",  "signed": False, "operation": lambda x: x * 0.1,    "unit": "Kelvin"},
	    {"name": "Alternator potential",    "type": "word",  "signed": False, "operation": lambda x: x * 0.01,   "unit": "Volt"},
        {"name": "Fuel rate",               "type": "word",  "signed": False, "operation": lambda x: x * 0.0001, "unit": "cu-m/hr"},
        {"name": "Total engine hours",      "type": "double","signed": False, "operation": lambda x: x,          "unit": "Sec"},
        {"name": "Engine coolant pressure", "type": "word",  "signed": False, "operation": lambda x: x * 100,    "unit": "pa"},
        {"name": "Fuel Pressure",           "type": "word",  "signed": False, "operation": lambda x: x * 100,    "unit": "pa"},
	    {"name": "Not Available",           "type": "byte",  "signed": False, "operation": lambda x: x,          "unit": "bit"},
        {"name": "Engine Discrete Status 1","type": "word",  "signed": False, "operation": lambda x: x,          "unit": "Hex"},
        {"name": "Engine Discrete Status 2","type": "word",  "signed": False, "operation": lambda x: x,          "unit": "Hex"},
        {"name": "Percent Engine Load",     "type": "byte",  "signed": False, "operation": lambda x: x,          "unit": "%"},
	    {"name": "Percent Engine Torque",   "type": "byte",  "signed": False, "operation": lambda x: x,          "unit": "%"},
        ],
    127490: [
        {"name": "Inverter/Motor Id",       "type": "byte", "signed": False, "operation": lambda x: x,          "unit": "Nummer"},
        {"name": "Op.Mode + NMEA Res.",     "type": "byte", "signed": False, "operation": lambda x: x,          "unit": "bit"},
        {"name": "Motor Temperature",       "type": "word", "signed": False, "operation": lambda x: x * 0.01,   "unit": "Kelvin"},
	    {"name": "Inverter Temperature",    "type": "word", "signed": False, "operation": lambda x: x * 0.01,   "unit": "Kelvin"},
        {"name": "Coolant Temperature",     "type": "word", "signed": False, "operation": lambda x: x * 0.01,   "unit": "Kelvin"},
        {"name": "Gear Temperature",        "type": "word", "signed": False, "operation": lambda x: x * 0.01,   "unit": "Kelvin"},
        {"name": "Shaft Torque",            "type": "byte", "signed": False, "operation": lambda x: x,          "unit": "%"},
        ],
    127491: [
        {"name": "Energy Storage Id.r",     "type": "byte", "signed": False, "operation": lambda x: x * 1,      "unit": "Nummer"},
        {"name": "State of Charge",         "type": "byte", "signed": False, "operation": lambda x: x * 0.5,    "unit": "%"},
        {"name": "Time Remaining",          "type": "word", "signed": False, "operation": lambda x: x * 1,      "unit": "min."},
        {"name": "Highest Cell Temp.",      "type": "word", "signed": False, "operation": lambda x: x * 0.01,   "unit": "Kelvin"},
	    {"name": "Lowest Cell Temp.",       "type": "word", "signed": False, "operation": lambda x: x * 0.01,   "unit": "Kelvin"},
        {"name": "Average Cell Temp.",      "type": "word", "signed": False, "operation": lambda x: x * 0.01,   "unit": "Kelvin"},
        {"name": "Max. Discharge Current",  "type": "word", "signed": False, "operation": lambda x: x * 0.1,    "unit": "Amp"},
        {"name": "Max. Charge Current",     "type": "word", "signed": False, "operation": lambda x: x * 0.1,    "unit": "Amp"},
        {"name": "Cool & Heat Syst.Status", "type": "byte", "signed": False, "operation": lambda x: x,          "unit": "bit"},
        ],
    127494: [
        {"name": "Inverter/Motor identifier",           "type": "byte",  "signed": False, "operation": lambda x: x,         "unit": "Number"},
        {"name": "Motor Type + reserved",               "type": "byte",  "signed": False, "operation": lambda x: x,         "unit": "bit"},
        {"name": "Motor Voltage Rating",                "type": "word",  "signed": False, "operation": lambda x: x * 0.1,   "unit": "Volt"},
	    {"name": "Max. Cont. Motor Power",              "type": "word",  "signed": False, "operation": lambda x: x * 0.01,  "unit": "Kw"},
        {"name": "Max. Boost Motor Power",              "type": "word",  "signed": False, "operation": lambda x: x * 0.01,  "unit": "Kw"},
        {"name": "Max. Motor Temp. Rating",             "type": "word",  "signed": False, "operation": lambda x: x * 0.01,  "unit": "Kelvin"},
        {"name": "Rated Motor Speed",                   "type": "word",  "signed": False, "operation": lambda x: x * 0.25,  "unit": "RPM"},
        {"name": "Max.Controller Temp. Rating",         "type": "word",  "signed": False, "operation": lambda x: x * 0.01,  "unit": "Kelvin"},
	    {"name": "Motor Shaft Torque Rating",           "type": "word",  "signed": False, "operation": lambda x: x * 0.1,   "unit": "Nm"},
        {"name": "Motor DC-Voltage Derating Thresh.",   "type": "word",  "signed": False, "operation": lambda x: x * 0.1,   "unit": "Volt"},
        {"name": "Motor DC-Voltage Cut Off Thresh.",    "type": "word",  "signed": False, "operation": lambda x: x * 0.1,   "unit": "Volt"},
        {"name": "Drive/Motor Hours",                   "type": "double","signed": False, "operation": lambda x: x,         "unit": "sec"},
        ],
    127495: [
        {"name": "Energy Storage Id.",                  "type": "byte", "signed": False, "operation": lambda x: x,      "unit": "bit"},
        {"name": "Energy Sto.Mode + NEMA + Chemistry",  "type": "word", "signed": False, "operation": lambda x: x,      "unit": "bit"},
	    {"name": "Maximum Temperature Derating",        "type": "word", "signed": False, "operation": lambda x: x * 0.01,   "unit": "Kelvin"},
        {"name": "Maximum Temperature Shut Off",        "type": "word", "signed": False, "operation": lambda x: x * 0.01,   "unit": "Kelvin"},
        {"name": "Minimum Temperature Derating",        "type": "word", "signed": False, "operation": lambda x: x * 0.01,   "unit": "Kelvin"},
        {"name": "Minimum Temperature Shut Off",        "type": "word", "signed": False, "operation": lambda x: x * 0.01,   "unit": "Kelvin"},
        {"name": "Usable Battery Energy",               "type": "word", "signed": False, "operation": lambda x: x * 0.1,    "unit": "KwH"},
	    {"name": "State of Health",                     "type": "byte", "signed": False, "operation": lambda x: x * 0.5,    "unit": "%"},
        {"name": "Battery Cycle Counter",               "type": "word", "signed": False, "operation": lambda x: x,       "unit": "Cycles"},
        {"name": "Batt Full,Empty Status + NMEA Res.",  "type": "byte", "signed": False, "operation": lambda x: x,       "unit": "bit"},
        {"name": "Maximum Charge (SOC)",                "type": "byte", "signed": False, "operation": lambda x: x * 0.5,    "unit": "%"},
	    {"name": "Minimum Discharge (SOC)",             "type": "byte", "signed": False, "operation": lambda x: x * 0.5,    "unit": "%"},
        ],
    127506: [
        {"name": "Sequence ID",     "type": "byte", "signed": False, "operation": lambda x: x * 1,      "unit": "bit"},
        {"name": "DC Instance",     "type": "byte", "signed": False, "operation": lambda x: x * 1,      "unit": "bit"},
        {"name": "DC Type",         "type": "byte", "signed": False, "operation": lambda x: x * 1,      "unit": "Number"},
        {"name": "State of Charge", "type": "byte", "signed": False, "operation": lambda x: x * 1,      "unit": "%"},
	    {"name": "State of Health", "type": "word", "signed": False, "operation": lambda x: x * 1,      "unit": "%"},
        {"name": "Time Remaining",  "type": "word", "signed": False,"operation": lambda x: x * 0.01,   "unit": "Kelvin"},
        {"name": "Ripple Voltage",  "type": "word", "signed": False,"operation": lambda x: x * 1,      "unit": "mV"},
        {"name": "Amp Hours",       "type": "word", "signed": False,"operation": lambda x: x * 3600,   "unit": "Coulombs"},
        ],
    127508: [
        {"name": "Battery Instance",    "type": "byte", "signed": False, "operation": lambda x: x * 1,      "unit": "Number"},
        {"name": "Battery Voltage",     "type": "word", "signed": True,  "operation": lambda x: x * 0.01,   "unit": "Volt"},
        {"name": "Battery Current",     "type": "word", "signed": True,  "operation": lambda x: x * 0.1,    "unit": "Amp"},
        {"name": "Battery Case Temp.",  "type": "word", "signed": False, "operation": lambda x: x * 0.01,   "unit": "Kelvin"},
	    {"name": "Sequence ID",         "type": "byte", "signed": False, "operation": lambda x: x * 1,      "unit": ""},
        ],
    127513: [
        {"name": "Battery Instance",                    "type": "byte", "signed": False, "operation": lambda x: x * 1,      "unit": "Number"},
        {"name": "Batt.Type Equalisation + NMEA res.",  "type": "byte", "signed": False, "operation": lambda x: x * 1,      "unit": "bit"},
	    {"name": "Nom Voltage + Batt Chemistry",        "type": "byte", "signed": False, "operation": lambda x: x * 0.01,   "unit": "bit"},
        {"name": "Battery Capacity",                    "type": "word", "signed": False, "operation": lambda x: x * 3600,   "unit": "Coulombs"},
	    {"name": "Battery Temp. Coeff.t",               "type": "byte", "signed": True,  "operation": lambda x: x * 1,      "unit": "%"},
        {"name": "Peukert Exponent",                    "type": "byte", "signed": False, "operation": lambda x: x * 0.002,  "unit": ""},
        {"name": "Charge Eff. Factor",                  "type": "byte", "signed": True,  "operation": lambda x: x * 1,      "unit": "%"},
        ],
    128002: [
        {"name": "Inverter/Motor Controller",   "type": "byte", "signed": False, "operation": lambda x: x * 1,         "unit": "Number"},
        {"name": "Active mode + BrakeMode",     "type": "byte", "signed": False, "operation": lambda x: x * 1,         "unit": "bits"},
	    {"name": "Rotational Shaft Speed",      "type": "word", "signed": False,  "operation": lambda x: x * 0.25,     "unit": "RPM"},
        {"name": "Motor DC Voltage",            "type": "word", "signed": False, "operation": lambda x: x * 0.1,       "unit": "Volt"},
        {"name": "Motor DC Current",            "type": "word", "signed": True,  "operation": lambda x: x * 0.1,       "unit": "Amp"},
        ],
    128003: [
        {"name": "Energy Storage Identifier",       "type": "byte", "signed": False, "operation": lambda x: x,          "unit": "Number"},
        {"name": "Battery/Isolation/Error Status",  "type": "byte", "signed": False, "operation": lambda x: x,          "unit": "bits"},
        {"name": "Battery Voltage",                 "type": "word", "signed": False, "operation": lambda x: x * 0.1,    "unit": "Volt"},
        {"name": "Battery Current",                 "type": "word", "signed": True,  "operation": lambda x: x * 0.1,    "unit": "Amp"},
        {"name": "NMEA Reserved",                   "type": "word", "signed": False, "operation": lambda x: x,          "unit": "bits"},
        ],
    65280: [
        {"name": "Manufacurer code",    "type": "word",     "signed": False,  "operation": lambda x: x,          "unit": "Number"},
        {"name": "Heave",               "type": "double",   "signed": False,    "operation": lambda x: x,          "unit": "Number"},
        {"name": "Reserved",            "type": "word",     "signed": False,    "operation": lambda x: x,        "unit": "Number"}
        ]
}
# Opslag voor actuele PGN-data
pgn_data = {}

def extract_pgn(arbitration_id):
    """
    Extraheer de PGN van het CAN arbitration ID.
    """
    return (arbitration_id >> 8) & 0x01FFFF  # PGN bevindt zich in bits 8-25

def process_pgn_data(pgn, data):
    """
    Verwerk data van een specifieke PGN volgens de definities.
    """
    if pgn in pgn_definitions:
        # print(F"Received PGN: {pgn}")
        decoded_data = {}
        offset = 0  # Houd de byte-offset bij voor parsing
        for field in pgn_definitions[pgn]:
            field_size = {"byte": 1, "word": 2, "double": 4}[field["type"]]
            raw_value = int.from_bytes(data[offset:offset+field_size], byteorder='little', signed=field["signed"])
            
            # Speciale verwerking voor velden met eenheid "bit"
            if field["unit"].lower() == "bit":
                # Zet waarde om naar binaire vorm, afhankelijk van het aantal bytes
                value = format(raw_value, f'0{field_size * 8}b')
            else:
                # Normale verwerking, waarbij gesigneerde waarden correct worden gedecodeerd
                value = round(field["operation"](raw_value), 3)
            
            decoded_data[field["name"]] = {"value": value, "unit": field["unit"]}
            offset += field_size
        return decoded_data
    return {"Onbekend": {"value": "Geen definitie beschikbaar", "unit": ""}}

def display_pgn_data():
    """
    Toon de actuele PGN-data in tabelvorm, per PGN.
    """
    for pgn, fields in pgn_data.items():
        print(f"\nPGN {pgn}:")
        table = PrettyTable()
        table.field_names = ["Naam van waarde", "Waarde", "Eenheid"]
        table.align["Naam van waarde"] = "l"  # Links uitlijnen
        table.align["Waarde"] = "r"           # Rechts uitlijnen
        table.align["Eenheid"] = "l"         # Links uitlijnen
        for field_name, field_data in fields.items():
            table.add_row([field_name, field_data["value"], field_data["unit"]])
        print(table)

def main():
    channel = 'COM5'  # De USB-CAN poort is aangesloten op COM10
    bitrate = 250000   # Baudrate voor de CAN-bus (250 Kbps)

    # Initialiseer de CAN-bus
    try:
        print(f"Initialiseer CAN-bus op kanaal {channel} met {bitrate} bps...")
        bus = can.interface.Bus(interface='slcan', channel=channel, bitrate=bitrate)
        print("CAN-bus succesvol geïnitialiseerd!")
    except Exception as e:
        print(f"Fout bij initialisatie: {e}")
        return

    global pgn_data

    # Lees en decodeer CAN-berichten
    try:
        start_time = time.time()
        message = bus.recv(1)  # Sync
        while True:
            message = bus.recv(1)  # Wacht maximaal 1 seconde op een bericht
            if message:
                pgn = extract_pgn(message.arbitration_id)
                decoded_fields = process_pgn_data(pgn, message.data)
                pgn_data[pgn] = decoded_fields  # Sla de meest recente gegevens op

            # Toon de gegevens elke 2 seconden
            if time.time() - start_time >= 1:
                display_pgn_data()
                start_time = time.time()  # Reset de timer
    except KeyboardInterrupt:
        print("Programma gestopt door gebruiker.")
    except Exception as e:
        print(f"Fout tijdens uitlezen: {e}")

if __name__ == "__main__":
    main()
