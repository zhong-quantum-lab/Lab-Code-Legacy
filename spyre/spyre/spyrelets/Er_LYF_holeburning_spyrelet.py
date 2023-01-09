import wave
import numpy as np
import pyqtgraph as pg
import time
import csv
import os
from lantz import Q_

import matplotlib.pyplot as plt
import datetime
from scipy.constants import c

from PyQt5.Qsci import QsciScintilla, QsciLexerPython
from PyQt5.QtWidgets import QPushButton, QTextEdit, QVBoxLayout

from spyre import Spyrelet, Task, Element
from spyre.widgets.task import TaskWidget
from spyre.plotting import LinePlotWidget
from spyre.widgets.rangespace import Rangespace
from spyre.widgets.param_widget import ParamWidget
from spyre.widgets.repository_widget import RepositoryWidget

###Import lantz drivers files for all instruments you use.
# e.g.
# from lantz.drivers.keysight import Keysight_33622A
# The above line will import the AWG driver
from toptica.lasersdk.client import NetworkConnection, Client, SerialConnection
from lantz.drivers.bristol import Bristol_771  # Wavelength meter
from lantz.drivers.spectrum import MS2721B  # Anritsu spectrum analyzer
from lantz.log import log_to_screen, DEBUG

nm = Q_(1, 'nm')
s = Q_(1, 's')

volt = Q_(1, 'V')
milivolt = Q_(1, 'mV')
Hz = Q_(1, 'Hz')
kHz = Q_(1, 'kHz')
MHz = Q_(1.0, 'MHz')
dB = Q_(1, 'dB')


