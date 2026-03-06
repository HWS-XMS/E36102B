import pyvisa
import sys

class E36102B(object):

	def __init__(self):
		resource_manager    = pyvisa.ResourceManager()
		instruments         = resource_manager.list_resources()
		resource_name 		= list(filter(lambda dev: dev.startswith('USB'), instruments))
		if len(resource_name) != 1:
			print('Bad instrument list', instruments)
			sys.exit(-1)
		else:
			print('Found USB Devices: {}'.format(resource_name))
			print('Picking the first one...')
		self._resource 				= resource_manager.open_resource(resource_name[0])

	def __write(self, message):
		self._resource.write(message)

	def __query(self, message):
		return self._resource.query(message)

	@property
	def voltage(self) -> float:
		return float(self.__query("SOURCE:VOLTAGE?"))

	@voltage.setter
	def voltage(self, voltage: float):
		assert (0.0 <= voltage <= 6.1)
		self.__write("SOURCE:VOLTAGE {:4.3f}".format(voltage))

	@property
	def voltage_protection(self) -> bool:
		return self.__query("SOURCE:VOLTAGE:PROTECTION:STATE?").replace('\n', '') == '1'

	@voltage_protection.setter
	def voltage_protection(self, on: bool):
		self.__write("SOURCE:VOLTAGE:PROTECTION:STATE {}".format("ON" if on else "OFF"))

	@property
	def voltage_protection_tripped(self) -> bool:
		return self.__query("SOURCE:VOLTAGE:PROTECTION:TRIPPED?").replace('\n', '') == '1'

	@property
	def current(self):
		return float(self.__query("SOURCE:CURRENT?"))

	@current.setter
	def current(self, current: float):
		assert (0.0 <= current <= 5.150)
		self.__write("SOURCE:CURRENT {:4.3f}".format(current))

	@property
	def current_protection(self) -> bool:
		return self.__query("SOURCE:CURRENT:PROTECTION:STATE?").replace('\n', '') == '1'

	@current_protection.setter
	def current_protection(self, on: bool):
		self.__write("SOURCE:CURRENT:PROTECTION:STATE {}".format("ON" if on else "OFF"))

	@property
	def current_protection_tripped(self) -> bool:
		return self.__query("SOURCE:CURRENT:PROTECTION:TRIPPED?").replace('\n', '') == '1'

	@property
	def output_state(self) -> bool:
		return self.__query("OUTPUT:STATE?").replace('\n', '') == '1'

	@output_state.setter
	def output_state(self, on: bool):
		return self.__write("OUTPUT:STATE {}".format("ON" if on else "OFF"))

	def clear_voltage_protection(self):
		self.__write("SOURCE:VOLTAGE:PROTECTION:CLEAR")

	def clear_current_protection(self):
		self.__write("SOURCE:CURRENT:PROTECTION:CLEAR")

	def clear_output_protection(self):
		self.__write("OUTPUT:PROTECTION:CLEAR")

import time
if __name__ == "__main__":
	dc_supply 						= E36102B()
	dc_supply.voltage 				= 5.0
	dc_supply.voltage_protection 	= False
	dc_supply.current 				= 1
	dc_supply.current_protection 	= True
	while True:
		dc_supply.output_state			= True
		time.sleep(1)
		dc_supply.output_state			= False
		time.sleep(0.5)
		if dc_supply.current_protection_tripped:
			print('Tripped, yoo!')
			dc_supply.clear_output_protection()
