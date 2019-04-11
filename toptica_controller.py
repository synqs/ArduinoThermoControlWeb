import sys

import matplotlib.pyplot as pyplot

from toptica.lasersdk.dlcpro.v2_0_3 import DLCpro, NetworkConnection, DeviceNotFoundError
from toptica.lasersdk.utils.dlcpro import *


def main():
    try:
        with DLCpro(NetworkConnection(sys.argv[1])) as dlcpro:
            # Retrieve scan, lock raw data from device
            scope_data = extract_float_arrays('xyY', dlcpro.laser1.scope.data.get())
            raw_lock_candidates = dlcpro.laser1.dl.lock.candidates.get()
            lock_candidates = extract_lock_points('clt', raw_lock_candidates)
            lock_state = extract_lock_state(raw_lock_candidates)

            # Create double y axis plot
            fig, laxis = pyplot.subplots()
            fig.suptitle('DLC pro Scope Output')

            ch1_available = dlcpro.laser1.scope.channel1.signal.get() != -3  # Signal is 'none'
            ch2_available = dlcpro.laser1.scope.channel2.signal.get() != -3

            # Set label and unit of X axis
            laxis.set_xlabel("{} [{}]".format(
                dlcpro.laser1.scope.channelx.name.get(),
                dlcpro.laser1.scope.channelx.unit.get()))

            if ch1_available:
                red = laxis

                # Set label and unit of left Y axis
                red.set_ylabel("{} [{}]".format(
                    dlcpro.laser1.scope.channel1.name.get(),
                    dlcpro.laser1.scope.channel1.unit.get()),
                    color='red')

                # Plot first scope channel data
                red.plot(
                    scope_data['x'],
                    scope_data['y'],
                    linestyle='solid',
                    color='red',
                    zorder=1)

                # Plot lock candidate points if available
                if 'c' in lock_candidates.keys():
                    red.plot(
                        lock_candidates['c']['x'],
                        lock_candidates['c']['y'],
                        linestyle='None',
                        marker='o',
                        markersize=12.0,
                        color='grey',
                        zorder=2)

                # Plot selected lock candidate point if available
                if 'l' in lock_candidates.keys() and lock_state == 3:  # State is 'Selected'
                    red.plot(
                        lock_candidates['l']['x'],
                        lock_candidates['l']['y'],
                        linestyle='None',
                        marker='o',
                        markersize=16.0,
                        color='red',
                        markerfacecolor='none',
                        zorder=3)

                # Retrieve and plot background trace data if lock is closed
                if lock_state == 5:  # State is 'Locked'
                    background_trace = extract_float_arrays('xy', dlcpro.laser1.dl.lock.background_trace.get())

                    red.plot(
                        background_trace['x'],
                        background_trace['y'],
                        linestyle='solid',
                        color='lightgrey',
                        zorder=1)

                # Plot lock tracking position if available
                if 't' in lock_candidates.keys():
                    red.plot(
                        lock_candidates['t']['x'],
                        lock_candidates['t']['y'],
                        linestyle='None',
                        marker='o',
                        markersize=20.0,
                        color='red',
                        markerfacecolor='none',
                        zorder=3)

            # Plot second scope channel data if available
            if ch2_available:
                if ch1_available:
                    blue = laxis.twinx()
                else:
                    blue = laxis

                blue.set_ylabel("{} [{}]".format(
                    dlcpro.laser1.scope.channel2.name.get(),
                    dlcpro.laser1.scope.channel2.unit.get()),
                    color='blue')

                blue.plot(
                    scope_data['x'],
                    scope_data['Y'],
                    linestyle='solid',
                    color='blue',
                    zorder=0)

                laxis.set_zorder(blue.get_zorder() + 1)
                laxis.patch.set_visible(False)

            pyplot.margins(x=0.0)
            pyplot.show()

    except DeviceNotFoundError:
        sys.stderr.write('Device not found')


if __name__ == "__main__":
    main()