# Sweep EOM modulation signal
class HoleBurn(Spyrelet):
    requires = {
        'wm': Bristol_771,
        'analyzer': MS2721B
    }

    qutag = None
    laser = NetworkConnection('1.1.1.2')

    def homelaser(self, start, precision, drift_time):
        current = self.wm.measure_wavelength()
        with Client(self.laser) as client:
            while current < start - precision or current > start + precision:
                setting = client.get('laser1:ctl:wavelength-set', float)
                offset = current - start
                client.set('laser1:ctl:wavelength-set', setting - offset)
                time.sleep(drift_time.magnitude)
                current = self.wm.measure_wavelength()
                print(current, start, setting - offset)

    ###Tasks##############################################################
    @Task()
    def testlaser(self):
        log_to_screen(DEBUG)
        testparams = self.Laser_Frequency_Settings.widget.get()
        with Client(self.laser) as client:
            setting = client.get('laser1:ctl:wavelength-set', float)
            # print('Setting is {}.'.format(setting))
            target_wl = testparams['carrier wavelength (nm)']
            client.set('laser1:ctl:wavelength-set', target_wl)
            print('Set wavelength to {}'.format(target_wl))
            # setting = client.get('laser1:ctl:wavelength-set', float)
            # print('Setting is now {}.'.format(setting))
            time.sleep(3)
            wl = self.wm.measure_wavelength()
            print('Actual wavelength is {}'.format(wl))

            # target_current = testparams['current']
            # client.set('laser1:dl:cc:current-set', target_current)
            # current = client.get('laser1:dl:cc:current-set', float)
            # print('current is set to ' + str(current))

        return

    @testlaser.initializer
    def initialize(self):
        self.wm.start_data()
        return

    @testlaser.finalizer
    def finalize(self):
        self.wm.stop_data()
        print('Lifetime measurements complete.')
        return

    @Task()
    def hole_burning(self):
        self.dataset.clear()
        log_to_screen(DEBUG)

        print('here 1')
        laser_freq_params = self.Laser_Frequency_Settings.widget.get()
        exp_params = self.Experiment_Settings.widget.get()
        pump_params = self.Pump_Settings.widget.get()
        probe_params = self.Probe_Settings.widget.get()

        carrier_wl = laser_freq_params['carrier wavelength (nm)']
        carrier_precision = laser_freq_params['precision(nm): ±']
        drift_time = laser_freq_params['drift_time']
        current = laser_freq_params['current']

        file_name = exp_params['File Name']
        num_scan = exp_params['Num Scan']

        pump_freq = pump_params['frequency']
        pump_duration = pump_params['duration']
        pump_power = pump_params['power']
        pump_TG_power = pump_params['TG power']

        probe_delay = probe_params['wait']
        probe_fr_low = probe_params['start frequency']
        probe_fr_high = probe_params['stop frequency']
        probe_power = probe_params['power']
        probe_duration = probe_params['duration']
        probe_power = pump_params['power']
        probe_TG_power = pump_params['TG power']

        print("here 2")

        probe_span = probe_fr_high - probe_fr_low
        curr = datetime.datetime.now()

        for i in range(num_scan):
            print('This is scan repeat {}'.format(i))

            with Client(self.laser) as client:
                # setting = client.get('laser1:ctl:wavelength-set', float)
                client.set('laser1:ctl:wavelength-set', carrier_wl)
                # Correct for laser drift  \pm 0.00001 nm ~ \pm 1MHz
                print('correcting for laser drift')
                self.homelaser(carrier_wl, carrier_precision, drift_time)
                print('actual carrier wavelength: ' + str(self.wm.measure_wavelength()))
                carrier_wl = self.wm.measure_wavelength()
                sideband_wl_start = c / (c / (carrier_wl * 1e-9) + probe_fr_low.magnitude) * 1e9
                sideband_wl_stop = c / (c / (carrier_wl * 1e-9) + probe_fr_high.magnitude) * 1e9
                print('upper sideband wavelength: from ' + str(sideband_wl_start) + ' to ' + str(sideband_wl_stop))

            # pump
            self.analyzer.freq_cent = pump_freq
            self.analyzer.freq_span = 0 * Hz
            self.analyzer.generator_power = pump_TG_power
            self.analyzer.generator = 'ON'
            time.sleep(pump_duration.magnitude)

            if probe_delay.magnitude > 0:
                # delay
                self.analyzer.generator = 'OFF'
                time.sleep(probe_delay.magnitude)
                self.analyzer.generator_power = probe_TG_power
                self.analyzer.generator = 'ON'

            # probe
            self.analyzer.generator_power = probe_TG_power
            self.analyzer.freq_star = probe_fr_low
            self.analyzer.freq_span = probe_span
            self.analyzer.savefile(file_name + curr.strftime("%Y-%m-%d_%H-%M-%S") + "_" + str(i))

            print('here 4!')

            self.analyzer.generator = 'OFF'
            print('Scan repeat ' + str(i) + " is done.")
            time.sleep(30)

        return

    @hole_burning.initializer
    def initialize(self):
        self.wm.start_data()
        return

    @hole_burning.finalizer
    def finalize(self):
        self.wm.stop_data()
        print('Data Collection complete.')
        return

    ###Elements###########################################################
    @Element()
    def Laser_Frequency_Settings(self):
        laser_freq_params = [
            ('carrier wavelength (nm)', {'type': float, 'default': 1530}),
            ('precision(nm): ±', {'type': float, 'default': 0.001}),
            ('drift_time', {'type': float, 'default': 5, 'units': 's'}),
            # ('current', {'type': float, 'default': 0, 'units': 'mA'})
        ]
        w = ParamWidget(laser_freq_params)
        return w

    @Element()
    def Experiment_Settings(self):
        exp_params = [
            ('Num Scan', {'type': int, 'default': 3}),
            ('File Name', {'type': str, 'default': 'Er_LYF_Hole_Burn'}),
        ]
        w = ParamWidget(exp_params)
        return w

    @Element()
    def Pump_Settings(self):
        pump_params = [
            ('frequency', {'type': float, 'default': 20, 'units': 'Hz'}),
            ('duration', {'type': float, 'default': 1, 'units': 's'}),
            ('power', {'type': float, 'default': 0}),
            ('TG_power', {'type': float, 'default': 0}),
        ]
        w = ParamWidget(pump_params)
        return w

    @Element()
    def Probe_Settings(self):
        probe_params = [
            ('wait', {'type': float, 'default': 0, 'units': 's'}),
            ('start frequency', {'type': float, 'default': 9000, 'units': 'Hz'}),
            ('stop frequency', {'type': float, 'default': 9010, 'units': 'Hz'}),
            ('duration', {'type': float, 'default': 1, 'units': 's'}),
            ('power', {'type': float, 'default': 0}),
            ('TG_power', {'type': float, 'default': 0}),
        ]
        w = ParamWidget(probe_params)
        return w