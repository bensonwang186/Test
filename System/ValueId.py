class ValueIdFinder:

    def getValueId(self, valueId):

        if valueId is "STATUS_UTILITY_VOLT":
            valueId = 0  # array of mV(three phase)
        elif valueId is "STATUS_OUTPUT_VOLT":
            valueId = 1  # array of mV(three phase)
        elif valueId is "STATUS_PERCENT_LOAD":
            valueId = 2  # array of m % (three phase)
        elif valueId is "STATUS_BATTERY_CAPACITY":
            valueId = 3  # m %
        elif valueId is "STATUS_BATTERY_VOLT":
            valueId = 4  # mVDC
        elif valueId is "STATUS_TEMPERATURE":
            valueId = 5  # mC
        elif valueId is "STATUS_UTILITY_FREQ":
            valueId = 6  # array of mHz (three phase)
        elif valueId is "STATUS_OUTPUT_FREQ":
            valueId = 7  # array of mHz (three phase)
        elif valueId is "STATUS_REMAIN_RUNTIME":
            valueId = 8  # s (three phase used also)
        elif valueId is "STATUS_REMAIN_CHARGETIME":
            valueId = 9  # s
        elif valueId is "STATUS_OUTPUT_CURRENT":
            valueId = 10  # array of mA (three phase)
        elif valueId is "STATUS_UTILITY_FAILURE":
            valueId = 11  # 1/0
        elif valueId is "STATUS_BATTERY_CRITICAL":
            valueId = 12  # 1/0
        elif valueId is "STATUS_BATTERY_WARNING":
            valueId = 13  # 1": battery capacity less 80 %":valueId =   0": otherwise
        elif valueId is "STATUS_BUZZER_BEEPING":
            valueId = 14  # 1/0
        elif valueId is "STATUS_BATTERY_TESTING":
            valueId = 15  # 1/0
        elif valueId is "STATUS_SHUTDOWN_SCHEDULE_PENDING":
            valueId = 16  # 1/0
        elif valueId is "STATUS_RESTORE_SCHEDULE_PENDING":
            valueId = 17  # 1/0
        elif valueId is "STATUS_HARDWARE_FAULT":
            valueId = 18  # 1/0
        elif valueId is "STATUS_AVR_LEVEL":
            valueId = 19  # 0: normal =   1: boost =   2: boost more =   3: buck
        elif valueId is "STATUS_INV_OVERHEAT":
            valueId = 20  # 1/0
        elif valueId is "STATUS_INV_FAULT":
            valueId = 21  # 1/0
        elif valueId is "STATUS_INV_OFF":
            valueId = 22  # 1/0
        elif valueId is "STATUS_UTILITY_FREQ_FAILURE":
            valueId = 23  # 1/0
        elif valueId is "STATUS_UTILITY_VOLT_FAILURE":
            valueId = 24  # 1/0
        elif valueId is "STATUS_RESTORE_THRESHOLD_PENDING":
            valueId = 25  # 1/0
        elif valueId is "STATUS_CHARGING":
            valueId = 26  # 1/0
        elif valueId is "STATUS_DISCHARGING":
            valueId = 27  # 1/0
        elif valueId is "STATUS_BATTERY_REPLACE":
            valueId = 28  # 1/0
        elif valueId is "STATUS_BATTERY_NOT_PRESENT":
            valueId = 29  # 1/0
        elif valueId is "STATUS_BYPASS_OVERLOAD":
            valueId = 30  # 1/0
        elif valueId is "STATUS_BYPASS_ACTIVE":
            valueId = 31  # 1/0
        elif valueId is "STATUS_OUTPUT_SHORTED":
            valueId = 32  # 1/0
        elif valueId is "STATUS_OUTPUT_HAS_LOAD":
            valueId = 33  # 1/0
        elif valueId is "STATUS_OUTPUT_OVERLOAD":
            valueId = 34  # 1/0
        elif valueId is "STATUS_OUTPUT_FREQ_FAILURE":
            valueId = 35  # 1/0
        elif valueId is "STATUS_OUTPUT_VOLT_FAILURE":
            valueId = 36  # 1/0

        # properties

        elif valueId is "PROP_PROTOCOL_VERSION":
            valueId = 37  # string
        elif valueId is "PROP_APPARENT_POWER":
            valueId = 38  # VA
        elif valueId is "PROP_ACTIVE_POWER":
            valueId = 39  # W
        elif valueId is "PROP_RATING_VOLT":
            valueId = 40  # V
        elif valueId is "PROP_RATING_CURRENT":
            valueId = 41  # mV
        elif valueId is "PROP_RATING_FREQ_HIGH_TOP":
            valueId = 42  # mHz
        elif valueId is "PROP_RATING_FREQ_HIGH_MIDDLE":
            valueId = 43  # mHz
        elif valueId is "PROP_RATING_FREQ_LOW_MIDDLE":
            valueId = 44  # mHz
        elif valueId is "PROP_RATING_FREQ_LOW_BOTTOM":
            valueId = 45  # mHz
        elif valueId is "PROP_BATTERY_VOLT":
            valueId = 46  # mVDC
        elif valueId is "PROP_BATTERY_PACK_COUNT":
            valueId = 47  # number
        elif valueId is "PROP_BATTERY_PACK_CAPACITY":
            valueId = 48  # mAh
        elif valueId is "PROP_BATTERY_EXT_COUNT":
            valueId = 49  # number
        elif valueId is "PROP_RATING_RUNTIME":
            valueId = 50  # s
        elif valueId is "PROP_RATING_CHARGETIME":
            valueId = 51  # s

        elif valueId is "PROP_MODEL_NAME":
            valueId = 52  # string
        elif valueId is "PROP_HARDWARE_VERSION":
            valueId = 53  # string: major.minor.patch.build
        elif valueId is "PROP_SERIAL_NUMBER":
            valueId = 54  # string
        elif valueId is "PROP_COMPANY_NAME":
            valueId = 55  # string

        elif valueId is "PROP_LIST_OUTPUT_VOLT":
            valueId = 56  # array of V
        elif valueId is "PROP_LIST_TRANSFER_VOLT_HIGH":
            valueId = 57  # array of V
        elif valueId is "PROP_LIST_TRANSFER_VOLT_LOW":
            valueId = 58  # array of V
        elif valueId is "PROP_LIST_BATTERY_CRITICAL_THRESDHOLD":
            valueId = 59  # array of %
        elif valueId is "PROP_LIST_BAUDRATE":
            valueId = 60  # array of number

        elif valueId is "PROP_BOOST_SUPPORTED":
            valueId = 61  # 1/0
        elif valueId is "PROP_BUCK_SUPPORTED":
            valueId = 62  # 1/0
        elif valueId is "PROP_ONLINE_TYPE":
            valueId = 63  # 1/0

        elif valueId is "STATUS_FAULT_CODE":
            valueId = 64

        # configurable properties

        elif valueId is "PROP_BATTERY_TEST_PERIOD":
            valueId = 65  # s

        elif valueId is "PROP_OUTPUT_VOLT":
            valueId = 66  # V
        elif valueId is "PROP_OUTPUT_FREQ":
            valueId = 67  # Hz

        elif valueId is "PROP_TRANSFER_VOLT_HIGH":
            valueId = 68  # V
        elif valueId is "PROP_TRANSFER_VOLT_LOW":
            valueId = 69  # V

        elif valueId is "PROP_BATTERY_CRITICAL_THRESDHOLD":
            valueId = 70  # %
        elif valueId is "PROP_RESTORE_THRESHOLD":
            valueId = 71  # %
        elif valueId is "PROP_RESTORE_RUNTIME":
            valueId = 72  # s

        elif valueId is "PROP_FREQ_FOLLOWUP_TOLERANCE":
            valueId = 73  # %
        elif valueId is "PROP_OVERLOAD_THRESHOLD":
            valueId = 74  # %

        elif valueId is "PROP_SHUTDOWN_ALLOW":
            valueId = 75  # 1/0
        elif valueId is "PROP_BUZZER_ALLOW":
            valueId = 76  # 1/0
        elif valueId is "PROP_FORCE_REBOOT_ALLOW":
            valueId = 77  # 1/0
        elif valueId is "PROP_AUTORESTART_ALLOW":
            valueId = 79  # 1/0
        elif valueId is "PROP_FREQ_FOLLOWUP_ALLOW":
            valueId = 82  # 1/0

        elif valueId is "PROP_SHORTED_RESTORE_ALLOW":
            valueId = 83  # 1/0
        elif valueId is "PROP_COLDSTART_ALLOW":
            valueId = 78  # 1/0
        elif valueId is "PROP_OVERLOAD_BYPASS_ALLOW":
            valueId = 84  # 1/0
        elif valueId is "PROP_ENERGY_SAVING_ALLOW":
            valueId = 81
        elif valueId is "PROP_FORCE_BYPASS_ALLOW":
            valueId = 85  # 1/0
        elif valueId is "PROP_AVOID_DEEP_DISCHARGE_ALLOW":
            valueId = 80  # 1/0

        ########################
        # outlet

        elif valueId is "STATUS_OUTLET_SHUTDOWN_SCHEDULE_PENDING":
            valueId = 86  # 1/0
        elif valueId is "STATUS_OUTLET_RESTORE_SCHEDULE_PENDING":
            valueId = 87  # 1/0
        elif valueId is "STATUS_OUTLET_SHUTDOWN_DELAY_PENDING":
            valueId = 88  # 1/0
        elif valueId is "STATUS_OUTLET_RESTORE_DELAY_PENDING":
            valueId = 89  # 1/0
        elif valueId is "STATUS_OUTLET_STATE":
            valueId = 90  # 1: ON":valueId =   0: OFF

        elif valueId is "PROP_OUTLET_SWITCHABLE":
            valueId = 91  # 1/0

        elif valueId is "PROP_OUTLET_SHUTDOWN_DELAY":
            valueId = 92  # s
        elif valueId is "PROP_OUTLET_RESTORE_DELAY":
            valueId = 93  # s
        elif valueId is "PROP_OUTLET_SHUTDOWN_THRESHOLD":
            valueId = 94  # %

        ########################

        # to setup


        elif valueId is "SET_BAUDRATE":
            valueId = 95  # number
        elif valueId is "SET_ACCESS_PERMISSION":
            valueId = 96  # 0: none":valueId =   1: 1 read":valueId =   3: read & write
        elif valueId is "SET_BATTERY_TEST_PERIOD":
            valueId = 97  # s

        elif valueId is "SET_OUTPUT_VOLT":
            valueId = 98  # V
        elif valueId is "SET_OUTPUT_FREQ":
            valueId = 99  # Hz

        elif valueId is "SET_TRANSFER_VOLT_HIGH":
            valueId = 100  # V
        elif valueId is "SET_TRANSFER_VOLT_LOW":
            valueId = 101  # V

        elif valueId is "SET_BATTERY_CRITICAL_THRESDHOLD":
            valueId = 102  # %
        elif valueId is "SET_RESTORE_THRESHOLD":
            valueId = 103  # %
        elif valueId is "SET_RESTORE_RUNTIME":
            valueId = 104  # s

        elif valueId is "SET_FREQ_FOLLOWUP_TOLERANCE":
            valueId = 105  # %
        elif valueId is "SET_OVERLOAD_THRESHOLD":
            valueId = 106  # %

        elif valueId is "SET_COLDSTART_ALLOW":
            valueId = 107  # 1/0
        elif valueId is "SET_AUTORESTART_ALLOW":
            valueId = 108  # 1/0
        elif valueId is "SET_BUZZER_ALLOW":
            valueId = 109  # 1/0
        elif valueId is "SET_AVOID_DEEP_DISCHARGE_ALLOW":
            valueId = 110  # 1/0
        elif valueId is "SET_ENERGY_SAVING_ALLOW":
            valueId = 111  # 1/0
        elif valueId is "SET_SHUTDOWN_ALLOW":
            valueId = 112  # 1/0
        elif valueId is "SET_FREQ_FOLLOWUP_ALLOW":
            valueId = 113  # 1/0
        elif valueId is "SET_OVERLOAD_BYPASS_ALLOW":
            valueId = 114  # 1/0
        elif valueId is "SET_FORCE_BYPASS_ALLOW":
            valueId = 115  # 1/0
        elif valueId is "SET_FORCE_REBOOT_ALLOW":
            valueId = 116  # 1/0
        elif valueId is "SET_SHORTED_RESTORE_ALLOW":
            valueId = 117  # 1/0

        elif valueId is "SET_OUTLET_SHUTDOWN_DELAY":
            valueId = 118  # s
        elif valueId is "SET_OUTLET_RESTORE_DELAY":
            valueId = 119  # s
        elif valueId is "SET_OUTLET_SHUTDOWN_THRESHOLD":
            valueId = 120  # %

        ########################

        # ask a command

        elif valueId is "CMD_BUZZER_TEST":
            valueId = 121  # nothing
        elif valueId is "CMD_MUTE_TEMPORAL":
            valueId = 122

        elif valueId is "CMD_BATTERY_TEST":
            valueId = 123  # nothing
        elif valueId is "CMD_BATTERY_CALIBRATE":
            valueId = 124  # nothing
        elif valueId is "CMD_BATTERY_TEST_SUSTAIN":
            valueId = 125  # s
        elif valueId is "CMD_CANCEL_TEST":
            valueId = 126  # nothing
        elif valueId is "CMD_SLEEP":
            valueId = 127  # s
        elif valueId is "CMD_SHUTDOWN":
            valueId = 128  # s
        elif valueId is "CMD_RESTORE":
            valueId = 129  # s
        elif valueId is "CMD_SHUTDOWN_RESTORE":
            valueId = 130  # s
        elif valueId is "CMD_CANCEL_SCHEDULE":
            valueId = 131  # nothing

        elif valueId is "CMD_OUTLET_SHUTDOWN":
            valueId = 132  # s
        elif valueId is "CMD_OUTLET_RESTORE":
            valueId = 133  # s
        elif valueId is "CMD_OUTLET_CANCEL_SCHEDULE":
            valueId = 134  # nothing

        # other
        elif valueId is "SET_POLLING_RATE":
            valueId = 135
        elif valueId is "POLLING_RATE":
            valueId = 136

        # other
        # SET_POLLING_RATE = 135
        # POLLING_RATE = 136

        # Device (Proxy) Management

        # get =   query
        # PRESENT_DEVICE" =  # id number
        elif valueId is "LIST_DEVICES":
            valueId = 137  # array of id number
        elif valueId is "CHECK_DEVICE_VALID":
            valueId = 138  # 1/0
        elif valueId is "POLICY_TYPE":
            valueId = 139  # handle method (number)

        elif valueId is "PROP_DETECT_LOW_FREQ":
            valueId = 140  # mhz
        elif valueId is "PROP_DETECT_HIGH_FREQ":
            valueId = 141  # mhz
        elif valueId is "PROP_BYPASS_LOW_VOLT":
            valueId = 142  # mv
        elif valueId is "PROP_BYPASS_HIGH_VOLT":
            valueId = 143  # mv
        elif valueId is "PROP_BYPASS_AUDIBLE":
            valueId = 144  # 1/0
        elif valueId is "PROP_BATTERYMODE_AUTIBLE":
            valueId = 145  # 1/0
        elif valueId is "PROP_MANUAL_BYPASS_AUDIBLE":
            valueId = 146  # 1/0
        elif valueId is "PROP_MANUAL_BATTERYMODE_AUTIBLE":
            valueId = 147  # 1/0
        elif valueId is "PROP_BYPASS_WHEN_OFF":
            valueId = 148  # 1/0

        elif valueId is "SET_DETECT_LOW_FREQ":
            valueId = 149  # mhz
        elif valueId is "SET_DETECT_HIGH_FREQ":
            valueId = 150  # mhz
        elif valueId is "SET_BYPASS_LOW_VOLT":
            valueId = 151  # mv
        elif valueId is "SET_BYPASS_HIGH_VOLT":
            valueId = 152  # mv
        elif valueId is "SET_BYPASS_AUDIBLE":
            valueId = 153  # 1/0
        elif valueId is "SET_BATTERYMODE_AUTIBLE":
            valueId = 154  # 1/0
        elif valueId is "SET_MANUAL_BYPASS_AUDIBLE":
            valueId = 155  # 1/0
        elif valueId is "SET_MANUAL_BATTERYMODE_AUTIBLE":
            valueId = 156  # 1/0
        elif valueId is "SET_BYPASS_WHEN_OFF":
            valueId = 157  # 1/0

        elif valueId is "STATUS_OUTPUT_OFF":
            valueId = 158  # 1/0

        elif valueId is "PROP_BATTERY_OUTPUT_VOLT":
            valueId = 159  # V
        elif valueId is "SET_BATTERY_OUTPUT_VOLT":
            valueId = 160  # V
        elif valueId is "PROP_LIST_BATTERY_OUTPUT_VOLT":
            valueId = 161  # array of V

        elif valueId is "PROP_LIST_DETECT_LOW_FREQ":
            valueId = 162  # array of Hz
        elif valueId is "PROP_LIST_DETECT_HIGH_FREQ":
            valueId = 163  # array of Hz
        elif valueId is "PROP_LIST_BYPASS_LOW_VOLT":
            valueId = 164  # array of V
        elif valueId is "PROP_LIST_BYPASS_HIGH_VOLT":
            valueId = 165  # array of V

        elif valueId is "PROP_VALUE_ATTRIBUTE":
            valueId = 166

        elif valueId is "PROP_EXT_CABINET_COUNT":
            valueId = 167  # number
        elif valueId is "PROP_EXT_BATTERY_VOLT":
            valueId = 168  # mV
        elif valueId is "PROP_EXT_BATTERY_COUNT":
            valueId = 169  # number
        elif valueId is "PROP_EXT_BATTERY_AH":
            valueId = 170  # mAH

        elif valueId is "SET_EXT_CABINET_COUNT":
            valueId = 171  # number

        elif valueId is "PROP_OUTLET_CRITICAL_LOAD_":
            valueId = 172  # 1/0

        elif valueId is "STATUS_FULL_CHARGED":
            valueId = 173  # 1/0
        elif valueId is "PROP_UPS_TYPE":
            valueId = 174  # 0: off line, 1: line interactive, 2: sine wave line interactive, 3: on line, 4: Modular, 5: 3-phase, 6: PFC sine wave

        elif valueId is "PROP_VOLT_SENSITIVITY":
            valueId = 175  # 0: LOW, 1: MEDIUM, 2: HIGH
        elif valueId is "SET_VOLT_SENSITIVITY":
            valueId = 176  # 0: LOW, 1: MEDIUM, 2: HIGH

        elif valueId is "CMD_INDICATOR_TEST":
            valueId = 177

        elif valueId is "PROP_TURN_ON_DELAY":
            valueId = 178  # 0~600 s
        elif valueId is "SET_TURN_ON_DELAY":
            valueId = 179  # 0~600 s

        elif valueId is "CMD_RESTORE_IMMEDIATELY":
            valueId = 180

        elif valueId is "PROP_BATTERY_REPLACE_DATE":
            valueId = 181  # yymmdd
        elif valueId is "SET_BATTERY_REPLACE_DATE":
            valueId = 182  # yymmdd

        elif valueId is "STATUS_CONFIG_CHANGE_ID":
            valueId = 183  # number
        elif valueId is "PROP_CONFIG_CHANGE":
            valueId = 184  # array of property id

        elif valueId is "PROP_BUZZER_TEST_SUPPORTED":
            valueId = 185  # 1/0
        elif valueId is "PROP_INDICATOR_TEST_SUPPORTED":
            valueId = 186  # 1/0

        elif valueId is "PROP_RESTORE_IMMEDIATELY_SUPPORTED":
            valueId = 187  # 1/0

        elif valueId is "PROP_MAX_SHUTDOWN_DELAY":
            valueId = 188  # s
        elif valueId is "PROP_MAX_RESTORE_DELAY":
            valueId = 189  # s

        # STATUS_TEST_RESULT" = 190 include battery test & calibration test,
        # some ups support STATUS_TEST_RESULT only, and the other UPS support battery test result & calibration test result independently
        # (refer STATUS_BATTERY_TEST_RESULT = 314  STATUS_CALIBRATION_TEST_RESULT = 315)
        elif valueId is "STATUS_TEST_RESULT":
            valueId = 190  # 1: TEST_PASSED , 2: TEST_WARNING, 3: TEST_ERROR, 4: TEST_ABORTED, 5: TEST_PROGRESSING, 6: TEST_NOTHING

        elif valueId is "PROP_MAX_SLEEP_DELAY":
            valueId = 191  # s

        elif valueId is "STATUS_RUNTIME_LOW":
            valueId = 192  # 1/0
        elif valueId is "STATUS_BUZZER_MUTED":
            valueId = 193  # 1/0
        elif valueId is "STATUS_WIRING_FAULT":
            valueId = 194  # 1/0
        elif valueId is "STATUS_ECO_MODE":
            valueId = 195  # 1/0
        elif valueId is "STATUS_MANUAL_BYPASS":
            valueId = 196  # 1/0

        elif valueId is "PROP_HIGH_BYPASS_VOLT_WINDOW":
            valueId = 197  # V
        elif valueId is "PROP_LOW_BYPASS_VOLT_WINDOW":
            valueId = 198  # V
        elif valueId is "PROP_LIST_HIGH_BYPASS_VOLT_WINDOW":
            valueId = 199  # array of V
        elif valueId is "PROP_LIST_LOW_BYPASS_VOLT_WINDOW":
            valueId = 200  # array of V
        elif valueId is "PROP_ECO_MODE":
            valueId = 201  # 0/10/15
        elif valueId is "PROP_LIST_ECO_MODE":
            valueId = 202  # array of ECO mode
        elif valueId is "PROP_MANUAL_BYPASS_MODE":
            valueId = 203  # 1/0
        elif valueId is "PROP_WIRING_FAULT_DETECT":
            valueId = 204  # 1/0
        elif valueId is "PROP_DRY_RELAY_FUNCTION":
            valueId = 205  # 0/1/2/3/4
        elif valueId is "PROP_LIST_DRY_RELAY_FUNCTION":
            valueId = 206  # array of dry relay function
        elif valueId is "PROP_GENERATOR_MODE":
            valueId = 207  # 1/0
        elif valueId is "PROP_SCREEN_SAVER":
            valueId = 208  # 0s/30s/60s
        elif valueId is "PROP_LIST_SCREEN_SAVER":
            valueId = 209  # array of screen saver
        elif valueId is "PROP_QUALelifY_BYPASS":
            valueId = 210  # 0/1/2
        elif valueId is "PROP_LIST_QUALelifY_BYPASS":
            valueId = 211  # array of qualelify bypass
        elif valueId is "PROP_BATT_TO_LINE_DELAY":
            valueId = 212  # s
        elif valueId is "PROP_LIST_BATT_TO_LINE_DELAY":
            valueId = 213  # array of battery to line delay
        elif valueId is "PROP_LIST_OUTLET_INFORMATION":
            valueId = 214  # array of outlet information

        elif valueId is "SET_HIGH_LOW_BYPASS_VOLT_WINDOW":
            valueId = 215  # V
        elif valueId is "SET_ECO_MODE":
            valueId = 216  # 0/10/15
        elif valueId is "SET_MANUAL_BYPASS_MODE":
            valueId = 217  # 1/0
        elif valueId is "SET_WIRING_FAULT_DETECT":
            valueId = 218  # 1/0
        elif valueId is "SET_DRY_RELAY_FUNCTION":
            valueId = 219  # 0/1/2/3/4
        elif valueId is "SET_GENERATOR_MODE":
            valueId = 220  # 1/0
        elif valueId is "SET_SCREEN_SAVER":
            valueId = 221  # s
        elif valueId is "SET_QUALelifY_BYPASS":
            valueId = 222  # 0/1/2
        elif valueId is "SET_BATT_TO_LINE_DELAY":
            valueId = 223  # s

        elif valueId is "PROP_UPS_SYNC_CLOCK":
            valueId = 224
        elif valueId is "CMD_UPS_SYNC_CLOCK":
            valueId = 225

        elif valueId is "PROP_VOLTAGE_TRANSFER_MODE":
            valueId = 226  # 0/1, 0: utility voltage transfer, 1: output voltage transfer,

        elif valueId is "PROP_LCD_FIRMWARE_VERSION":
            valueId = 227
        elif valueId is "PROP_USB_FIRMWARE_VERSION":
            valueId = 228

        # three phase ups
        elif valueId is "PROP_THREE_PHASE_UPS":
            valueId = 229  # 1/0
        elif valueId is "STATUS_UTILITY_CURRENT":
            valueId = 230  # array of A(Amp.)
        elif valueId is "STATUS_UTILITY_POWER_FACTOR":
            valueId = 231  # array of %(0 ~ 1.00)
        elif valueId is "STATUS_BYPASS_VOLT":
            valueId = 232  # array of mV
        elif valueId is "STATUS_BYPASS_FREQ":
            valueId = 233  # array of mHz
        elif valueId is "STATUS_BYPASS_CURRENT":
            valueId = 234  # array of A(Amp.)
        elif valueId is "STATUS_BYPASS_POWER_FACTOR":
            valueId = 235  # array of %(0 ~ 1.00)
        elif valueId is "STATUS_OUTPUT_POWER_FACTOR":
            valueId = 236  # array of %(0 ~ 1.00)
        elif valueId is "STATUS_OUTPUT_ACTIVE_POWER":
            valueId = 237  # array of kW (three phase)
        elif valueId is "STATUS_OUTPUT_APPARENT_POWER":
            valueId = 238  # array of kVA (three phase)
        elif valueId is "STATUS_OUTPUT_REACTIVE_POWER":
            valueId = 239  # array of kVAR (three phase)
        elif valueId is "STATUS_BATTERY_CURRENT":
            valueId = 240  # array of A(Amp.)
        elif valueId is "STATUS_SYSTEM_MAINTENANCE_BREAK":
            valueId = 241  # 1/0
        elif valueId is "STATUS_BYPASS_FAULT":
            valueId = 242  # 1/0
        elif valueId is "STATUS_BYPASS_FAN_FAULT":
            valueId = 243  # 1/0
        elif valueId is "STATUS_BATTERY_TEMPERATURE":
            valueId = 245  # mC
        elif valueId is "STATUS_BATTERY_EXHAUSTED":
            valueId = 246  # 1/0
        elif valueId is "STATUS_BATTERY_CONNECTION_REVERSED":
            valueId = 247  # 1/0
        elif valueId is "STATUS_BATTERY_FLOAT_CHARGING":
            valueId = 248  # 1/0
        elif valueId is "STATUS_BATTERY_BOOST_CHARGING":
            valueId = 249  # 1/0
        elif valueId is "STATUS_UTILITY_NO_NEUTRAL":
            valueId = 250  # 1/0
        elif valueId is "STATUS_UTILITY_GENERATOR_DETECTED":
            valueId = 251  # 1/0
        elif valueId is "STATUS_BYPASS_FREQUENCY_FAILURE":
            valueId = 252  # 1/0
        elif valueId is "STATUS_MODULE_AMOUNT":
            valueId = 253
        elif valueId is "STATUS_MODULE_OFFLINE":
            valueId = 254  # array of 1/0 (total has 10 module for three phase)
        elif valueId is "STATUS_MODULE_RECTelifIER_FAULT":
            valueId = 255  # array of 1/0 (total has 10 module for three phase)
        elif valueId is "STATUS_MODULE_INVERTER_FAULT":
            valueId = 256  # array of 1/0 (total has 10 module for three phase)
        elif valueId is "STATUS_MODULE_INVERTER_PROTECTED":
            valueId = 257  # array of 1/0 (total has 10 module for three phase)
        elif valueId is "STATUS_MODULE_RECTelifIER_OVERHEAT":
            valueId = 258  # array of 1/0 (total has 10 module for three phase)
        elif valueId is "STATUS_MODULE_INVERTER_OVERHEAT":
            valueId = 259  # array of 1/0 (total has 10 module for three phase)
        elif valueId is "STATUS_MODULE_INVERTER_OVERLOAD":
            valueId = 260  # array of 1/0 (total has 10 module for three phase)
        elif valueId is "STATUS_MODULE_INVERTER_OVERLOAD_EXPIRED":
            valueId = 261  # array of 1/0 (total has 10 module for three phase)
        elif valueId is "STATUS_MODULE_FAN_FAULT":
            valueId = 262  # array of 1/0 (total has 10 module for three phase)

        elif valueId is "CMD_MANUAL_BOOT_CHARGE":
            valueId = 263  # 1/0 (Start/Stop)
        elif valueId is "CMD_MANUAL_FLOAT_CHARGE":
            valueId = 264  # 1/0 (Start/Stop)

        # probe three phase config
        elif valueId is "PROP_THREE_PHASE_FOLLOW_UP_SPEED":
            valueId = 265  # range (0.1 - 5.0Hz/s)*1000, the interval is 0.1
        elif valueId is "PROP_THREE_PHASE_FOLLOW_UP_TOLERANCE":
            valueId = 266  # range (0.1 - 5.0Hz/s)*1000, the interval is 0.1
        elif valueId is "PROP_RESTORE_MODE":
            valueId = 267  # 0/1/2 (Normal/Bypass/Standby)
        elif valueId is "PROP_BYPASS_FREQ_BOUNDARY":
            valueId = 268  # 1/2/0 ( 1Hz/3Hz/5Hz)
        elif valueId is "PROP_BATTERY_AH_AMOUNT":
            valueId = 269  # amount (1-30000)
        elif valueId is "PROP_FLOAT_CHARGE_CELL_VOLTAGE":
            valueId = 270  # range (2.20 ~ 2.35)*1000, the interval is 0.01
        elif valueId is "PROP_BOOST_CHARGE_CELL_VOLTAGE":
            valueId = 271  # range (2.25 ~ 2.45)*1000, the interval is 0.01
        elif valueId is "PROP_BOOST_CHARGE_TIME_LIMIT":
            valueId = 272  # range (1~48) hr
        elif valueId is "PROP_BOOST_CHARGE_PERIOD":
            valueId = 273  # 1 hr for 720 - 30,000
        elif valueId is "PROP_CHARGE_CURRENT_LIMIT":
            valueId = 274  # range (1~20)
        elif valueId is "PROP_COMPENSATE_CHARGING":
            valueId = 275  # mV/C, range (0~5, the interval is 0.01)
        elif valueId is "PROP_STOP_DIS_CELL_VOLTAGE_06C":
            valueId = 276  # float voltage * 1000 ( 1.6-1.85, the interval is 0.01)
        elif valueId is "PROP_STOP_DIS_CELL_VOLTAGE_015C":
            valueId = 277  # float voltage * 1000 (1.65-1.9, the interval is 0.01)
        elif valueId is "PROP_DISCHARGE_DURATION_LIMIT":
            valueId = 278  # s
        elif valueId is "PROP_DETECTING_PERIOD":
            valueId = 279  # s
        elif valueId is "PROP_DETECTING_DURATION":
            valueId = 280  # s
        elif valueId is "PROP_LCD_BACK_LIGHT_SAVING":
            valueId = 281  # s
        elif valueId is "PROP_REDUNDANT_QUANTITY":
            valueId = 282  # range (0~9)
        elif valueId is "PROP_CABINET_ID":
            valueId = 283  # range (1~255)
        elif valueId is "PROP_ECO_PARALLEL":
            valueId = 284  # ECO&Parallel, 1/2/4/6 (Single/Parallel/Single ECO/Parallel ECO)

        # set three phase config
        elif valueId is "SET_THREE_PHASE_FOLLOW_UP_SPEED":
            valueId = 285  # range (0.1 - 5.0Hz/s)*1000, the interval is 0.1
        elif valueId is "SET_THREE_PHASE_FOLLOW_UP_TOLERANCE":
            valueId = 286  # range (0.1 - 5.0Hz/s)*1000, the interval is 0.1
        elif valueId is "SET_RESTORE_MODE":
            valueId = 287  # 0/1/2 (Normal/Bypass/Standby)
        elif valueId is "SET_BYPASS_FREQ_BOUNDARY":
            valueId = 288  # 1/2/0 ( 1Hz/3Hz/5Hz)
        elif valueId is "SET_BATTERY_AH_AMOUNT":
            valueId = 289  # amount (1-30000)
        elif valueId is "SET_FLOAT_CHARGE_CELL_VOLTAGE":
            valueId = 290  # range (2.20 ~ 2.35)*1000, the interval is 0.01
        elif valueId is "SET_BOOST_CHARGE_CELL_VOLTAGE":
            valueId = 291  # range (2.25 ~ 2.45)*1000, the interval is 0.01
        elif valueId is "SET_BOOST_CHARGE_TIME_LIMIT":
            valueId = 292  # range (1~48) hr
        elif valueId is "SET_BOOST_CHARGE_PERIOD":
            valueId = 293  # 1 hr for 720 - 30,000
        elif valueId is "SET_CHARGE_CURRENT_LIMIT":
            valueId = 294  # range (1~20)
        elif valueId is "SET_COMPENSATE_CHARGING":
            valueId = 295  # mV/C, range (0~5, the interval is 0.01)
        elif valueId is "SET_STOP_DIS_CELL_VOLTAGE_06C":
            valueId = 296  # float voltage * 1000 ( 1.6-1.85, the interval is 0.01)
        elif valueId is "SET_STOP_DIS_CELL_VOLTAGE_015C":
            valueId = 297  # float voltage * 1000 (1.65-1.9, the interval is 0.01)
        elif valueId is "SET_DISCHARGE_DURATION_LIMIT":
            valueId = 298  # s
        elif valueId is "SET_DETECTING_PERIOD":
            valueId = 299  # s
        elif valueId is "SET_DETECTING_DURATION":
            valueId = 300  # s
        elif valueId is "SET_LCD_BACK_LIGHT_SAVING":
            valueId = 301  # s
        elif valueId is "SET_REDUNDANT_QUANTITY":
            valueId = 302  # range (0~9)
        elif valueId is "SET_CABINET_ID":
            valueId = 303  # range (1~255)
        elif valueId is "SET_ECO_PARALLEL":
            valueId = 304  # ECO&Parallel, 1/2/4/6 (Single/Parallel/Single ECO/Parallel ECO)
        elif valueId is "SET_BATTERY_PACK_COUNT":
            valueId = 305  # number

        elif valueId is "STATUS_OUTPUT_EMERGENCY_POWER_OFF":
            valueId = 306  # 1/0
        elif valueId is "STATUS_OUTPUT_REDUNDANCY_LOST":
            valueId = 307  # 1/0
        elif valueId is "STATUS_OUTPUT_INVERTER_POWER_INSUFFICIENT":
            valueId = 308  # 1/0
        elif valueId is "STATUS_UNABLE_RECOVER":
            valueId = 309  # 1/0

        elif valueId is "STATUS_BYPASS_OVERLOAD_TIMEOUT":
            valueId = 311
        elif valueId is "STATUS_BYPASS_SEQUENCE_FAULT":
            valueId = 312
        elif valueId is "STATUS_BYPASS_VOLT_FAILURE":
            valueId = 313

        elif valueId is "# battery test result & calibration test result, refer STATUS_TEST_RESULT":
            valueId = 190
        elif valueId is "STATUS_BATTERY_TEST_RESULT":
            valueId = 314  # 0: TEST_NOTHING, 1: TEST_PASSED, 2: TEST_WARNING/TEST_ERROR, 3: TEST_PROGRESSING
        elif valueId is "STATUS_CALIBRATION_TEST_RESULT":
            valueId = 315  # 0: TEST_NOTHING, 1: TEST_PASSED, 2: TEST_WARNING/TEST_ERROR, 3: TEST_PROGRESSING

        elif valueId is "STATUS_MODULE_SHUTDOWN":
            valueId = 316  # array of 1/0 (total has 10 module for three phase)

        elif valueId is "PROP_MODULE_APPARENT_POWER":
            valueId = 317  # VA

        elif valueId is "PROP_CONFIGURED_OUTPUT_VOLT":
            valueId = 318  # V
        elif valueId is "SET_CONFIGURED_OUTPUT_VOLT":
            valueId = 319  # V

        elif valueId is "PROP_BYPASS_FREQUENCY_TOLERANCE":
            valueId = 320  # %
        elif valueId is "SET_BYPASS_FREQUENCY_TOLERANCE":
            valueId = 321  # %
        elif valueId is "PROP_LIST_BYPASS_FREQUENCY_TOLERANCE":
            valueId = 322
        elif valueId is "PROP_BATTERY_LIFE_SPAN_MONTH":
            valueId = 323  # month

        elif valueId is "PROP_USE_CUSTOMIZE_BATTERY_PACKET":
            valueId = 324  # 1/0
        elif valueId is "SET_USE_CUSTOMIZE_BATTERY_PACKET":
            valueId = 325  # 1/0

        elif valueId is "PROP_UPS_PROTOCOL_TYPE":
            valueId = 326  # 0:other, 1: titan protocol, 2: v1 protocol, 3: v2e protocol, 4: hid protocol, 5: invt protocol

        elif valueId is "PROP_LIST_EXT_CABINET":
            valueId = 327  # array of count

        elif valueId is "UNEXPECTED_DISCONNECT":
            valueId = 328  # 1/0, unexpected disconnect condition:1.OL series connect via Usb sometimes will lost for a while, in fact, it doesn't lost connection

        elif valueId is "PROP_OUTLET_SHUTDOWN_DELAY_MAX":
            valueId = 329

        elif valueId is "PROP_OUTLET_RESTORE_DELAY_MAX":
            valueId = 330

        elif valueId is "PROP_CUMULATIVE_ENERGY_CONSUMPTION":
            valueId = 331  # unit 0.1 kwh

        elif valueId is "PROP_BATTERY_TEST_STARTUP":
            valueId = 332  # Startup Self Test 0: not support, 1: support and disabled, 2: support and enabled
        elif valueId is "SET_BATTERY_TEST_STARTUP":
            valueId = 333

        elif valueId is "STATUS_HARDWARE_FAULT_CODE":
            valueId = 334  # HEX String

        elif valueId is "PROP_DRY_RELAY_MAX ":
            valueId = 335  # HEX String

        elif valueId is "STATUS_OUTPUT_WATT":
            valueId = 376

        elif valueId is "PROP_LIST_BATTERY_RUNTIME_THRESHOLD":
            valueId = 379

        elif valueId is "SET_BATTERY_RUNTIME_THRESDHOLD":
            valueId = 380

        elif valueId is "PROP_BATTERY_RUNTIME_THRESDHOLD":
            valueId = 381

        # elif valueId is "STATUS_UPS_EVENT":
        #     valueId = 382

        # elif valueId is "STATUS_UPS_EVENT_CODE":
        #     valueId = 383

        elif valueId is "PROP_UPS_EVENT_CODE":
            valueId = 382

        return valueId