#!/usr/bin/env python3

import aws_cdk as cdk

from telegrambot_billing.telegrambot_billing_stack import TelegrambotBillingStack


app = cdk.App()
TelegrambotBillingStack(app, "TelegrambotBillingStack")

app.synth()
