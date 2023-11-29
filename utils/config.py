#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    config
"""
import yaml
from dataclasses import dataclass
import inspect


@dataclass
class AppConfig:
    ROBOT_NAME: str
    APP_ID: str
    APP_SECRET: str
    ENCRYPT_KEY: str
    VERIFICATION_TOKEN: str
    CHAT_KEY: str

    @classmethod
    def from_dict(cls, env):
        return cls(**{
            k: v for k, v in env.items() if k in inspect.signature(cls).parameters
        })

    def validate(self):
        if not self.ROBOT_NAME:
            raise Exception('ROBOT_NAME is required')
        if not self.APP_ID:
            raise Exception('APP_ID is required')
        if not self.APP_SECRET:
            raise Exception('APP_SECRET is required')
        if not self.ENCRYPT_KEY:
            raise Exception('ENCRYPT_KEY is required')
        if not self.VERIFICATION_TOKEN:
            raise Exception('VERIFICATION_TOKEN is required')


def load_config():
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        app_config_ = AppConfig.from_dict(config)
        app_config_.validate()
        return app_config_


def app_config():
    return load_config()
