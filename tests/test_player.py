#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2020-2024 Félix Chénier

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Tests for ktk.Player
"""

__author__ = "Félix Chénier"
__copyright__ = "Copyright (C) 2020-2024 Félix Chénier"
__email__ = "chenier.felix@uqam.ca"
__license__ = "Apache 2.0"

import kineticstoolkit as ktk
import matplotlib.pyplot as plt
import matplotlib as mpl
import warnings
import numpy as np
import os


def init() -> bool:
    """
    Initialize the graphic aggrator to Qt5Agg.

    This tries to ask Matplotlib to use Qt5Agg, which sets the interactive
    mode and therefore prevents a warning telling that Player must be used
    in interactive mode.

    If it fails, it's ok, unless we are running on macOS. For weird reasons,
    macOS headless mode on GitHub's continuous integration fails with bus
    errors or segmentation faults. Since KTK is primlarily developed on macOS,
    it does not bother me that the Player is not tested specifically on macOS
    during continuous integration, because it is tested locally. It is still
    tested on Linux and Windows.

    Returns
    -------
    bool
        True if the test must be run, False if it must not be run.

    """
    try:
        mpl.use("Qt5Agg")
    except ImportError:
        if ktk.config.is_mac:
            return False
    return True


def test_instanciate_and_to_html5():
    """Test that instanciating a Player does not crash."""
    if not init():
        return

    # Load markers
    kinematics = ktk.load(
        ktk.doc.download("inversedynamics_kinematics.ktk.zip")
    )

    kinematics = kinematics["Kinematics"]

    # The player can be instanciated to show markers
    pl = ktk.Player(kinematics["Markers"], target=[-5, 0, 0])
    plt.pause(0.2)
    pl.close()

    # The player can be instanciated to show rigid bodies
    pl = ktk.Player(kinematics["ReferenceFrames"], target=[-5, 0, 0])
    plt.pause(0.2)
    pl.close()

    # Or the player can be instanciated to show both markers and rigid bodies
    pl = ktk.Player(
        kinematics["Markers"],
        kinematics["ReferenceFrames"],
        target=[-5, 0, 0],
        up="z",
    )
    plt.pause(0.2)

    # Test that to_html5 doesn't crash
    assert pl.to_html5() is not None

    pl.close()


def test_issue137():
    """
    Player should not fail if some TimeSeries are not Nx4 or Nx4x4
    """
    if not init():
        return

    kinematics = ktk.load(
        ktk.doc.download("inversedynamics_kinematics.ktk.zip")
    )
    kinematics = kinematics["Kinematics"]["Markers"]
    kinematics.data["test"] = kinematics.time
    pl = ktk.Player(kinematics)  # Shouldn't crash
    plt.pause(0.2)
    pl.close()


def test_scripting():
    """Test that every property assignation works or crashes as expected."""
    # %%
    # Download and read markers from a sample C3D file
    if not init():
        return

    filename = ktk.doc.download("kinematics_tennis_serve.c3d")
    markers = ktk.read_c3d(filename)["Points"]

    # # Create another person
    # markers2 = markers.copy()
    # keys = list(markers2.data.keys())
    # for key in keys:
    #     markers2.data[key] += [[1.0, 0.0, 0.0, 0.0]]
    #     markers2.rename_data(key, key.replace("Derrick", "Viktor"), in_place=True)

    interconnections = dict()  # Will contain all segment definitions

    interconnections["LLowerLimb"] = {
        "Color": [0, 0.5, 1],  # In RGB format (here, greenish blue)
        "Links": [  # List of lines that span lists of markers
            ["*LTOE", "*LHEE", "*LANK", "*LTOE"],
            ["*LANK", "*LKNE", "*LASI"],
            ["*LKNE", "*LPSI"],
        ],
    }

    interconnections["RLowerLimb"] = {
        "Color": [0, 0.5, 1],
        "Links": [
            ["*RTOE", "*RHEE", "*RANK", "*RTOE"],
            ["*RANK", "*RKNE", "*RASI"],
            ["*RKNE", "*RPSI"],
        ],
    }

    interconnections["LUpperLimb"] = {
        "Color": [0, 0.5, 1],
        "Links": [
            ["*LSHO", "*LELB", "*LWRA", "*LFIN"],
            ["*LELB", "*LWRB", "*LFIN"],
            ["*LWRA", "*LWRB"],
        ],
    }

    interconnections["RUpperLimb"] = {
        "Color": [1, 0.5, 0],
        "Links": [
            ["*RSHO", "*RELB", "*RWRA", "*RFIN"],
            ["*RELB", "*RWRB", "*RFIN"],
            ["*RWRA", "*RWRB"],
        ],
    }

    interconnections["Head"] = {
        "Color": [1, 0.5, 1],
        "Links": [
            ["*C7", "*LFHD", "*RFHD", "*C7"],
            ["*C7", "*LBHD", "*RBHD", "*C7"],
            ["*LBHD", "*LFHD"],
            ["*RBHD", "*RFHD"],
        ],
    }

    interconnections["TrunkPelvis"] = {
        "Color": [0.5, 1, 0.5],
        "Links": [
            ["*LASI", "*STRN", "*RASI"],
            ["*STRN", "*CLAV"],
            ["*LPSI", "*T10", "*RPSI"],
            ["*T10", "*C7"],
            ["*LASI", "*LSHO", "*LPSI"],
            ["*RASI", "*RSHO", "*RPSI"],
            [
                "*LPSI",
                "*LASI",
                "*RASI",
                "*RPSI",
                "*LPSI",
            ],
            [
                "*LSHO",
                "*CLAV",
                "*RSHO",
                "*C7",
                "*LSHO",
            ],
        ],
    }

    # In this file, the up axis is z:
    p = ktk.Player(
        markers, up="z", anterior="-y", interconnections=interconnections
    )

    # %% Front view
    p.azimuth = 0.0
    p.elevation = 0.0
    p.target = (0.0, 0.0, 0.0)
    p.perspective = False

    # %% Right view
    p.azimuth = np.pi / 2

    # %% Top view
    p.azimuth = 0.0
    p.elevation = np.pi / 2

    # or

    p.set_view("top")

    # %% Standard view
    p.elevation = 0.1
    p.azimuth = np.pi / 4
    p.perspective = True

    # %% Styling points and interconnections
    p.point_size = 8.0
    p.interconnection_width = 5.0

    # %% Styling frames
    p.frame_size = 1.0
    p.frame_width = 3.0

    # %% Sizing grid
    p.grid_size = 8.0
    p.grid_origin = (0, -1.0, 0.0)

    # %% Styling grid and background
    p.grid_color = (1.0, 0.5, 1.0)
    p.background_color = (1.0, 1.0, 1.0)

    # %% Styling grid and background
    p.grid_color = (0.0, 0.5, 0.5)
    p.background_color = (0.0, 0.0, 0.2)

    # %% Remove data
    ts = p.get_contents()
    p.set_contents(ktk.TimeSeries())

    # %% Put back data
    p.set_contents(ts)

    # %% Remove interconnections
    inter = p.get_interconnections()
    p.set_interconnections({})

    # %% Put back interconnections
    p.set_interconnections(inter)

    # %% Keep only seconds 4 to 5
    p.set_contents(markers.get_ts_between_times(4.0, 5.0))

    # %% Play and pause
    p.play()
    plt.pause(0.5)
    p.pause()

    # %% Close
    p.close()

    # %%


def test_set_current_time():
    """Test that setting the current time on construction works."""
    if not init():
        return

    filename = ktk.doc.download("kinematics_tennis_serve.c3d")
    markers = ktk.read_c3d(filename)["Points"]
    p = ktk.Player(markers, current_time=2.5)


def test_to_png_mp4():
    """Test that to_png and to_mp4 work."""
    if not init():
        return

    filename = ktk.doc.download("kinematics_tennis_serve.c3d")
    markers = ktk.read_c3d(filename)["Points"]
    p = ktk.Player(markers.get_ts_between_times(0, 0.1))
    p.to_mp4("test.mp4")
    p.to_png("test.png")
    assert os.path.exists("test.mp4")
    assert os.path.exists("test.png")
    os.remove("test.mp4")
    os.remove("test.png")


def test_old_parameter_names():
    """Test the old parameter names."""
    if not init():
        return

    filename = ktk.doc.download("kinematics_tennis_serve.c3d")
    markers = ktk.read_c3d(filename)["Points"]

    p = ktk.Player(
        markers,
        segments={
            "Head": {
                "Color": [1, 0.5, 1],
                "Links": [
                    ["*C7", "*LFHD", "*RFHD", "*C7"],
                    ["*C7", "*LBHD", "*RBHD", "*C7"],
                    ["*LBHD", "*LFHD"],
                    ["*RBHD", "*RFHD"],
                ],
            }
        },
        segment_width=0,
        current_frame=10,
    )
    plt.pause(0.2)
    p.close()


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
