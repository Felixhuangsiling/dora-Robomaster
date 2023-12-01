#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Callable, Optional, Union

from enum import Enum
import numpy as np
import pyarrow as pa
import torch
from utils import LABELS
from dora import DoraStatus

pa.array([])

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480


class Operator:
    """
    Infering object from images
    """

    def on_event(
        self,
        dora_event: dict,
        send_output: Callable[[str, Union[bytes, pa.Array], Optional[dict]], None],
    ) -> DoraStatus:
        if dora_event["type"] == "INPUT":
            return self.on_input(dora_event, send_output)
        return DoraStatus.CONTINUE

    def on_input(
        self,
        dora_input: dict,
        send_output: Callable[[str, Union[bytes, pa.array], Optional[dict]], None],
    ) -> DoraStatus:
        x, y, z, acc, action = 0, 0, 0, 0, 0
        bboxs = dora_input["value"].to_numpy()
        bboxs = np.reshape(bboxs, (-1, 6))
        arrays = pa.array([0, 0, 0, 0, 0])
        obstacle = False
        box = False
        for bbox in bboxs:
            box = True
            [
                min_x,
                min_y,
                max_x,
                max_y,
                confidence,
                label,
            ] = bbox
            if (
                min_x > 276
                and min_x < 288
                and max_x > 361
                and max_x < 370
                and min_y > 422
                and min_y < 430
                and max_y > 479
            ):
                continue
            if LABELS[int(label)] == "ABC":
                continue
            
            if LABELS[int(label)] == "bottle":
                    action = 1
            
            if max_y > 370 and (min_x + max_x) / 2 > 240 and (min_x + max_x) / 2 < 400:
                if (min_x + max_x) / 2 > 320:
                    y = -0.15
                    acc = 0.4
                elif (min_x + max_x) / 2 <= 320:
                    y = 0.15
                    acc = 0.4

                if LABELS[int(label)] == "bottle":
                    action = 1
                obstacle = True
                break
        if obstacle == False and box == True:
            x = 0.2
            acc = 0.8

        arrays = pa.array([x, y, z, acc, action])

        if box == True:
            send_output("control", arrays, dora_input["metadata"])

        return DoraStatus.CONTINUE
