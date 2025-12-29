"""
Pi5 hardware profile: pin mappings and config loader.
Reads from config.yaml in repo root (if present) for overrides.
"""
from __future__ import annotations

import logging
import os
import yaml
from dataclasses import dataclass

logger = logging.getLogger(__name__)

DEFAULTS = {
    'i2c_bus': 1,
    'spi_bus': 0,
    'spi_device': 0,
    'uart_port': '/dev/serial0',
    'uart_baud': 9600,
    'buttons': {'up': 5, 'down': 6, 'select': 13, 'back': 19},
    'rotary': {'a': 20, 'b': 21},
    'pwm': {'fan': 18, 'backlight': 12}
}


@dataclass
class HardwareProfile:
    i2c_bus: int
    spi_bus: int
    spi_device: int
    uart_port: str
    uart_baud: int
    buttons: dict
    rotary: dict
    pwm: dict


def load_profile(config_path: str = None) -> HardwareProfile:
    if config_path is None:
        config_path = os.path.join(os.getcwd(), 'config.yaml')
    cfg = DEFAULTS.copy()
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as fh:
                data = yaml.safe_load(fh) or {}
            cfg.update(data.get('hardware', {}))
    except Exception as e:
        logger.debug('Failed reading config.yaml: %s', e)
    return HardwareProfile(
        i2c_bus=cfg['i2c_bus'],
        spi_bus=cfg['spi_bus'],
        spi_device=cfg['spi_device'],
        uart_port=cfg['uart_port'],
        uart_baud=cfg['uart_baud'],
        buttons=cfg['buttons'],
        rotary=cfg['rotary'],
        pwm=cfg['pwm'],
    )
