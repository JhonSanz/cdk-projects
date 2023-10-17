#!/usr/bin/env python3

import aws_cdk as cdk

from positions_trading_website.positions_trading_website_stack import PositionsTradingWebsiteStack


app = cdk.App()
PositionsTradingWebsiteStack(app, "PositionsTradingWebsiteStack")

app.synth()
